#!/usr/bin/env python
"""
Phase 9 Demo - Settings, Profiles & Network
Phase 9 - Settings, Profiles & Network

Demonstrates the Phase 9 widgets functionality including:
- Profile Manager: Create, clone, switch, delete profiles
- Settings Manager: Units, UI scale, theme, touchscreen mode
- Network Manager: SMB/NFS mount management
- Backup/Restore: Profile and settings backup with factory reset
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                                QVBoxLayout, QWidget, QLabel, QMessageBox,
                                QHBoxLayout, QPushButton, QSplitter)
    from PyQt5.QtCore import pyqtSlot, QTimer
    from PyQt5.QtGui import QFont
    PyQt5_available = True
except ImportError:
    try:
        from PyQt4.QtGui import (QApplication, QMainWindow, QTabWidget,
                                QVBoxLayout, QWidget, QLabel, QMessageBox,
                                QHBoxLayout, QPushButton, QFont)
        from PyQt4.QtCore import pyqtSlot, QTimer
        PyQt5_available = False
        
        # Create QSplitter stub for PyQt4
        class QSplitter(QWidget):
            def __init__(self, orientation=None):
                super(QSplitter, self).__init__()
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
            def addWidget(self, widget):
                self.layout.addWidget(widget)
    except ImportError:
        print("Error: Neither PyQt5 nor PyQt4 is available")
        print("This demo requires PyQt5 or PyQt4 to run")
        sys.exit(1)

# Import Phase 9 widgets
try:
    from widgets.profile_manager.profile_manager import ProfileManager
    from widgets.settings_manager.settings_manager import SettingsManager  
    from widgets.network_manager.network_manager import NetworkManager
    from widgets.backup_restore.backup_restore import BackupRestore
    widgets_available = True
except ImportError as e:
    print(f"Warning: Could not import Phase 9 widgets: {e}")
    widgets_available = False


class Phase9Demo(QMainWindow):
    """Main demo window for Phase 9 functionality"""
    
    def __init__(self):
        super(Phase9Demo, self).__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Phase 9 Demo - Settings, Profiles & Network")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Phase 9 - Settings, Profiles & Network Demo")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("padding: 16px; background: #f0f0f0; border-radius: 8px; margin-bottom: 16px;")
        layout.addWidget(header)
        
        # Info panel
        info_text = """
This demo showcases the Phase 9 functionality:

• Profile Manager: Create, clone, switch, and delete LinuxCNC machine profiles
• Settings Manager: Configure units, UI scale, theme, and touchscreen options  
• Network Manager: Manage SMB/NFS network share mounting with credentials
• Backup/Restore: Complete backup and restore system with factory reset capability

