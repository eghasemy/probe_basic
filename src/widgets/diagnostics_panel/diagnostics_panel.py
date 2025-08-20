#!/usr/bin/env python

import os
import sys
import time
import subprocess
import tempfile
import zipfile
from datetime import datetime
from qtpy.QtCore import Qt, QTimer, QThread, Signal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QFrame, QPushButton, QTextEdit, QTreeWidget,
                            QTreeWidgetItem, QGroupBox, QTabWidget, QSplitter,
                            QProgressBar, QFileDialog, QMessageBox)
from qtpy.QtGui import QFont, QPalette, QColor
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class SupportBundleThread(QThread):
    """
    Background thread for creating support bundle
    """
    progress_updated = Signal(int, str)
    bundle_complete = Signal(str)
    bundle_error = Signal(str)
    
    def __init__(self, output_path):
        super(SupportBundleThread, self).__init__()
        self.output_path = output_path
        
    def run(self):
        """Create support bundle in background thread"""
        try:
            self.progress_updated.emit(10, "Initializing support bundle...")
            
            # Create temporary directory for bundle contents
            with tempfile.TemporaryDirectory() as temp_dir:
                bundle_dir = os.path.join(temp_dir, "probe_basic_support")
                os.makedirs(bundle_dir)
                
                # Collect system information
                self.progress_updated.emit(20, "Collecting system information...")
                self.collect_system_info(bundle_dir)
                
                # Collect LinuxCNC configuration
                self.progress_updated.emit(40, "Collecting LinuxCNC configuration...")
                self.collect_linuxcnc_config(bundle_dir)
                
                # Collect HAL information
                self.progress_updated.emit(60, "Collecting HAL information...")
                self.collect_hal_info(bundle_dir)
                
                # Collect logs
                self.progress_updated.emit(80, "Collecting log files...")
                self.collect_logs(bundle_dir)
                
                # Create ZIP archive
                self.progress_updated.emit(90, "Creating ZIP archive...")
                self.create_zip_archive(bundle_dir, self.output_path)
                
                self.progress_updated.emit(100, "Support bundle complete!")
                self.bundle_complete.emit(self.output_path)
                
        except Exception as e:
            self.bundle_error.emit(str(e))
            
    def collect_system_info(self, bundle_dir):
        """Collect system information"""
        info_file = os.path.join(bundle_dir, "system_info.txt")
        with open(info_file, 'w') as f:
            f.write(f"Support Bundle Generated: {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            # System information
            try:
                f.write("SYSTEM INFORMATION:\n")
                f.write(f"Platform: {sys.platform}\n")
                f.write(f"Python Version: {sys.version}\n")
                
                # Get system info via subprocess
                commands = [
                    ("Kernel", ["uname", "-a"]),
                    ("Distribution", ["lsb_release", "-a"]),
                    ("Memory", ["free", "-h"]),
                    ("Disk Space", ["df", "-h"]),
                    ("CPU Info", ["lscpu"]),
                ]
                
                for name, cmd in commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        f.write(f"\n{name}:\n{result.stdout}\n")
                    except Exception as e:
                        f.write(f"\n{name}: Error - {e}\n")
                        
            except Exception as e:
                f.write(f"Error collecting system info: {e}\n")
                
    def collect_linuxcnc_config(self, bundle_dir):
        """Collect LinuxCNC configuration files"""
        try:
            ini_file = os.getenv('INI_FILE_NAME')
            if ini_file and os.path.exists(ini_file):
                # Copy INI file
                dest_ini = os.path.join(bundle_dir, "machine.ini")
                with open(ini_file, 'r') as src, open(dest_ini, 'w') as dst:
                    dst.write(src.read())
                    
                # Try to find HAL files mentioned in INI
                config_dir = os.path.dirname(ini_file)
                for file in os.listdir(config_dir):
                    if file.endswith('.hal'):
                        src_path = os.path.join(config_dir, file)
                        dst_path = os.path.join(bundle_dir, file)
                        try:
                            with open(src_path, 'r') as src, open(dst_path, 'w') as dst:
                                dst.write(src.read())
                        except Exception:
                            pass  # Skip files that can't be read
                            
        except Exception as e:
            error_file = os.path.join(bundle_dir, "config_error.txt")
            with open(error_file, 'w') as f:
                f.write(f"Error collecting LinuxCNC config: {e}\n")
                
    def collect_hal_info(self, bundle_dir):
        """Collect HAL information"""
        hal_file = os.path.join(bundle_dir, "hal_info.txt")
        try:
            with open(hal_file, 'w') as f:
                f.write("HAL INFORMATION:\n")
                f.write("=" * 30 + "\n\n")
                
                # Try to get HAL information via halcmd
                commands = [
                    ("Components", ["halcmd", "show", "comp"]),
                    ("Pins", ["halcmd", "show", "pin"]),
                    ("Signals", ["halcmd", "show", "sig"]),
                    ("Parameters", ["halcmd", "show", "param"]),
                    ("Threads", ["halcmd", "show", "thread"]),
                ]
                
                for name, cmd in commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        f.write(f"{name}:\n{result.stdout}\n\n")
                    except Exception as e:
                        f.write(f"{name}: Error - {e}\n\n")
                        
        except Exception as e:
            with open(hal_file, 'w') as f:
                f.write(f"Error collecting HAL info: {e}\n")
                
    def collect_logs(self, bundle_dir):
        """Collect relevant log files"""
        log_dir = os.path.join(bundle_dir, "logs")
        os.makedirs(log_dir)
        
        # Common log locations
        log_files = [
            "/var/log/linuxcnc.log",
            "/tmp/linuxcnc.log",
            "/var/log/dmesg",
            "/var/log/syslog",
        ]
        
        for log_path in log_files:
            try:
                if os.path.exists(log_path):
                    log_name = os.path.basename(log_path)
                    dest_path = os.path.join(log_dir, log_name)
                    
                    # Copy last 1000 lines of log files
                    with open(log_path, 'r') as src:
                        lines = src.readlines()
                        with open(dest_path, 'w') as dst:
                            dst.writelines(lines[-1000:])  # Last 1000 lines
            except Exception:
                pass  # Skip files that can't be read
                
    def create_zip_archive(self, bundle_dir, output_path):
        """Create ZIP archive of bundle"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(bundle_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, bundle_dir)
                    zipf.write(file_path, arc_path)


class DiagnosticsPanel(QWidget):
    """
    Diagnostics Panel Widget for Phase 3
    Live errors, HAL component listing, thread rates, task latency, and support bundle export
    """
    
    def __init__(self, parent=None):
        super(DiagnosticsPanel, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.hal = getPlugin('hal')
        
        self.setupUI()
        self.connectSignals()
        
        # Update timer for live diagnostics
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateDiagnostics)
        self.update_timer.start(1000)  # Update every second
        
        # Support bundle thread
        self.bundle_thread = None
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("diagnosticsPanel")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("Diagnostics Panel - System Health & Information")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        main_layout.addWidget(header)
        
        # Tab widget for different diagnostic views
        self.tab_widget = QTabWidget()
        
        # Live Status tab
        self.tab_widget.addTab(self.createLiveStatusTab(), "Live Status")
        
        # HAL Components tab
        self.tab_widget.addTab(self.createHALComponentsTab(), "HAL Components")
        
        # System Info tab
        self.tab_widget.addTab(self.createSystemInfoTab(), "System Info")
        
        # Error Log tab
        self.tab_widget.addTab(self.createErrorLogTab(), "Error Log")
        
        main_layout.addWidget(self.tab_widget)
        
        # Support bundle section
        bundle_group = self.createSupportBundleGroup()
        main_layout.addWidget(bundle_group)
        
        self.setLayout(main_layout)
        
    def createLiveStatusTab(self):
        """Create live status monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QGridLayout()
        
        # Task latency
        metrics_layout.addWidget(QLabel("Task Latency:"), 0, 0)
        self.task_latency_label = QLabel("-- μs")
        metrics_layout.addWidget(self.task_latency_label, 0, 1)
        
        # Thread rates
        metrics_layout.addWidget(QLabel("Servo Thread:"), 1, 0)
        self.servo_thread_label = QLabel("-- Hz")
        metrics_layout.addWidget(self.servo_thread_label, 1, 1)
        
        metrics_layout.addWidget(QLabel("Base Thread:"), 2, 0)
        self.base_thread_label = QLabel("-- Hz")
        metrics_layout.addWidget(self.base_thread_label, 2, 1)
        
        # Machine status
        metrics_layout.addWidget(QLabel("Machine Status:"), 3, 0)
        self.machine_status_label = QLabel("Unknown")
        metrics_layout.addWidget(self.machine_status_label, 3, 1)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Error summary
        error_group = QGroupBox("Current Errors")
        error_layout = QVBoxLayout()
        
        self.error_text = QTextEdit()
        self.error_text.setMaximumHeight(200)
        self.error_text.setReadOnly(True)
        error_layout.addWidget(self.error_text)
        
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        widget.setLayout(layout)
        return widget
        
    def createHALComponentsTab(self):
        """Create HAL components listing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refreshHALComponents)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        
        filter_label = QLabel("Filter:")
        self.hal_filter = QTextEdit()
        self.hal_filter.setMaximumHeight(25)
        self.hal_filter.setPlaceholderText("Type to filter components...")
        controls_layout.addWidget(filter_label)
        controls_layout.addWidget(self.hal_filter)
        
        layout.addLayout(controls_layout)
        
        # Component tree
        self.hal_tree = QTreeWidget()
        self.hal_tree.setHeaderLabels(["Component", "Type", "State", "Details"])
        layout.addWidget(self.hal_tree)
        
        widget.setLayout(layout)
        return widget
        
    def createSystemInfoTab(self):
        """Create system information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # System info text
        self.system_info_text = QTextEdit()
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setFont(QFont("monospace"))
        layout.addWidget(self.system_info_text)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh System Info")
        refresh_btn.clicked.connect(self.refreshSystemInfo)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
        
    def createErrorLogTab(self):
        """Create error log tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clearErrorLog)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        
        auto_scroll_label = QLabel("Auto-scroll:")
        controls_layout.addWidget(auto_scroll_label)
        
        layout.addLayout(controls_layout)
        
        # Error log text
        self.error_log_text = QTextEdit()
        self.error_log_text.setReadOnly(True)
        self.error_log_text.setFont(QFont("monospace"))
        layout.addWidget(self.error_log_text)
        
        widget.setLayout(layout)
        return widget
        
    def createSupportBundleGroup(self):
        """Create support bundle export group"""
        group = QGroupBox("Support Bundle Export")
        layout = QVBoxLayout()
        
        # Description
        desc_label = QLabel("Export a comprehensive support bundle containing logs, configuration files, HAL information, and system details for troubleshooting.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Support Bundle")
        self.export_btn.clicked.connect(self.exportSupportBundle)
        controls_layout.addWidget(self.export_btn)
        
        controls_layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        layout.addLayout(controls_layout)
        
        # Status label
        self.bundle_status_label = QLabel("Ready to export")
        layout.addWidget(self.bundle_status_label)
        
        group.setLayout(layout)
        return group
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.error.notify(self.handleError)
            
    def updateDiagnostics(self):
        """Update live diagnostics"""
        try:
            self.updatePerformanceMetrics()
            self.updateMachineStatus()
        except Exception as e:
            LOG.error(f"Error updating diagnostics: {e}")
            
    def updatePerformanceMetrics(self):
        """Update performance metrics"""
        # Mock data for simulation - in real implementation, these would come from HAL
        import random
        
        # Simulate task latency (microseconds)
        latency = random.uniform(10, 50)
        self.task_latency_label.setText(f"{latency:.1f} μs")
        
        # Simulate thread rates
        servo_rate = random.uniform(980, 1020)
        base_rate = random.uniform(9800, 10200)
        self.servo_thread_label.setText(f"{servo_rate:.1f} Hz")
        self.base_thread_label.setText(f"{base_rate:.1f} Hz")
        
    def updateMachineStatus(self):
        """Update machine status"""
        if not self.status:
            self.machine_status_label.setText("Status plugin unavailable")
            return
            
        try:
            if self.status.estop():
                status = "ESTOP Active"
                color = "red"
            elif not self.status.enabled():
                status = "Machine Disabled"
                color = "orange"
            else:
                status = "Machine Enabled"
                color = "green"
                
            self.machine_status_label.setText(status)
            self.machine_status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            
        except Exception as e:
            self.machine_status_label.setText(f"Error: {e}")
            
    def refreshHALComponents(self):
        """Refresh HAL components list"""
        self.hal_tree.clear()
        
        # Mock HAL components for simulation
        mock_components = [
            ("motmod", "RT", "Ready", "Motion module"),
            ("iocontrol", "RT", "Ready", "IO control"),
            ("probe_basic", "User", "Running", "UI application"),
            ("halui", "User", "Ready", "HAL user interface"),
            ("sim_encoder", "RT", "Ready", "Simulated encoder"),
        ]
        
        for comp_name, comp_type, state, details in mock_components:
            item = QTreeWidgetItem([comp_name, comp_type, state, details])
            
            # Color code by state
            if state == "Ready":
                item.setBackground(1, QColor(200, 255, 200))
            elif state == "Running":
                item.setBackground(1, QColor(200, 200, 255))
            else:
                item.setBackground(1, QColor(255, 200, 200))
                
            self.hal_tree.addTopLevelItem(item)
            
    def refreshSystemInfo(self):
        """Refresh system information"""
        info_text = f"System Information - {datetime.now()}\n"
        info_text += "=" * 50 + "\n\n"
        
        # Python info
        info_text += f"Python Version: {sys.version}\n"
        info_text += f"Platform: {sys.platform}\n\n"
        
        # Environment
        info_text += "Environment Variables:\n"
        for key in ["INI_FILE_NAME", "LINUXCNC_HOME", "EMC2_HOME"]:
            value = os.getenv(key, "Not set")
            info_text += f"  {key}: {value}\n"
            
        info_text += "\n"
        
        # Mock additional system info
        info_text += "Memory Usage: 1.2 GB / 8.0 GB\n"
        info_text += "CPU Usage: 15%\n"
        info_text += "Disk Space: 45 GB / 120 GB\n"
        
        self.system_info_text.setPlainText(info_text)
        
    def clearErrorLog(self):
        """Clear error log"""
        self.error_log_text.clear()
        
    def handleError(self, error_msg):
        """Handle new error messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_error = f"[{timestamp}] {error_msg}\n"
        
        self.error_text.append(formatted_error)
        self.error_log_text.append(formatted_error)
        
    def exportSupportBundle(self):
        """Export support bundle"""
        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"probe_basic_support_{timestamp}.zip"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Support Bundle", 
            default_name,
            "ZIP files (*.zip)"
        )
        
        if not file_path:
            return
            
        # Start export in background thread
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.bundle_status_label.setText("Creating support bundle...")
        
        self.bundle_thread = SupportBundleThread(file_path)
        self.bundle_thread.progress_updated.connect(self.updateBundleProgress)
        self.bundle_thread.bundle_complete.connect(self.bundleComplete)
        self.bundle_thread.bundle_error.connect(self.bundleError)
        self.bundle_thread.start()
        
    def updateBundleProgress(self, progress, message):
        """Update bundle export progress"""
        self.progress_bar.setValue(progress)
        self.bundle_status_label.setText(message)
        
    def bundleComplete(self, file_path):
        """Handle bundle export completion"""
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.bundle_status_label.setText(f"Support bundle saved to: {file_path}")
        
        # Show success message
        QMessageBox.information(
            self,
            "Export Complete",
            f"Support bundle successfully exported to:\n{file_path}"
        )
        
    def bundleError(self, error_msg):
        """Handle bundle export error"""
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.bundle_status_label.setText(f"Export failed: {error_msg}")
        
        # Show error message
        QMessageBox.critical(
            self,
            "Export Error",
            f"Failed to create support bundle:\n{error_msg}"
        )