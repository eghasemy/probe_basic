#!/usr/bin/env python

import os
from datetime import datetime
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton, QFrame
from qtpy.QtGui import QFont
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class AlarmEntry(QFrame):
    """Individual alarm entry widget"""
    
    acknowledged = Signal(str)  # Signal emitted when alarm is acknowledged
    
    def __init__(self, alarm_id, message, timestamp, severity="warning", parent=None):
        super(AlarmEntry, self).__init__(parent)
        
        self.alarm_id = alarm_id
        self.message = message
        self.timestamp = timestamp
        self.severity = severity
        self.is_acknowledged = False
        
        self.setupUI()
        
    def setupUI(self):
        """Set up the alarm entry UI"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Severity indicator
        severity_label = QLabel("●")
        severity_label.setMinimumSize(20, 20)
        severity_label.setAlignment(Qt.AlignCenter)
        
        # Set color based on severity
        color_map = {
            "critical": "#FF0000",
            "error": "#FF4444", 
            "warning": "#FF8800",
            "info": "#0088FF"
        }
        color = color_map.get(self.severity, "#888888")
        severity_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        
        # Message and timestamp
        info_layout = QVBoxLayout()
        
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        time_label = QLabel(self.timestamp.strftime("%H:%M:%S"))
        time_label.setStyleSheet("color: #666; font-size: 10px;")
        
        info_layout.addWidget(message_label)
        info_layout.addWidget(time_label)
        
        # Acknowledge button
        self.ack_button = QPushButton("ACK")
        self.ack_button.setMinimumSize(60, 30)
        self.ack_button.setMaximumSize(80, 35)
        self.ack_button.clicked.connect(self.acknowledge)
        
        self.ack_button.setStyleSheet("""
            QPushButton {
                background-color: #FF8800;
                border: 1px solid #333;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #FF9900;
            }
            QPushButton:pressed {
                background-color: #FF7700;
            }
        """)
        
        layout.addWidget(severity_label)
        layout.addLayout(info_layout, 1)  # Stretch to fill
        layout.addWidget(self.ack_button)
        
        self.setLayout(layout)
        
        # Initial styling
        self.updateAppearance()
        
    def acknowledge(self):
        """Acknowledge this alarm"""
        self.is_acknowledged = True
        self.ack_button.setText("✓")
        self.ack_button.setEnabled(False)
        self.ack_button.setStyleSheet("""
            QPushButton {
                background-color: #44AA44;
                border: 1px solid #333;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.updateAppearance()
        self.acknowledged.emit(self.alarm_id)
        
    def updateAppearance(self):
        """Update appearance based on acknowledgment status"""
        if self.is_acknowledged:
            self.setStyleSheet("""
                AlarmEntry {
                    background-color: #333;
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("""
                AlarmEntry {
                    background-color: #444;
                    border: 2px solid #FF8800;
                }
            """)


class AlarmsPanel(QWidget):
    """
    Alarms Panel Widget
    Displays sticky alarm entries with acknowledge functionality
    Based on Phase 1 requirements
    """
    
    def __init__(self, parent=None):
        super(AlarmsPanel, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.alarm_entries = {}  # Dictionary to track alarm entries
        self.alarm_counter = 0   # Counter for unique alarm IDs
        
        self.setupUI()
        self.connectSignals()
        
        # Update timer for checking alarms
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.checkForAlarms)
        self.update_timer.start(500)  # Check every 500ms
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("alarmsPanel")
        self.setMinimumSize(400, 150)
        self.setMaximumSize(800, 300)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("ALARMS")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF8800;")
        
        # Clear all button
        self.clear_all_button = QPushButton("CLEAR ALL")
        self.clear_all_button.setMaximumSize(100, 30)
        self.clear_all_button.clicked.connect(self.clearAllAlarms)
        self.clear_all_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                border: 1px solid #333;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.clear_all_button)
        
        # Scrollable alarms area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for alarm entries
        self.alarms_container = QWidget()
        self.alarms_layout = QVBoxLayout()
        self.alarms_layout.setContentsMargins(0, 0, 0, 0)
        self.alarms_layout.setSpacing(2)
        
        # No alarms message
        self.no_alarms_label = QLabel("No active alarms")
        self.no_alarms_label.setAlignment(Qt.AlignCenter)
        self.no_alarms_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
        self.alarms_layout.addWidget(self.no_alarms_label)
        
        self.alarms_layout.addStretch()
        self.alarms_container.setLayout(self.alarms_layout)
        self.scroll_area.setWidget(self.alarms_container)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            # Connect to error and status signals
            self.status.task_state.notify(self.checkForAlarms)
            
    def addAlarm(self, message, severity="warning"):
        """Add a new alarm entry"""
        alarm_id = f"alarm_{self.alarm_counter}"
        self.alarm_counter += 1
        
        timestamp = datetime.now()
        alarm_entry = AlarmEntry(alarm_id, message, timestamp, severity)
        alarm_entry.acknowledged.connect(self.onAlarmAcknowledged)
        
        # Hide no alarms message
        self.no_alarms_label.hide()
        
        # Add to layout (insert at top, above stretch)
        self.alarms_layout.insertWidget(0, alarm_entry)
        
        # Store reference
        self.alarm_entries[alarm_id] = alarm_entry
        
        LOG.info(f"Added alarm: {message}")
        
    def onAlarmAcknowledged(self, alarm_id):
        """Handle alarm acknowledgment"""
        LOG.info(f"Alarm acknowledged: {alarm_id}")
        
    def clearAllAlarms(self):
        """Clear all alarm entries"""
        for alarm_id, alarm_entry in self.alarm_entries.items():
            self.alarms_layout.removeWidget(alarm_entry)
            alarm_entry.deleteLater()
            
        self.alarm_entries.clear()
        
        # Show no alarms message
        self.no_alarms_label.show()
        
        LOG.info("All alarms cleared")
        
    def checkForAlarms(self):
        """Check for new alarms from LinuxCNC status"""
        if not self.status:
            return
            
        try:
            # Check for error conditions and generate alarms
            # This is a simplified implementation - real alarm monitoring would be more comprehensive
            
            # Check if machine is in estop
            if self.status.estop():
                if "estop_alarm" not in self.alarm_entries:
                    self.addAlarm("Emergency Stop is Active", "critical")
                    self.alarm_entries["estop_alarm"] = None  # Mark as added
            else:
                if "estop_alarm" in self.alarm_entries and self.alarm_entries["estop_alarm"] is None:
                    del self.alarm_entries["estop_alarm"]
                    
            # Check for limit switch trips
            limits = self.status.limit()
            if any(limits):
                if "limit_alarm" not in self.alarm_entries:
                    self.addAlarm("Limit Switch Triggered", "error")
                    self.alarm_entries["limit_alarm"] = None
            else:
                if "limit_alarm" in self.alarm_entries and self.alarm_entries["limit_alarm"] is None:
                    del self.alarm_entries["limit_alarm"]
            
        except Exception as e:
            LOG.error(f"Error checking for alarms: {e}")
            
    def simulateAlarm(self, message="Test alarm", severity="warning"):
        """Simulate an alarm for testing purposes"""
        self.addAlarm(message, severity)