Each tab demonstrates a different aspect of the Phase 9 implementation.
        """
        
        info_label = QLabel(info_text.strip())
        info_label.setStyleSheet("padding: 12px; background: #e8f4f8; border-radius: 6px; margin-bottom: 16px;")
        layout.addWidget(info_label)
        
        if widgets_available:
            # Create tab widget with Phase 9 widgets
            self.tab_widget = QTabWidget()
            
            # Profile Manager tab
            self.profile_manager = ProfileManager()
            self.profile_manager.profile_switched.connect(self.on_profile_switched)
            self.profile_manager.profile_created.connect(self.on_profile_created)
            self.profile_manager.profile_deleted.connect(self.on_profile_deleted)
            self.tab_widget.addTab(self.profile_manager, "Profile Manager")
            
            # Settings Manager tab
            self.settings_manager = SettingsManager()
            self.settings_manager.settings_changed.connect(self.on_setting_changed)
            self.settings_manager.theme_changed.connect(self.on_theme_changed)
            self.settings_manager.units_changed.connect(self.on_units_changed)
            self.tab_widget.addTab(self.settings_manager, "Settings Manager")
            
            # Network Manager tab
            self.network_manager = NetworkManager()
            self.network_manager.share_mounted.connect(self.on_share_mounted)
            self.network_manager.share_unmounted.connect(self.on_share_unmounted)
            self.network_manager.shares_changed.connect(self.on_shares_changed)
            self.tab_widget.addTab(self.network_manager, "Network Manager")
            
            # Backup/Restore tab
            self.backup_restore = BackupRestore()
            self.backup_restore.backup_completed.connect(self.on_backup_completed)
            self.backup_restore.restore_completed.connect(self.on_restore_completed)
            self.backup_restore.factory_reset_completed.connect(self.on_factory_reset_completed)
            self.tab_widget.addTab(self.backup_restore, "Backup & Restore")
            
            layout.addWidget(self.tab_widget)
            
            # Demo controls
            demo_layout = QHBoxLayout()
            
            self.demo_profile_btn = QPushButton("Create Demo Profile")
            self.demo_profile_btn.clicked.connect(self.create_demo_profile)
            demo_layout.addWidget(self.demo_profile_btn)
            
            self.demo_settings_btn = QPushButton("Apply Demo Settings")
            self.demo_settings_btn.clicked.connect(self.apply_demo_settings)
            demo_layout.addWidget(self.demo_settings_btn)
            
            self.demo_share_btn = QPushButton("Add Demo Network Share")
            self.demo_share_btn.clicked.connect(self.add_demo_share)
            demo_layout.addWidget(self.demo_share_btn)
            
            demo_layout.addStretch()
            
            self.demo_backup_btn = QPushButton("Create Demo Backup")
            self.demo_backup_btn.clicked.connect(self.create_demo_backup)
            demo_layout.addWidget(self.demo_backup_btn)
            
            layout.addLayout(demo_layout)
            
        else:
            # Show error message if widgets not available
            error_label = QLabel(
                "❌ Phase 9 widgets could not be imported.\n\n"
                "This may be due to missing Qt dependencies.\n"
                "The widgets are implemented and ready for integration."
            )
            error_label.setStyleSheet("padding: 20px; background: #ffebee; border-radius: 8px; color: #c62828;")
            layout.addWidget(error_label)
            
        # Status bar
        self.status_label = QLabel("Ready - Phase 9 Demo Loaded")
        self.status_label.setStyleSheet("padding: 8px; background: #f5f5f5; border-top: 1px solid #ddd;")
        layout.addWidget(self.status_label)
        
        central_widget.setLayout(layout)
        
    # Profile Manager signal handlers
    @pyqtSlot(str)
    def on_profile_switched(self, profile_name):
        """Handle profile switch"""
        self.status_label.setText(f"Profile switched to: {profile_name}")
        QMessageBox.information(self, "Profile Switched", 
                               f"Successfully switched to profile: {profile_name}")
        
    @pyqtSlot(str) 
    def on_profile_created(self, profile_name):
        """Handle profile creation"""
        self.status_label.setText(f"Profile created: {profile_name}")
        
    @pyqtSlot(str)
    def on_profile_deleted(self, profile_name):
        """Handle profile deletion"""
        self.status_label.setText(f"Profile deleted: {profile_name}")
        
    # Settings Manager signal handlers
    @pyqtSlot(str, object)
    def on_setting_changed(self, setting_name, value):
        """Handle setting change"""
        self.status_label.setText(f"Setting changed: {setting_name} = {value}")
        
    @pyqtSlot(str)
    def on_theme_changed(self, theme_name):
        """Handle theme change"""
        self.status_label.setText(f"Theme changed to: {theme_name}")
        
    @pyqtSlot(str)
    def on_units_changed(self, units):
        """Handle units change"""
        self.status_label.setText(f"Units changed to: {units}")
        
    # Network Manager signal handlers
    @pyqtSlot(str, str)
    def on_share_mounted(self, name, mount_point):
        """Handle share mounted"""
        self.status_label.setText(f"Share mounted: {name} at {mount_point}")
        QMessageBox.information(self, "Share Mounted",
                               f"Network share '{name}' mounted successfully at:\n{mount_point}")
        
    @pyqtSlot(str)
    def on_share_unmounted(self, name):
        """Handle share unmounted"""
        self.status_label.setText(f"Share unmounted: {name}")
        
    @pyqtSlot()
    def on_shares_changed(self):
        """Handle shares configuration change"""
        self.status_label.setText("Network shares configuration updated")
        
    # Backup/Restore signal handlers
    @pyqtSlot(str)
    def on_backup_completed(self, backup_path):
        """Handle backup completion"""
        self.status_label.setText(f"Backup completed: {backup_path}")
        QMessageBox.information(self, "Backup Completed",
                               f"Backup created successfully:\n{backup_path}")
        
    @pyqtSlot()
    def on_restore_completed(self):
        """Handle restore completion"""
        self.status_label.setText("Restore completed successfully")
        QMessageBox.information(self, "Restore Completed",
                               "Backup restored successfully!")
        
    @pyqtSlot()
    def on_factory_reset_completed(self):
        """Handle factory reset completion"""
        self.status_label.setText("Factory reset completed")
        QMessageBox.information(self, "Factory Reset",
                               "Factory reset completed successfully!")
        
    # Demo functions
    def create_demo_profile(self):
        """Create a demo profile"""
        if not widgets_available:
            return
            
        # Simulate profile creation
        demo_data = {
            'name': f'Demo_Profile_{QTimer().remainingTime() % 1000}',
            'description': 'Demo profile created for testing',
            'template': 'Basic Sim (3-axis mill)',
            'set_default': False,
            'switch_after_create': False
        }
        
        try:
            self.profile_manager.create_profile_bundle(demo_data)
            self.profile_manager.load_profiles()
            self.status_label.setText(f"Demo profile created: {demo_data['name']}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create demo profile:\n{e}")
            
    def apply_demo_settings(self):
        """Apply demo settings"""
        if not widgets_available:
            return
            
        # Apply some demo settings
        try:
            self.settings_manager.set_setting('units', 'Metric (mm)')
            self.settings_manager.set_setting('scale_factor', 125)
            self.settings_manager.set_setting('theme', 'High Contrast')
            self.settings_manager.load_current_settings()
            self.status_label.setText("Demo settings applied")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to apply demo settings:\n{e}")
            
    def add_demo_share(self):
        """Add demo network share"""
        if not widgets_available:
            return
            
        # Add a demo share configuration
        demo_share = {
            'name': 'Demo_Share',
            'type': 'SMB',
            'server': '192.168.1.100',
            'share': 'shared_files',
            'mount_point': str(Path.home() / 'mnt' / 'demo_share'),
            'auto_mount': True,
            'readonly': False
        }
        
        try:
            self.network_manager.shares['Demo_Share'] = demo_share
            self.network_manager.save_shares()
            self.network_manager.load_shares_list()
            self.status_label.setText("Demo network share added")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add demo share:\n{e}")
            
    def create_demo_backup(self):
        """Create demo backup"""
        if not widgets_available:
            return
            
        # Set up demo backup
        import tempfile
        from datetime import datetime
        
        demo_backup_path = Path(tempfile.gettempdir()) / f"pb_touch_demo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        try:
            self.backup_restore.backup_path_edit.setText(str(demo_backup_path))
            self.backup_restore.backup_profiles_check.setChecked(True)
            self.backup_restore.backup_settings_check.setChecked(True) 
            self.backup_restore.backup_network_check.setChecked(True)
            self.status_label.setText("Demo backup configured - click 'Create Backup' to proceed")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to setup demo backup:\n{e}")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Phase 9 Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Probe Basic")
    
    # Create and show main window
    demo = Phase9Demo()
    demo.show()
    
    # Show startup message
    QTimer.singleShot(500, lambda: QMessageBox.information(
        demo, "Phase 9 Demo",
        "Welcome to the Phase 9 Demo!\n\n"
        "This demonstrates the Settings, Profiles & Network functionality.\n\n"
        "• Profile Manager: Manage LinuxCNC machine configurations\n"
        "• Settings Manager: Configure application preferences\n" 
        "• Network Manager: Mount SMB/NFS network shares\n"
        "• Backup/Restore: Complete backup and restore system\n\n"
        "Use the demo buttons to see the functionality in action."
    ))
    
    return app.exec_()


if __name__ == "__main__":
    print("Phase 9 Demo - Settings, Profiles & Network")
    print("=" * 50)
    print()
    
    if not widgets_available:
        print("Warning: Phase 9 widgets could not be imported")
        print("This may be due to Qt dependencies not being available")
        print("The demo will show the UI structure but functionality will be limited")
        print()
    
    sys.exit(main())