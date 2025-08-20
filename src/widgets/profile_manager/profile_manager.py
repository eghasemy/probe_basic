"""
Profile Manager Widget
Phase 9 - Settings, Profiles & Network

Manages LinuxCNC machine profiles including creation, cloning, deletion, and switching.
Each profile bundle contains: INI + HAL + YAML + pinmap configuration files.
"""

import os
import shutil
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                                QListWidgetItem, QPushButton, QLabel, QLineEdit,
                                QMessageBox, QDialog, QDialogButtonBox, QTextEdit,
                                QComboBox, QGroupBox, QCheckBox, QProgressBar,
                                QInputDialog)
    from PyQt5.QtCore import pyqtSignal, QTimer
    from PyQt5.QtGui import QIcon
except ImportError:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                            QListWidgetItem, QPushButton, QLabel, QLineEdit,
                            QMessageBox, QDialog, QDialogButtonBox, QTextEdit,
                            QComboBox, QGroupBox, QCheckBox, QIcon, QInputDialog)
    from PyQt4.QtCore import pyqtSignal, QTimer
    
    # Create QProgressBar stub for PyQt4 compatibility
    class QProgressBar(QWidget):
        def __init__(self, parent=None):
            super(QProgressBar, self).__init__(parent)
        def setValue(self, value): pass
        def setMaximum(self, value): pass


class ProfileCreateDialog(QDialog):
    """Dialog for creating new profiles"""
    
    def __init__(self, parent=None, existing_profiles=None):
        super(ProfileCreateDialog, self).__init__(parent)
        self.existing_profiles = existing_profiles or []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Create New Profile")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Profile name
        name_group = QGroupBox("Profile Information")
        name_layout = QVBoxLayout()
        
        name_layout.addWidget(QLabel("Profile Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter unique profile name")
        self.name_edit.textChanged.connect(self.validate_input)
        name_layout.addWidget(self.name_edit)
        
        name_layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description")
        self.description_edit.setMaximumHeight(80)
        name_layout.addWidget(self.description_edit)
        
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Template selection
        template_group = QGroupBox("Template")
        template_layout = QVBoxLayout()
        
        template_layout.addWidget(QLabel("Base Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Basic Sim (3-axis mill)",
            "ATC Sim (Tool changer)",
            "Lathe Sim", 
            "Custom (empty profile)"
        ])
        template_layout.addWidget(self.template_combo)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.set_default_check = QCheckBox("Set as default profile")
        options_layout.addWidget(self.set_default_check)
        
        self.open_after_create = QCheckBox("Switch to profile after creation")
        self.open_after_create.setChecked(True)
        options_layout.addWidget(self.open_after_create)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Validation label
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red")
        layout.addWidget(self.validation_label)
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)
        self.validate_input()
        
    def validate_input(self):
        """Validate user input"""
        name = self.name_edit.text().strip()
        
        if not name:
            self.validation_label.setText("Profile name is required")
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
            return False
            
        if name in self.existing_profiles:
            self.validation_label.setText("Profile name already exists")
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
            return False
            
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in name for char in invalid_chars):
            self.validation_label.setText("Profile name contains invalid characters")
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
            return False
            
        self.validation_label.setText("")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)
        return True
        
    def get_profile_data(self):
        """Get profile creation data"""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'template': self.template_combo.currentText(),
            'set_default': self.set_default_check.isChecked(),
            'switch_after_create': self.open_after_create.isChecked()
        }


