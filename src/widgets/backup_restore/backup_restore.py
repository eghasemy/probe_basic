"""
Backup/Restore System Widget
Phase 9 - Settings, Profiles & Network

Provides comprehensive backup and restore functionality for:
- Profile bundles (INI + HAL + YAML + pinmap)
- Application settings
- Network configurations
- Factory reset capability
"""

import os
import shutil
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                                QLabel, QPushButton, QListWidget, QListWidgetItem,
                                QMessageBox, QFileDialog, QProgressBar, QTextEdit,
                                QCheckBox, QTabWidget, QFormLayout, QLineEdit,
                                QComboBox, QSplitter, QTreeWidget, QTreeWidgetItem)
    from PyQt5.QtCore import pyqtSignal, QTimer, QThread, QObject
    from PyQt5.QtGui import QIcon, QFont
except ImportError:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QPushButton, QListWidget, QListWidgetItem,
                            QMessageBox, QFileDialog, QTextEdit, QCheckBox,
                            QTabWidget, QFormLayout, QLineEdit, QComboBox,
                            QSplitter, QTreeWidget, QTreeWidgetItem, QIcon, QFont)
    from PyQt4.QtCore import pyqtSignal, QTimer, QThread, QObject
    
    # Create QProgressBar stub for PyQt4 compatibility
    class QProgressBar(QWidget):
        def __init__(self, parent=None):
            super(QProgressBar, self).__init__(parent)
        def setValue(self, value): pass
        def setMaximum(self, value): pass


