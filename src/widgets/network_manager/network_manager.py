"""
Network Mount Manager Widget
Phase 9 - Settings, Profiles & Network

Manages SMB/NFS network share mounting with credentials vault and persistence.
Integrates with file browser for seamless access to network shares.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from base64 import b64encode, b64decode

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                                QListWidgetItem, QPushButton, QLabel, QLineEdit,
                                QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
                                QComboBox, QGroupBox, QCheckBox, QTextEdit, QProgressBar,
                                QTabWidget, QTreeWidget, QTreeWidgetItem, QSplitter)
    from PyQt5.QtCore import pyqtSignal, QTimer, QThread, QObject
    from PyQt5.QtGui import QIcon
except ImportError:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                            QListWidgetItem, QPushButton, QLabel, QLineEdit,
                            QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
                            QComboBox, QGroupBox, QCheckBox, QTextEdit, QIcon,
                            QTabWidget, QTreeWidget, QTreeWidgetItem, QSplitter)
    from PyQt4.QtCore import pyqtSignal, QTimer, QThread, QObject
    
    # Create QProgressBar stub for PyQt4 compatibility
    class QProgressBar(QWidget):
        def __init__(self, parent=None):
            super(QProgressBar, self).__init__(parent)
        def setValue(self, value): pass
        def setMaximum(self, value): pass


class MountWorker(QObject):
    """Worker thread for mount operations"""
    
    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(int)        # progress percentage
    
    def __init__(self, operation, share_config):
        super(MountWorker, self).__init__()
        self.operation = operation
        self.share_config = share_config
        
    def run(self):
        """Run mount operation"""
        try:
            if self.operation == "mount":
                success, message = self.mount_share()
            elif self.operation == "unmount":
                success, message = self.unmount_share()
            else:
                success, message = False, f"Unknown operation: {self.operation}"
                
            self.finished.emit(success, message)
            
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def mount_share(self) -> Tuple[bool, str]:
        """Mount network share"""
        share_type = self.share_config['type']
        server = self.share_config['server']
        share_name = self.share_config['share']
        mount_point = self.share_config['mount_point']
        username = self.share_config.get('username', '')
        password = self.share_config.get('password', '')
        
        self.progress.emit(25)
        
        # Create mount point
        mount_path = Path(mount_point)
        mount_path.mkdir(parents=True, exist_ok=True)
        
        self.progress.emit(50)
        
        if share_type.lower() == 'smb':
            return self.mount_smb(server, share_name, mount_point, username, password)
        elif share_type.lower() == 'nfs':
            return self.mount_nfs(server, share_name, mount_point)
        else:
            return False, f"Unsupported share type: {share_type}"
            
    def mount_smb(self, server: str, share: str, mount_point: str, 
                  username: str, password: str) -> Tuple[bool, str]:
        """Mount SMB share"""
        try:
            self.progress.emit(75)
            
            # Build mount command
            share_path = f"//{server}/{share}"
            cmd = ["sudo", "mount", "-t", "cifs", share_path, mount_point]
            
            # Add options
            options = ["rw", "nosuid", "nodev"]
            if username:
                options.append(f"username={username}")
                if password:
                    options.append(f"password={password}")
                else:
                    options.append("password=")
            else:
                options.append("guest")
                
            options.append("uid=1000")  # Current user
            options.append("gid=1000")
            options.append("iocharset=utf8")
            
            cmd.extend(["-o", ",".join(options)])
            
            # Execute mount command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            self.progress.emit(100)
            
            if result.returncode == 0:
                return True, f"Successfully mounted {share_path}"
            else:
                return False, f"Mount failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Mount operation timed out"
        except Exception as e:
            return False, f"Mount error: {e}"
            
    def mount_nfs(self, server: str, share: str, mount_point: str) -> Tuple[bool, str]:
        """Mount NFS share"""
        try:
            self.progress.emit(75)
            
            # Build mount command
            share_path = f"{server}:{share}"
            cmd = ["sudo", "mount", "-t", "nfs", share_path, mount_point]
            
            # Add NFS options
            options = ["rw", "nosuid", "nodev", "soft", "intr", "timeo=10"]
            cmd.extend(["-o", ",".join(options)])
            
            # Execute mount command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            self.progress.emit(100)
            
            if result.returncode == 0:
                return True, f"Successfully mounted {share_path}"
            else:
                return False, f"Mount failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Mount operation timed out"
        except Exception as e:
            return False, f"Mount error: {e}"
            
    def unmount_share(self) -> Tuple[bool, str]:
        """Unmount network share"""
        try:
            mount_point = self.share_config['mount_point']
            
            self.progress.emit(50)
            
            # Execute unmount command
            cmd = ["sudo", "umount", mount_point]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            self.progress.emit(100)
            
            if result.returncode == 0:
                return True, f"Successfully unmounted {mount_point}"
            else:
                return False, f"Unmount failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Unmount operation timed out"
        except Exception as e:
            return False, f"Unmount error: {e}"


class ShareConfigDialog(QDialog):
    """Dialog for configuring network shares"""
    
    def __init__(self, parent=None, share_config=None):
        super(ShareConfigDialog, self).__init__(parent)
        self.share_config = share_config or {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Configure Network Share")
        self.setModal(True)
        self.resize(450, 400)
        
        layout = QVBoxLayout()
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Display name for this share")
        basic_layout.addRow("Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["SMB/CIFS", "NFS"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        basic_layout.addRow("Share Type:", self.type_combo)
        
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("Server IP or hostname")
        basic_layout.addRow("Server:", self.server_edit)
        
        self.share_edit = QLineEdit()
        self.share_edit.setPlaceholderText("Share name or path")
        basic_layout.addRow("Share Path:", self.share_edit)
        
        self.mount_point_edit = QLineEdit()
        self.mount_point_edit.setPlaceholderText("Local mount point")
        default_mount = os.path.expanduser("~/mnt/network_share")
        self.mount_point_edit.setText(default_mount)
        basic_layout.addRow("Mount Point:", self.mount_point_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Authentication settings
        self.auth_group = QGroupBox("Authentication (SMB/CIFS)")
        auth_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username (leave empty for guest)")
        auth_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password")
        auth_layout.addRow("Password:", self.password_edit)
        
        self.save_credentials_check = QCheckBox()
        self.save_credentials_check.setChecked(True)
        auth_layout.addRow("Save Credentials:", self.save_credentials_check)
        
        self.auth_group.setLayout(auth_layout)
        layout.addWidget(self.auth_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QFormLayout()
        
        self.auto_mount_check = QCheckBox()
        self.auto_mount_check.setChecked(True)
        options_layout.addRow("Auto-mount on startup:", self.auto_mount_check)
        
        self.readonly_check = QCheckBox()
        options_layout.addRow("Read-only:", self.readonly_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)
        
        # Load existing configuration
        if self.share_config:
            self.load_config()
            
        self.on_type_changed()
        
    def on_type_changed(self):
        """Handle share type change"""
        share_type = self.type_combo.currentText()
        self.auth_group.setVisible(share_type == "SMB/CIFS")
        
        if share_type == "NFS":
            self.share_edit.setPlaceholderText("/path/to/export")
        else:
            self.share_edit.setPlaceholderText("share_name")
            
    def load_config(self):
        """Load existing configuration"""
        self.name_edit.setText(self.share_config.get('name', ''))
        share_type = self.share_config.get('type', 'SMB')
        if share_type.upper() == 'SMB':
            self.type_combo.setCurrentText("SMB/CIFS")
        else:
            self.type_combo.setCurrentText("NFS")
            
        self.server_edit.setText(self.share_config.get('server', ''))
        self.share_edit.setText(self.share_config.get('share', ''))
        self.mount_point_edit.setText(self.share_config.get('mount_point', ''))
        self.username_edit.setText(self.share_config.get('username', ''))
        self.password_edit.setText(self.share_config.get('password', ''))
        self.auto_mount_check.setChecked(self.share_config.get('auto_mount', True))
        self.readonly_check.setChecked(self.share_config.get('readonly', False))
        
    def get_config(self) -> Dict:
        """Get share configuration"""
        share_type = "SMB" if self.type_combo.currentText() == "SMB/CIFS" else "NFS"
        
        config = {
            'name': self.name_edit.text().strip(),
            'type': share_type,
            'server': self.server_edit.text().strip(),
            'share': self.share_edit.text().strip(),
            'mount_point': self.mount_point_edit.text().strip(),
            'auto_mount': self.auto_mount_check.isChecked(),
            'readonly': self.readonly_check.isChecked()
        }
        
        if share_type == "SMB" and self.save_credentials_check.isChecked():
            config['username'] = self.username_edit.text().strip()
            config['password'] = self.password_edit.text()
            
        return config


class NetworkManager(QWidget):
    """
    Network Mount Manager Widget
    
    Manages SMB/NFS network share mounting with:
    - Share configuration and credentials management
    - Mount/unmount operations
    - Auto-mounting on startup
    - Integration with file browser
    """
    
    # Signals
    share_mounted = pyqtSignal(str, str)    # name, mount_point
    share_unmounted = pyqtSignal(str)       # name
    shares_changed = pyqtSignal()           # shares list changed
    
    def __init__(self, parent=None):
        super(NetworkManager, self).__init__(parent)
        
        # Configuration storage
        self.config_dir = Path.home() / ".pb-touch" / "network"
        self.shares_file = self.config_dir / "shares.json"
        self.credentials_file = self.config_dir / "credentials.json"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Shares configuration
        self.shares = self.load_shares()
        
        # Mount worker thread
        self.mount_thread = None
        self.mount_worker = None
        
        self.init_ui()
        self.load_shares_list()
        self.check_mount_status()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Network Share Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.check_mount_status)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Main content
        splitter = QSplitter()
        
        # Left panel - shares list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Configured Shares:"))
        
        self.shares_list = QListWidget()
        self.shares_list.currentItemChanged.connect(self.on_share_selected)
        left_layout.addWidget(self.shares_list)
        
        # Share control buttons
        share_buttons = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_share)
        share_buttons.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_share)
        self.edit_btn.setEnabled(False)
        share_buttons.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_share)
        self.delete_btn.setEnabled(False)
        share_buttons.addWidget(self.delete_btn)
        
        left_layout.addLayout(share_buttons)
        
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)
        
        # Right panel - share details and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Share details
        self.details_group = QGroupBox("Share Details")
        details_layout = QFormLayout()
        
        self.detail_name = QLabel("-")
        details_layout.addRow("Name:", self.detail_name)
        
        self.detail_type = QLabel("-")
        details_layout.addRow("Type:", self.detail_type)
        
        self.detail_server = QLabel("-")
        details_layout.addRow("Server:", self.detail_server)
        
        self.detail_share = QLabel("-")
        details_layout.addRow("Share:", self.detail_share)
        
        self.detail_mount_point = QLabel("-")
        details_layout.addRow("Mount Point:", self.detail_mount_point)
        
        self.detail_status = QLabel("-")
        details_layout.addRow("Status:", self.detail_status)
        
        self.details_group.setLayout(details_layout)
        right_layout.addWidget(self.details_group)
        
        # Mount controls
        mount_group = QGroupBox("Mount Controls")
        mount_layout = QVBoxLayout()
        
        mount_buttons = QHBoxLayout()
        
        self.mount_btn = QPushButton("Mount")
        self.mount_btn.clicked.connect(self.mount_share)
        self.mount_btn.setEnabled(False)
        mount_buttons.addWidget(self.mount_btn)
        
        self.unmount_btn = QPushButton("Unmount")
        self.unmount_btn.clicked.connect(self.unmount_share)
        self.unmount_btn.setEnabled(False)
        mount_buttons.addWidget(self.unmount_btn)
        
        mount_layout.addLayout(mount_buttons)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        mount_layout.addWidget(self.progress_bar)
        
        mount_group.setLayout(mount_layout)
        right_layout.addWidget(mount_group)
        
        # Auto-mount settings
        auto_group = QGroupBox("Auto-mount Settings")
        auto_layout = QVBoxLayout()
        
        auto_buttons = QHBoxLayout()
        
        self.mount_all_btn = QPushButton("Mount All Auto-mount Shares")
        self.mount_all_btn.clicked.connect(self.mount_all_auto_shares)
        auto_buttons.addWidget(self.mount_all_btn)
        
        self.unmount_all_btn = QPushButton("Unmount All")
        self.unmount_all_btn.clicked.connect(self.unmount_all_shares)
        auto_buttons.addWidget(self.unmount_all_btn)
        
        auto_layout.addLayout(auto_buttons)
        auto_group.setLayout(auto_layout)
        right_layout.addWidget(auto_group)
        
        right_layout.addStretch()
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        layout.addWidget(splitter)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 4px; color: #666;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def load_shares(self) -> Dict:
        """Load shares configuration"""
        if self.shares_file.exists():
            try:
                with open(self.shares_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load shares config: {e}")
                
        return {}
        
    def save_shares(self):
        """Save shares configuration"""
        try:
            with open(self.shares_file, 'w') as f:
                json.dump(self.shares, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shares config:\n{e}")
            
    def load_shares_list(self):
        """Load shares into list widget"""
        self.shares_list.clear()
        
        for share_name, config in self.shares.items():
            item = QListWidgetItem(share_name)
            item.setData(1, share_name)
            
            # Set tooltip with share details
            tooltip = f"Type: {config['type']}\nServer: {config['server']}\nShare: {config['share']}"
            item.setToolTip(tooltip)
            
            self.shares_list.addItem(item)
            
        self.status_label.setText(f"Loaded {len(self.shares)} shares")
        
    def on_share_selected(self):
        """Handle share selection"""
        current_item = self.shares_list.currentItem()
        has_selection = current_item is not None
        
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
        if has_selection:
            share_name = current_item.data(1)
            self.update_share_details(share_name)
            
    def update_share_details(self, share_name: str):
        """Update share details panel"""
        if share_name not in self.shares:
            return
            
        config = self.shares[share_name]
        
        self.detail_name.setText(share_name)
        self.detail_type.setText(config['type'])
        self.detail_server.setText(config['server'])
        self.detail_share.setText(config['share'])
        self.detail_mount_point.setText(config['mount_point'])
        
        # Check mount status
        is_mounted = self.is_mounted(config['mount_point'])
        status_text = "Mounted" if is_mounted else "Not mounted"
        status_color = "green" if is_mounted else "red"
        self.detail_status.setText(f"<span style='color: {status_color}'>{status_text}</span>")
        
        self.mount_btn.setEnabled(not is_mounted)
        self.unmount_btn.setEnabled(is_mounted)
        
    def is_mounted(self, mount_point: str) -> bool:
        """Check if mount point is currently mounted"""
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True)
            return mount_point in result.stdout
        except Exception:
            return False
            
    def check_mount_status(self):
        """Check status of all configured shares"""
        self.load_shares_list()
        if self.shares_list.currentItem():
            current_share = self.shares_list.currentItem().data(1)
            self.update_share_details(current_share)
            
    def add_share(self):
        """Add new share configuration"""
        dialog = ShareConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            share_name = config['name']
            
            if not share_name:
                QMessageBox.warning(self, "Error", "Share name is required")
                return
                
            if share_name in self.shares:
                QMessageBox.warning(self, "Error", "Share name already exists")
                return
                
            self.shares[share_name] = config
            self.save_shares()
            self.load_shares_list()
            self.shares_changed.emit()
            
    def edit_share(self):
        """Edit selected share configuration"""
        current_item = self.shares_list.currentItem()
        if not current_item:
            return
            
        share_name = current_item.data(1)
        config = self.shares[share_name].copy()
        
        dialog = ShareConfigDialog(self, config)
        if dialog.exec_() == QDialog.Accepted:
            new_config = dialog.get_config()
            new_name = new_config['name']
            
            # If name changed, handle rename
            if new_name != share_name:
                if new_name in self.shares:
                    QMessageBox.warning(self, "Error", "Share name already exists")
                    return
                del self.shares[share_name]
                
            self.shares[new_name] = new_config
            self.save_shares()
            self.load_shares_list()
            self.shares_changed.emit()
            
    def delete_share(self):
        """Delete selected share"""
        current_item = self.shares_list.currentItem()
        if not current_item:
            return
            
        share_name = current_item.data(1)
        
        reply = QMessageBox.question(
            self, "Delete Share",
            f"Are you sure you want to delete share '{share_name}'?\n\n"
            "This will not unmount the share if it's currently mounted.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.shares[share_name]
            self.save_shares()
            self.load_shares_list()
            self.shares_changed.emit()
            
    def mount_share(self):
        """Mount selected share"""
        current_item = self.shares_list.currentItem()
        if not current_item:
            return
            
        share_name = current_item.data(1)
        config = self.shares[share_name]
        
        self.start_mount_operation("mount", config)
        
    def unmount_share(self):
        """Unmount selected share"""
        current_item = self.shares_list.currentItem()
        if not current_item:
            return
            
        share_name = current_item.data(1)
        config = self.shares[share_name]
        
        self.start_mount_operation("unmount", config)
        
    def start_mount_operation(self, operation: str, config: Dict):
        """Start mount/unmount operation in worker thread"""
        if self.mount_thread and self.mount_thread.isRunning():
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.mount_btn.setEnabled(False)
        self.unmount_btn.setEnabled(False)
        
        # Create worker thread
        self.mount_thread = QThread()
        self.mount_worker = MountWorker(operation, config)
        self.mount_worker.moveToThread(self.mount_thread)
        
        # Connect signals
        self.mount_thread.started.connect(self.mount_worker.run)
        self.mount_worker.progress.connect(self.progress_bar.setValue)
        self.mount_worker.finished.connect(self.on_mount_finished)
        self.mount_worker.finished.connect(self.mount_thread.quit)
        self.mount_worker.finished.connect(self.mount_worker.deleteLater)
        self.mount_thread.finished.connect(self.mount_thread.deleteLater)
        
        # Start operation
        self.mount_thread.start()
        
    def on_mount_finished(self, success: bool, message: str):
        """Handle mount operation completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(message)
            
            # Emit appropriate signal
            current_item = self.shares_list.currentItem()
            if current_item:
                share_name = current_item.data(1)
                config = self.shares[share_name]
                
                if "mounted" in message.lower():
                    self.share_mounted.emit(share_name, config['mount_point'])
                else:
                    self.share_unmounted.emit(share_name)
                    
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Mount Error", message)
            
        # Update UI
        QTimer.singleShot(1000, self.check_mount_status)
        
    def mount_all_auto_shares(self):
        """Mount all shares configured for auto-mounting"""
        auto_shares = [name for name, config in self.shares.items() 
                      if config.get('auto_mount', False)]
        
        if not auto_shares:
            QMessageBox.information(self, "Info", "No shares configured for auto-mounting")
            return
            
        mounted_count = 0
        for share_name in auto_shares:
            config = self.shares[share_name]
            if not self.is_mounted(config['mount_point']):
                # Simple synchronous mount for auto-mounting
                success, _ = self.simple_mount_share(config)
                if success:
                    mounted_count += 1
                    
        self.status_label.setText(f"Auto-mounted {mounted_count}/{len(auto_shares)} shares")
        self.check_mount_status()
        
    def simple_mount_share(self, config: Dict) -> Tuple[bool, str]:
        """Simple synchronous mount operation"""
        try:
            worker = MountWorker("mount", config)
            return worker.mount_share()
        except Exception as e:
            return False, str(e)
            
    def unmount_all_shares(self):
        """Unmount all currently mounted shares"""
        reply = QMessageBox.question(
            self, "Unmount All",
            "Are you sure you want to unmount all network shares?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            unmounted_count = 0
            for share_name, config in self.shares.items():
                if self.is_mounted(config['mount_point']):
                    worker = MountWorker("unmount", config)
                    success, _ = worker.unmount_share()
                    if success:
                        unmounted_count += 1
                        
            self.status_label.setText(f"Unmounted {unmounted_count} shares")
            self.check_mount_status()
            
    def get_mounted_shares(self) -> List[Tuple[str, str]]:
        """Get list of currently mounted shares (name, mount_point)"""
        mounted = []
        for name, config in self.shares.items():
            if self.is_mounted(config['mount_point']):
                mounted.append((name, config['mount_point']))
        return mounted
        
    def export_config(self, export_path: str) -> bool:
        """Export network configuration"""
        try:
            config_data = {
                'shares': self.shares,
                'exported_at': os.path.basename(__file__)
            }
            with open(export_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception:
            return False
            
    def import_config(self, import_path: str) -> bool:
        """Import network configuration"""
        try:
            with open(import_path, 'r') as f:
                config_data = json.load(f)
                imported_shares = config_data.get('shares', {})
                
            # Merge with existing shares
            self.shares.update(imported_shares)
            self.save_shares()
            self.load_shares_list()
            self.shares_changed.emit()
            return True
        except Exception:
            return False