class ProfileManager(QWidget):
    """
    Profile Manager Widget
    
    Manages LinuxCNC machine profiles with create, clone, delete, and switch operations.
    Each profile is a bundle containing: INI + HAL + YAML + pinmap files.
    """
    
    # Signals
    profile_switched = pyqtSignal(str)  # profile_name
    profile_created = pyqtSignal(str)   # profile_name
    profile_deleted = pyqtSignal(str)   # profile_name
    restart_requested = pyqtSignal(str) # profile_name
    
    # Profile bundle file extensions
    PROFILE_EXTENSIONS = ['.ini', '.hal', '.yml', '.yaml', '.py', '.ngc', '.var']
    
    def __init__(self, parent=None):
        super(ProfileManager, self).__init__(parent)
        
        # Profile directories
        self.profiles_dir = Path.home() / ".pb-touch" / "profiles"
        self.templates_dir = Path(__file__).parent.parent.parent.parent / "configs"
        self.current_profile = None
        
        # Ensure directories exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self.init_ui()
        self.load_profiles()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Profile Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Current profile indicator
        self.current_label = QLabel("Current: None")
        self.current_label.setStyleSheet("padding: 8px; background: #e8f4f8; border-radius: 4px;")
        header_layout.addWidget(self.current_label)
        
        layout.addLayout(header_layout)
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.itemDoubleClicked.connect(self.switch_profile)
        self.profile_list.currentItemChanged.connect(self.update_buttons)
        layout.addWidget(self.profile_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(self.create_btn)
        
        self.clone_btn = QPushButton("Clone")
        self.clone_btn.clicked.connect(self.clone_profile)
        self.clone_btn.setEnabled(False)
        button_layout.addWidget(self.clone_btn)
        
        self.switch_btn = QPushButton("Switch")
        self.switch_btn.clicked.connect(self.switch_profile)
        self.switch_btn.setEnabled(False)
        button_layout.addWidget(self.switch_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_profile)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_profiles)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 4px; color: #666;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def load_profiles(self):
        """Load available profiles"""
        self.profile_list.clear()
        
        try:
            # Load profiles from profiles directory
            if self.profiles_dir.exists():
                for profile_dir in self.profiles_dir.iterdir():
                    if profile_dir.is_dir():
                        self.add_profile_item(profile_dir.name, profile_dir)
                        
            # Load current profile info
            self.load_current_profile()
            
            self.status_label.setText(f"Loaded {self.profile_list.count()} profiles")
            
        except Exception as e:
            self.status_label.setText(f"Error loading profiles: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load profiles:\n{e}")
            
    def add_profile_item(self, name: str, path: Path):
        """Add profile item to list"""
        item = QListWidgetItem(name)
        
        # Load profile metadata if available
        metadata_file = path / "profile.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    description = metadata.get('description', '')
                    if description:
                        item.setToolTip(f"{name}\n{description}")
                    else:
                        item.setToolTip(name)
            except:
                item.setToolTip(name)
        else:
            item.setToolTip(name)
            
        item.setData(1, str(path))  # Store path in item data
        self.profile_list.addItem(item)
        
    def load_current_profile(self):
        """Load current profile information"""
        try:
            # Check environment variable first
            current_ini = os.environ.get('INI_FILE_NAME')
            if current_ini:
                profile_path = Path(current_ini).parent
                profile_name = profile_path.name
                self.current_profile = profile_name
                self.current_label.setText(f"Current: {profile_name}")
                
                # Highlight current profile in list
                for i in range(self.profile_list.count()):
                    item = self.profile_list.item(i)
                    if item.text() == profile_name:
                        item.setSelected(True)
                        break
            else:
                self.current_label.setText("Current: None")
                
        except Exception as e:
            self.current_label.setText("Current: Unknown")
            
    def update_buttons(self):
        """Update button states based on selection"""
        has_selection = self.profile_list.currentItem() is not None
        selected_name = self.profile_list.currentItem().text() if has_selection else None
        is_current = selected_name == self.current_profile
        
        self.clone_btn.setEnabled(has_selection)
        self.switch_btn.setEnabled(has_selection and not is_current)
        self.delete_btn.setEnabled(has_selection and not is_current)
        
    def create_profile(self):
        """Create new profile"""
        existing_names = [self.profile_list.item(i).text() 
                         for i in range(self.profile_list.count())]
        
        dialog = ProfileCreateDialog(self, existing_names)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_profile_data()
            
            try:
                self.create_profile_bundle(data)
                self.load_profiles()
                
                if data['switch_after_create']:
                    # Find and switch to new profile
                    for i in range(self.profile_list.count()):
                        item = self.profile_list.item(i)
                        if item.text() == data['name']:
                            self.profile_list.setCurrentItem(item)
                            self.switch_profile()
                            break
                            
                self.profile_created.emit(data['name'])
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to create profile:\n{e}")
                
    def create_profile_bundle(self, data: Dict):
        """Create profile bundle from template"""
        profile_name = data['name']
        profile_path = self.profiles_dir / profile_name
        
        # Create profile directory
        profile_path.mkdir(exist_ok=True)
        
        # Copy template files based on selection
        template_name = data['template']
        if "ATC" in template_name:
            template_path = self.templates_dir / "atc_sim"
        elif "Lathe" in template_name:
            template_path = self.templates_dir / "probe_basic_lathe"
        elif "Custom" in template_name:
            template_path = None  # Empty profile
        else:
            template_path = self.templates_dir / "probe_basic"
            
        if template_path and template_path.exists():
            # Copy template files
            for file_path in template_path.iterdir():
                if file_path.is_file() and any(file_path.suffix == ext 
                                             for ext in self.PROFILE_EXTENSIONS):
                    dest_path = profile_path / file_path.name
                    shutil.copy2(file_path, dest_path)
        else:
            # Create minimal profile structure
            self.create_minimal_profile(profile_path)
            
        # Create profile metadata
        metadata = {
            'name': profile_name,
            'description': data['description'],
            'template': template_name,
            'created': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        metadata_file = profile_path / "profile.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def create_minimal_profile(self, profile_path: Path):
        """Create minimal profile structure"""
        # Create basic INI file
        ini_content = """[DISPLAY]
DISPLAY = probe_basic
POSITION_OFFSET = RELATIVE
POSITION_FEEDBACK = ACTUAL

[TASK]
TASK = milltask
CYCLE_TIME = 0.001

[RS274NGC]
PARAMETER_FILE = probe_basic.var

[EMCMOT]
EMCMOT = motmod
COMM_TIMEOUT = 1.0
SERVO_PERIOD = 1000000

[HAL]
HALFILE = probe_basic.hal
POSTGUI_HALFILE = probe_basic_postgui.hal

[TRAJ]
AXES = 3
COORDINATES = X Y Z
"""
        
        ini_file = profile_path / f"{profile_path.name}.ini"
        with open(ini_file, 'w') as f:
            f.write(ini_content)
            
        # Create basic HAL file
        hal_content = """# Basic HAL configuration
loadrt trivkins
loadrt [EMCMOT]EMCMOT servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=3

# Standard components
addf motion-command-handler servo-thread
addf motion-controller servo-thread
"""
        
        hal_file = profile_path / "probe_basic.hal"
        with open(hal_file, 'w') as f:
            f.write(hal_content)
            
        # Create postgui HAL file
        postgui_content = """# Post GUI HAL configuration
# Add post-GUI HAL commands here
"""
        
        postgui_file = profile_path / "probe_basic_postgui.hal"
        with open(postgui_file, 'w') as f:
            f.write(postgui_content)
            
    def clone_profile(self):
        """Clone selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        source_name = current_item.text()
        source_path = Path(current_item.data(1))
        
        # Get new name
        new_name, ok = self.get_new_profile_name(f"{source_name}_copy")
        if not ok or not new_name:
            return
            
        try:
            dest_path = self.profiles_dir / new_name
            
            # Copy entire profile directory
            shutil.copytree(source_path, dest_path)
            
            # Update metadata
            metadata_file = dest_path / "profile.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                metadata['name'] = new_name
                metadata['description'] = f"Copy of {source_name}"
                metadata['created'] = datetime.now().isoformat()
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                    
            self.load_profiles()
            self.profile_created.emit(new_name)
            self.status_label.setText(f"Cloned profile: {new_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to clone profile:\n{e}")
            
    def get_new_profile_name(self, default_name: str) -> Tuple[str, bool]:
        """Get new profile name from user"""
        existing_names = [self.profile_list.item(i).text() 
                         for i in range(self.profile_list.count())]
        
        name = default_name
        counter = 1
        while name in existing_names:
            name = f"{default_name}_{counter}"
            counter += 1
            
        # Use QInputDialog for getting text input
        text, ok = QInputDialog.getText(self, "Clone Profile", 
                                       "Enter name for cloned profile:", 
                                       text=name)
        
        if ok and text.strip():
            final_name = text.strip()
            if final_name not in existing_names:
                return final_name, True
            else:
                QMessageBox.warning(self, "Error", "Profile name already exists")
                return "", False
        return "", False
        
    def switch_profile(self):
        """Switch to selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        profile_name = current_item.text()
        profile_path = Path(current_item.data(1))
        
        # Confirm profile switch
        reply = QMessageBox.question(
            self, "Switch Profile",
            f"Switch to profile '{profile_name}'?\n\n"
            "This will restart the application with the new configuration.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Find INI file in profile
                ini_files = list(profile_path.glob("*.ini"))
                if not ini_files:
                    QMessageBox.warning(self, "Error", 
                                      "No INI file found in profile directory")
                    return
                    
                ini_file = ini_files[0]  # Use first INI file found
                
                # Emit signals
                self.profile_switched.emit(profile_name)
                self.restart_requested.emit(str(ini_file))
                
                self.status_label.setText(f"Switching to profile: {profile_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to switch profile:\n{e}")
                
    def delete_profile(self):
        """Delete selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        profile_name = current_item.text()
        profile_path = Path(current_item.data(1))
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete profile '{profile_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(profile_path)
                self.load_profiles()
                self.profile_deleted.emit(profile_name)
                self.status_label.setText(f"Deleted profile: {profile_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to delete profile:\n{e}")
                
    def get_profile_list(self) -> List[str]:
        """Get list of available profile names"""
        return [self.profile_list.item(i).text() 
                for i in range(self.profile_list.count())]
                
    def get_current_profile(self) -> Optional[str]:
        """Get current profile name"""
        return self.current_profile
        
    def export_profile(self, profile_name: str, export_path: str) -> bool:
        """Export profile to ZIP file"""
        try:
            profile_path = self.profiles_dir / profile_name
            if not profile_path.exists():
                return False
                
            import zipfile
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in profile_path.rglob('*'):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(profile_path)
                        zf.write(file_path, arc_name)
                        
            return True
            
        except Exception:
            return False
            
    def import_profile(self, import_path: str, profile_name: str) -> bool:
        """Import profile from ZIP file"""
        try:
            profile_path = self.profiles_dir / profile_name
            
            import zipfile
            with zipfile.ZipFile(import_path, 'r') as zf:
                zf.extractall(profile_path)
                
            self.load_profiles()
            return True
            
        except Exception:
            return False