class BackupWorker(QObject):
    """Worker thread for backup/restore operations"""
    
    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(int, str)   # progress percentage, status
    
    def __init__(self, operation, **kwargs):
        super(BackupWorker, self).__init__()
        self.operation = operation
        self.kwargs = kwargs
        
    def run(self):
        """Run backup/restore operation"""
        try:
            if self.operation == "backup":
                success, message = self.create_backup()
            elif self.operation == "restore":
                success, message = self.restore_backup()
            elif self.operation == "factory_reset":
                success, message = self.factory_reset()
            else:
                success, message = False, f"Unknown operation: {self.operation}"
                
            self.finished.emit(success, message)
            
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def create_backup(self) -> Tuple[bool, str]:
        """Create backup archive"""
        backup_path = self.kwargs['backup_path']
        include_profiles = self.kwargs.get('include_profiles', True)
        include_settings = self.kwargs.get('include_settings', True)
        include_network = self.kwargs.get('include_network', True)
        selected_profiles = self.kwargs.get('selected_profiles', [])
        
        self.progress.emit(10, "Initializing backup...")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                total_steps = 0
                current_step = 0
                
                # Count total steps
                if include_profiles:
                    total_steps += len(selected_profiles) if selected_profiles else 10
                if include_settings:
                    total_steps += 5
                if include_network:
                    total_steps += 3
                    
                # Create backup metadata
                metadata = {
                    'created_at': datetime.now().isoformat(),
                    'pb_touch_version': '1.0',
                    'backup_type': 'full',
                    'includes': {
                        'profiles': include_profiles,
                        'settings': include_settings,
                        'network': include_network
                    }
                }
                
                # Add metadata
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                    json.dump(metadata, tmp, indent=2)
                    tmp.flush()
                    zf.write(tmp.name, 'backup_metadata.json')
                    os.unlink(tmp.name)
                    
                self.progress.emit(20, "Added metadata...")
                
                # Backup profiles
                if include_profiles:
                    profiles_dir = Path.home() / ".pb-touch" / "profiles"
                    if profiles_dir.exists():
                        if selected_profiles:
                            # Backup selected profiles only
                            for profile_name in selected_profiles:
                                profile_path = profiles_dir / profile_name
                                if profile_path.exists():
                                    self.add_directory_to_zip(zf, profile_path, f"profiles/{profile_name}")
                                    current_step += 1
                                    progress = 20 + (current_step * 60 // total_steps)
                                    self.progress.emit(progress, f"Backing up profile: {profile_name}")
                        else:
                            # Backup all profiles
                            self.add_directory_to_zip(zf, profiles_dir, "profiles")
                            current_step += 10
                            self.progress.emit(50, "Backed up all profiles")
                            
                # Backup settings
                if include_settings:
                    settings_dir = Path.home() / ".pb-touch" / "settings"
                    if settings_dir.exists():
                        self.add_directory_to_zip(zf, settings_dir, "settings")
                        current_step += 5
                        progress = 20 + (current_step * 60 // total_steps)
                        self.progress.emit(progress, "Backed up settings")
                        
                # Backup network configuration
                if include_network:
                    network_dir = Path.home() / ".pb-touch" / "network"
                    if network_dir.exists():
                        self.add_directory_to_zip(zf, network_dir, "network")
                        current_step += 3
                        progress = 20 + (current_step * 60 // total_steps)
                        self.progress.emit(progress, "Backed up network configuration")
                        
                self.progress.emit(100, "Backup completed successfully")
                
            return True, f"Backup created successfully: {backup_path}"
            
        except Exception as e:
            return False, f"Backup failed: {e}"
            
    def add_directory_to_zip(self, zf: zipfile.ZipFile, source_dir: Path, archive_path: str):
        """Add directory contents to ZIP file"""
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                arc_name = archive_path + "/" + str(file_path.relative_to(source_dir))
                zf.write(file_path, arc_name)
                
    def restore_backup(self) -> Tuple[bool, str]:
        """Restore from backup archive"""
        backup_path = self.kwargs['backup_path']
        restore_profiles = self.kwargs.get('restore_profiles', True)
        restore_settings = self.kwargs.get('restore_settings', True)
        restore_network = self.kwargs.get('restore_network', True)
        
        self.progress.emit(10, "Opening backup archive...")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # Verify backup
                if 'backup_metadata.json' not in zf.namelist():
                    return False, "Invalid backup file: missing metadata"
                    
                # Read metadata
                with zf.open('backup_metadata.json') as meta_file:
                    metadata = json.load(meta_file)
                    
                self.progress.emit(20, "Verified backup metadata")
                
                pb_touch_dir = Path.home() / ".pb-touch"
                pb_touch_dir.mkdir(exist_ok=True)
                
                current_progress = 20
                
                # Restore profiles
                if restore_profiles and any(name.startswith('profiles/') for name in zf.namelist()):
                    self.progress.emit(current_progress, "Restoring profiles...")
                    
                    profiles_dir = pb_touch_dir / "profiles"
                    
                    # Extract profile files
                    for name in zf.namelist():
                        if name.startswith('profiles/') and name != 'profiles/':
                            target_path = pb_touch_dir / name
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with zf.open(name) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                                
                    current_progress = 50
                    self.progress.emit(current_progress, "Profiles restored")
                    
                # Restore settings
                if restore_settings and any(name.startswith('settings/') for name in zf.namelist()):
                    self.progress.emit(current_progress, "Restoring settings...")
                    
                    for name in zf.namelist():
                        if name.startswith('settings/') and name != 'settings/':
                            target_path = pb_touch_dir / name
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with zf.open(name) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                                
                    current_progress = 75
                    self.progress.emit(current_progress, "Settings restored")
                    
                # Restore network configuration
                if restore_network and any(name.startswith('network/') for name in zf.namelist()):
                    self.progress.emit(current_progress, "Restoring network configuration...")
                    
                    for name in zf.namelist():
                        if name.startswith('network/') and name != 'network/':
                            target_path = pb_touch_dir / name
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with zf.open(name) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                                
                    current_progress = 90
                    self.progress.emit(current_progress, "Network configuration restored")
                    
                self.progress.emit(100, "Restore completed successfully")
                
            return True, f"Backup restored successfully from: {backup_path}"
            
        except Exception as e:
            return False, f"Restore failed: {e}"
            
    def factory_reset(self) -> Tuple[bool, str]:
        """Perform factory reset"""
        self.progress.emit(10, "Starting factory reset...")
        
        try:
            pb_touch_dir = Path.home() / ".pb-touch"
            
            if pb_touch_dir.exists():
                self.progress.emit(30, "Removing user configurations...")
                
                # Remove all user configurations
                shutil.rmtree(pb_touch_dir)
                
                self.progress.emit(60, "Recreating default directories...")
                
                # Recreate basic directory structure
                (pb_touch_dir / "profiles").mkdir(parents=True, exist_ok=True)
                (pb_touch_dir / "settings").mkdir(parents=True, exist_ok=True)
                (pb_touch_dir / "network").mkdir(parents=True, exist_ok=True)
                (pb_touch_dir / "logs").mkdir(parents=True, exist_ok=True)
                
                self.progress.emit(80, "Creating default configuration...")
                
                # Create default settings
                default_settings = {
                    'units': 'Imperial (inches)',
                    'theme': 'Default Touch',
                    'scale_factor': 100,
                    'touch_enabled': True,
                    'created_by': 'factory_reset',
                    'created_at': datetime.now().isoformat()
                }
                
                settings_file = pb_touch_dir / "settings" / "settings.json"
                with open(settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                    
                self.progress.emit(100, "Factory reset completed")
                
            return True, "Factory reset completed successfully"
            
        except Exception as e:
            return False, f"Factory reset failed: {e}"


class BackupRestore(QWidget):
    """
    Backup/Restore System Widget
    
    Provides comprehensive backup and restore functionality including:
    - Profile bundle backup/restore
    - Settings backup/restore
    - Network configuration backup/restore
    - Factory reset capability
    """
    
    # Signals
    backup_completed = pyqtSignal(str)       # backup_path
    restore_completed = pyqtSignal()         # restore completed
    factory_reset_completed = pyqtSignal()   # factory reset completed
    
    def __init__(self, parent=None):
        super(BackupRestore, self).__init__(parent)
        
        # Configuration
        self.pb_touch_dir = Path.home() / ".pb-touch"
        self.backups_dir = self.pb_touch_dir / "backups"
        
        # Ensure directories exist
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # Worker thread
        self.worker_thread = None
        self.worker = None
        
        self.init_ui()
        self.scan_existing_backups()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Backup & Restore")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Backup tab
        self.backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(self.backup_tab, "Create Backup")
        
        # Restore tab
        self.restore_tab = self.create_restore_tab()
        self.tab_widget.addTab(self.restore_tab, "Restore")
        
        # Manage tab
        self.manage_tab = self.create_manage_tab()
        self.tab_widget.addTab(self.manage_tab, "Manage Backups")
        
        layout.addWidget(self.tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 4px; color: #666;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def create_backup_tab(self):
        """Create backup creation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Backup options
        options_group = QGroupBox("Backup Options")
        options_layout = QVBoxLayout()
        
        # What to backup
        self.backup_profiles_check = QCheckBox("Profiles")
        self.backup_profiles_check.setChecked(True)
        self.backup_profiles_check.stateChanged.connect(self.update_profile_selection)
        options_layout.addWidget(self.backup_profiles_check)
        
        # Profile selection
        self.profile_selection_widget = QWidget()
        profile_layout = QVBoxLayout()
        profile_layout.addWidget(QLabel("Select Profiles:"))
        
        self.profile_list = QListWidget()
        self.profile_list.setMaximumHeight(150)
        self.load_profiles_for_backup()
        profile_layout.addWidget(self.profile_list)
        
        profile_buttons = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_profiles)
        profile_buttons.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_no_profiles)
        profile_buttons.addWidget(self.select_none_btn)
        profile_buttons.addStretch()
        
        profile_layout.addLayout(profile_buttons)
        self.profile_selection_widget.setLayout(profile_layout)
        options_layout.addWidget(self.profile_selection_widget)
        
        self.backup_settings_check = QCheckBox("Application Settings")
        self.backup_settings_check.setChecked(True)
        options_layout.addWidget(self.backup_settings_check)
        
        self.backup_network_check = QCheckBox("Network Configuration")
        self.backup_network_check.setChecked(True)
        options_layout.addWidget(self.backup_network_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Backup location
        location_group = QGroupBox("Backup Location")
        location_layout = QFormLayout()
        
        location_h_layout = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        default_backup = self.backups_dir / f"pb_touch_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        self.backup_path_edit.setText(str(default_backup))
        location_h_layout.addWidget(self.backup_path_edit)
        
        self.browse_backup_btn = QPushButton("Browse...")
        self.browse_backup_btn.clicked.connect(self.browse_backup_location)
        location_h_layout.addWidget(self.browse_backup_btn)
        
        location_layout.addRow("Backup File:", location_h_layout)
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Create backup button
        self.create_backup_btn = QPushButton("Create Backup")
        self.create_backup_btn.clicked.connect(self.create_backup)
        self.create_backup_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        layout.addWidget(self.create_backup_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_restore_tab(self):
        """Create restore tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Backup file selection
        file_group = QGroupBox("Backup File")
        file_layout = QFormLayout()
        
        file_h_layout = QHBoxLayout()
        self.restore_path_edit = QLineEdit()
        self.restore_path_edit.setPlaceholderText("Select backup file to restore...")
        file_h_layout.addWidget(self.restore_path_edit)
        
        self.browse_restore_btn = QPushButton("Browse...")
        self.browse_restore_btn.clicked.connect(self.browse_restore_file)
        file_h_layout.addWidget(self.browse_restore_btn)
        
        file_layout.addRow("Backup File:", file_h_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Backup info
        self.backup_info_group = QGroupBox("Backup Information")
        self.backup_info_layout = QFormLayout()
        
        self.info_created = QLabel("-")
        self.backup_info_layout.addRow("Created:", self.info_created)
        
        self.info_version = QLabel("-")
        self.backup_info_layout.addRow("Version:", self.info_version)
        
        self.info_type = QLabel("-")
        self.backup_info_layout.addRow("Type:", self.info_type)
        
        self.backup_info_group.setLayout(self.backup_info_layout)
        self.backup_info_group.setVisible(False)
        layout.addWidget(self.backup_info_group)
        
        # Restore options
        self.restore_options_group = QGroupBox("Restore Options")
        restore_options_layout = QVBoxLayout()
        
        self.restore_profiles_check = QCheckBox("Restore Profiles")
        self.restore_profiles_check.setChecked(True)
        restore_options_layout.addWidget(self.restore_profiles_check)
        
        self.restore_settings_check = QCheckBox("Restore Settings")
        self.restore_settings_check.setChecked(True)
        restore_options_layout.addWidget(self.restore_settings_check)
        
        self.restore_network_check = QCheckBox("Restore Network Configuration")
        self.restore_network_check.setChecked(True)
        restore_options_layout.addWidget(self.restore_network_check)
        
        self.restore_options_group.setLayout(restore_options_layout)
        self.restore_options_group.setVisible(False)
        layout.addWidget(self.restore_options_group)
        
        # Restore button
        self.restore_backup_btn = QPushButton("Restore Backup")
        self.restore_backup_btn.clicked.connect(self.restore_backup)
        self.restore_backup_btn.setEnabled(False)
        self.restore_backup_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        layout.addWidget(self.restore_backup_btn)
        
        # Connect file path change to validation
        self.restore_path_edit.textChanged.connect(self.validate_restore_file)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_manage_tab(self):
        """Create backup management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Existing backups
        backups_group = QGroupBox("Existing Backups")
        backups_layout = QVBoxLayout()
        
        self.backups_list = QListWidget()
        self.backups_list.currentItemChanged.connect(self.on_backup_selected)
        backups_layout.addWidget(self.backups_list)
        
        # Backup actions
        backup_actions = QHBoxLayout()
        
        self.refresh_backups_btn = QPushButton("Refresh")
        self.refresh_backups_btn.clicked.connect(self.scan_existing_backups)
        backup_actions.addWidget(self.refresh_backups_btn)
        
        self.delete_backup_btn = QPushButton("Delete")
        self.delete_backup_btn.clicked.connect(self.delete_backup)
        self.delete_backup_btn.setEnabled(False)
        backup_actions.addWidget(self.delete_backup_btn)
        
        self.export_backup_btn = QPushButton("Export...")
        self.export_backup_btn.clicked.connect(self.export_backup)
        self.export_backup_btn.setEnabled(False)
        backup_actions.addWidget(self.export_backup_btn)
        
        backup_actions.addStretch()
        backups_layout.addLayout(backup_actions)
        
        backups_group.setLayout(backups_layout)
        layout.addWidget(backups_group)
        
        # Factory reset
        factory_group = QGroupBox("Factory Reset")
        factory_layout = QVBoxLayout()
        
        warning_label = QLabel("⚠️ Factory reset will remove ALL profiles, settings, and configurations!")
        warning_label.setStyleSheet("color: red; font-weight: bold; padding: 8px;")
        factory_layout.addWidget(warning_label)
        
        factory_text = QLabel(
            "This will:\n"
            "• Delete all user profiles\n"
            "• Reset all settings to defaults\n"
            "• Remove network configurations\n"
            "• Clear all customizations\n\n"
            "Consider creating a backup before proceeding."
        )
        factory_layout.addWidget(factory_text)
        
        self.factory_reset_btn = QPushButton("Factory Reset")
        self.factory_reset_btn.clicked.connect(self.factory_reset)
        self.factory_reset_btn.setStyleSheet("QPushButton { padding: 8px; background-color: #d32f2f; color: white; font-weight: bold; }")
        factory_layout.addWidget(self.factory_reset_btn)
        
        factory_group.setLayout(factory_layout)
        layout.addWidget(factory_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def load_profiles_for_backup(self):
        """Load available profiles for backup selection"""
        self.profile_list.clear()
        
        profiles_dir = self.pb_touch_dir / "profiles"
        if profiles_dir.exists():
            for profile_dir in profiles_dir.iterdir():
                if profile_dir.is_dir():
                    item = QListWidgetItem(profile_dir.name)
                    item.setCheckState(2)  # Checked
                    self.profile_list.addItem(item)
                    
    def update_profile_selection(self):
        """Update profile selection visibility"""
        enabled = self.backup_profiles_check.isChecked()
        self.profile_selection_widget.setVisible(enabled)
        
    def select_all_profiles(self):
        """Select all profiles for backup"""
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            item.setCheckState(2)  # Checked
            
    def select_no_profiles(self):
        """Deselect all profiles"""
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            item.setCheckState(0)  # Unchecked
            
    def browse_backup_location(self):
        """Browse for backup save location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup As", 
            str(self.backups_dir),
            "ZIP files (*.zip);;All files (*)"
        )
        
        if file_path:
            self.backup_path_edit.setText(file_path)
            
    def browse_restore_file(self):
        """Browse for backup file to restore"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File",
            str(self.backups_dir),
            "ZIP files (*.zip);;All files (*)"
        )
        
        if file_path:
            self.restore_path_edit.setText(file_path)
            
    def validate_restore_file(self):
        """Validate selected restore file"""
        file_path = self.restore_path_edit.text().strip()
        
        if not file_path or not os.path.exists(file_path):
            self.backup_info_group.setVisible(False)
            self.restore_options_group.setVisible(False)
            self.restore_backup_btn.setEnabled(False)
            return
            
        try:
            # Try to read backup metadata
            with zipfile.ZipFile(file_path, 'r') as zf:
                if 'backup_metadata.json' in zf.namelist():
                    with zf.open('backup_metadata.json') as meta_file:
                        metadata = json.load(meta_file)
                        
                    # Update info display
                    self.info_created.setText(metadata.get('created_at', 'Unknown'))
                    self.info_version.setText(metadata.get('pb_touch_version', 'Unknown'))
                    self.info_type.setText(metadata.get('backup_type', 'Unknown'))
                    
                    # Show available restore options
                    includes = metadata.get('includes', {})
                    self.restore_profiles_check.setVisible(includes.get('profiles', False))
                    self.restore_settings_check.setVisible(includes.get('settings', False))
                    self.restore_network_check.setVisible(includes.get('network', False))
                    
                    self.backup_info_group.setVisible(True)
                    self.restore_options_group.setVisible(True)
                    self.restore_backup_btn.setEnabled(True)
                else:
                    raise ValueError("Invalid backup file")
                    
        except Exception as e:
            self.backup_info_group.setVisible(False)
            self.restore_options_group.setVisible(False)
            self.restore_backup_btn.setEnabled(False)
            QMessageBox.warning(self, "Invalid Backup", f"Selected file is not a valid backup:\n{e}")
            
    def create_backup(self):
        """Create backup"""
        backup_path = self.backup_path_edit.text().strip()
        if not backup_path:
            QMessageBox.warning(self, "Error", "Please specify backup location")
            return
            
        # Ensure backup directory exists
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Get selected profiles
        selected_profiles = []
        if self.backup_profiles_check.isChecked():
            for i in range(self.profile_list.count()):
                item = self.profile_list.item(i)
                if item.checkState() == 2:  # Checked
                    selected_profiles.append(item.text())
                    
        # Prepare backup parameters
        backup_params = {
            'backup_path': backup_path,
            'include_profiles': self.backup_profiles_check.isChecked(),
            'include_settings': self.backup_settings_check.isChecked(),
            'include_network': self.backup_network_check.isChecked(),
            'selected_profiles': selected_profiles
        }
        
        self.start_operation("backup", **backup_params)
        
    def restore_backup(self):
        """Restore backup"""
        backup_path = self.restore_path_edit.text().strip()
        if not backup_path or not os.path.exists(backup_path):
            QMessageBox.warning(self, "Error", "Please select a valid backup file")
            return
            
        # Confirm restore
        reply = QMessageBox.question(
            self, "Confirm Restore",
            "Are you sure you want to restore this backup?\n\n"
            "This will overwrite existing profiles and settings.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            restore_params = {
                'backup_path': backup_path,
                'restore_profiles': self.restore_profiles_check.isChecked(),
                'restore_settings': self.restore_settings_check.isChecked(),
                'restore_network': self.restore_network_check.isChecked()
            }
            
            self.start_operation("restore", **restore_params)
            
    def factory_reset(self):
        """Perform factory reset"""
        # Double confirmation for factory reset
        reply1 = QMessageBox.question(
            self, "Factory Reset Confirmation",
            "Are you absolutely sure you want to perform a factory reset?\n\n"
            "This will permanently delete ALL user data, profiles, and settings.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply1 == QMessageBox.Yes:
            reply2 = QMessageBox.question(
                self, "Final Confirmation",
                "LAST WARNING: This action cannot be undone!\n\n"
                "All profiles, settings, and customizations will be permanently lost.\n\n"
                "Continue with factory reset?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply2 == QMessageBox.Yes:
                self.start_operation("factory_reset")
                
    def start_operation(self, operation: str, **kwargs):
        """Start backup/restore operation in worker thread"""
        if self.worker_thread and self.worker_thread.isRunning():
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable relevant buttons
        self.create_backup_btn.setEnabled(False)
        self.restore_backup_btn.setEnabled(False)
        self.factory_reset_btn.setEnabled(False)
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = BackupWorker(operation, **kwargs)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_operation_progress)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Start operation
        self.worker_thread.start()
        
    def on_operation_progress(self, progress: int, status: str):
        """Handle operation progress update"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        
    def on_operation_finished(self, success: bool, message: str):
        """Handle operation completion"""
        self.progress_bar.setVisible(False)
        
        # Re-enable buttons
        self.create_backup_btn.setEnabled(True)
        self.restore_backup_btn.setEnabled(True)
        self.factory_reset_btn.setEnabled(True)
        
        if success:
            self.status_label.setText(message)
            QMessageBox.information(self, "Success", message)
            
            # Emit appropriate signals and refresh
            if "Backup created" in message:
                self.backup_completed.emit(self.backup_path_edit.text())
                self.scan_existing_backups()
            elif "restored" in message:
                self.restore_completed.emit()
            elif "Factory reset" in message:
                self.factory_reset_completed.emit()
                
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
            
    def scan_existing_backups(self):
        """Scan for existing backup files"""
        self.backups_list.clear()
        
        if self.backups_dir.exists():
            for backup_file in self.backups_dir.glob("*.zip"):
                item = QListWidgetItem(backup_file.name)
                item.setData(1, str(backup_file))
                
                # Try to get backup info
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zf:
                        if 'backup_metadata.json' in zf.namelist():
                            with zf.open('backup_metadata.json') as meta_file:
                                metadata = json.load(meta_file)
                                created_at = metadata.get('created_at', 'Unknown')
                                item.setToolTip(f"Created: {created_at}")
                except:
                    item.setToolTip("Backup file (metadata unavailable)")
                    
                self.backups_list.addItem(item)
                
        self.status_label.setText(f"Found {self.backups_list.count()} backups")
        
    def on_backup_selected(self):
        """Handle backup selection in manage tab"""
        has_selection = self.backups_list.currentItem() is not None
        self.delete_backup_btn.setEnabled(has_selection)
        self.export_backup_btn.setEnabled(has_selection)
        
    def delete_backup(self):
        """Delete selected backup"""
        current_item = self.backups_list.currentItem()
        if not current_item:
            return
            
        backup_path = current_item.data(1)
        backup_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Delete Backup",
            f"Are you sure you want to delete backup '{backup_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(backup_path)
                self.scan_existing_backups()
                self.status_label.setText(f"Deleted backup: {backup_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete backup:\n{e}")
                
    def export_backup(self):
        """Export backup to another location"""
        current_item = self.backups_list.currentItem()
        if not current_item:
            return
            
        source_path = current_item.data(1)
        backup_name = current_item.text()
        
        export_path, _ = QFileDialog.getSaveFileName(
            self, "Export Backup As",
            backup_name,
            "ZIP files (*.zip);;All files (*)"
        )
        
        if export_path:
            try:
                shutil.copy2(source_path, export_path)
                self.status_label.setText(f"Exported backup to: {export_path}")
                QMessageBox.information(self, "Success", f"Backup exported to:\n{export_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export backup:\n{e}")
                
    def get_backup_list(self) -> List[str]:
        """Get list of available backups"""
        backups = []
        for i in range(self.backups_list.count()):
            item = self.backups_list.item(i)
            backups.append(item.text())
        return backups