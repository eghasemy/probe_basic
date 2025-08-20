#!/usr/bin/env python

import os
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QPushButton, QFrame, QDialog, QMessageBox,
                            QDialogButtonBox, QCheckBox)
from qtpy.QtGui import QFont
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class HomingBadge(QFrame):
    """Individual axis homing badge widget"""
    
    homeRequested = Signal(str)  # Signal emitted when home button is clicked
    
    def __init__(self, axis_name, axis_index, parent=None):
        super(HomingBadge, self).__init__(parent)
        
        self.axis_name = axis_name
        self.axis_index = axis_index
        self.is_homed = False
        
        self.setupUI()
        
    def setupUI(self):
        """Set up the badge UI"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setMinimumSize(80, 60)
        self.setMaximumSize(120, 80)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Axis label
        self.axis_label = QLabel(f"{self.axis_name}")
        self.axis_label.setAlignment(Qt.AlignCenter)
        self.axis_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.axis_label)
        
        # Status label
        self.status_label = QLabel("NOT HOMED")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 8))
        layout.addWidget(self.status_label)
        
        # Home button
        self.home_button = QPushButton("HOME")
        self.home_button.setFont(QFont("Arial", 8))
        self.home_button.clicked.connect(self.onHomeClicked)
        layout.addWidget(self.home_button)
        
        self.setLayout(layout)
        self.updateStatus(False)
        
    def updateStatus(self, is_homed):
        """Update the badge status"""
        self.is_homed = is_homed
        
        if is_homed:
            # Homed state - green
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d5a2d;
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4CAF50;
                    border: 1px solid #45a049;
                    border-radius: 4px;
                    color: white;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.status_label.setText("HOMED")
            self.home_button.setText("REHOME")
        else:
            # Not homed state - red
            self.setStyleSheet("""
                QFrame {
                    background-color: #5a2d2d;
                    border: 2px solid #f44336;
                    border-radius: 8px;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #f44336;
                    border: 1px solid #da190b;
                    border-radius: 4px;
                    color: white;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.status_label.setText("NOT HOMED")
            self.home_button.setText("HOME")
            
    def onHomeClicked(self):
        """Handle home button click"""
        self.homeRequested.emit(self.axis_name)

class HomingSequenceDialog(QDialog):
    """Dialog for guided homing sequence"""
    
    def __init__(self, unhomed_axes, parent=None):
        super(HomingSequenceDialog, self).__init__(parent)
        
        self.unhomed_axes = unhomed_axes
        self.homing_order = ['Z', 'X', 'Y']  # Default safe order: Z first, then X, Y
        
        self.setupUI()
        
    def setupUI(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Homing Required")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Warning message
        warning_label = QLabel("⚠️ Some axes are not homed!")
        warning_label.setFont(QFont("Arial", 14, QFont.Bold))
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setStyleSheet("color: #ff6b35; padding: 10px;")
        layout.addWidget(warning_label)
        
        # Information
        info_label = QLabel("Homing is required before jogging or running programs.\n"
                           "The recommended homing order is shown below:")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Homing sequence
        sequence_frame = QFrame()
        sequence_frame.setFrameStyle(QFrame.Box)
        sequence_layout = QVBoxLayout()
        
        sequence_title = QLabel("Recommended Homing Sequence:")
        sequence_title.setFont(QFont("Arial", 12, QFont.Bold))
        sequence_layout.addWidget(sequence_title)
        
        for i, axis in enumerate(self.homing_order):
            if axis in self.unhomed_axes:
                step_label = QLabel(f"{i+1}. Home {axis} axis first")
                step_label.setStyleSheet("padding: 5px; margin: 2px;")
                sequence_layout.addWidget(step_label)
        
        sequence_frame.setLayout(sequence_layout)
        layout.addWidget(sequence_frame)
        
        # Safety reminder
        safety_label = QLabel("⚠️ Safety Reminder: Ensure workspace is clear before homing")
        safety_label.setStyleSheet("color: #ff6b35; font-weight: bold; padding: 10px;")
        safety_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(safety_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.home_all_button = QPushButton("Home All Axes")
        self.home_all_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.home_all_button)
        layout.addWidget(button_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.home_all_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class HomingManager(QWidget):
    """
    Homing Manager Widget
    Provides per-axis homed status badges and guided homing flows
    Based on Phase 7 requirements
    """
    
    homingRequired = Signal(list)  # Signal emitted when homing is required
    
    def __init__(self, parent=None):
        super(HomingManager, self).__init__(parent)
        
        self.status = getPlugin('status')
        self.command = getPlugin('command')
        
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        if self.command is None:
            LOG.error("Could not get Command plugin")
            return
            
        self.axis_names = ['X', 'Y', 'Z']  # Default axes, can be configured
        self.homing_badges = {}
        
        self.setupUI()
        self.connectSignals()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateStatus)
        self.update_timer.start(500)  # Update every 500ms
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("homingManager")
        self.setMinimumSize(300, 100)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Title
        title_label = QLabel("Homing Status")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Badges layout
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(10)
        
        # Create homing badges for each axis
        for i, axis_name in enumerate(self.axis_names):
            badge = HomingBadge(axis_name, i)
            badge.homeRequested.connect(self.onHomeRequested)
            self.homing_badges[axis_name] = badge
            badges_layout.addWidget(badge)
            
        badges_layout.addStretch()  # Add stretch to center badges
        main_layout.addLayout(badges_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.home_all_button = QPushButton("Home All Axes")
        self.home_all_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.home_all_button.clicked.connect(self.onHomeAllRequested)
        self.home_all_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        control_layout.addStretch()
        control_layout.addWidget(self.home_all_button)
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.homed.notify(self.updateStatus)
            
    def updateStatus(self):
        """Update homing status for all axes"""
        if not self.status:
            return
            
        try:
            homed_status = self.status.homed()
            
            # Update each badge
            for i, axis_name in enumerate(self.axis_names):
                if i < len(homed_status) and axis_name in self.homing_badges:
                    is_homed = homed_status[i]
                    self.homing_badges[axis_name].updateStatus(is_homed)
                    
            # Enable/disable home all button based on machine state
            machine_on = self.status.enabled() if hasattr(self.status, 'enabled') else False
            estop_ok = not self.status.estop() if hasattr(self.status, 'estop') else True
            
            self.home_all_button.setEnabled(machine_on and estop_ok)
            
        except Exception as e:
            LOG.error(f"Error updating homing status: {e}")
            
    def onHomeRequested(self, axis_name):
        """Handle individual axis home request"""
        try:
            if self.command:
                LOG.info(f"Homing {axis_name} axis")
                # Send home command for specific axis
                self.command.home(axis_name)
        except Exception as e:
            LOG.error(f"Error homing {axis_name} axis: {e}")
            
    def onHomeAllRequested(self):
        """Handle home all axes request"""
        try:
            if self.command:
                LOG.info("Homing all axes")
                # Send home all command
                self.command.home(-1)  # -1 typically means all axes
        except Exception as e:
            LOG.error(f"Error homing all axes: {e}")
            
    def checkHomingRequired(self, operation="operation"):
        """
        Check if homing is required before an operation
        Returns True if homing is required, False if all axes are homed
        Shows dialog if homing is required
        """
        if not self.status:
            return False
            
        try:
            homed_status = self.status.homed()
            unhomed_axes = []
            
            for i, axis_name in enumerate(self.axis_names):
                if i < len(homed_status) and not homed_status[i]:
                    unhomed_axes.append(axis_name)
                    
            if unhomed_axes:
                # Show homing dialog
                dialog = HomingSequenceDialog(unhomed_axes, self)
                dialog.setWindowTitle(f"Homing Required for {operation}")
                
                result = dialog.exec_()
                
                if result == QDialog.Accepted:
                    # User chose to home all axes
                    self.onHomeAllRequested()
                    return True  # Homing was requested
                else:
                    # User cancelled
                    return True  # Homing is still required
                    
        except Exception as e:
            LOG.error(f"Error checking homing status: {e}")
            
        return False  # All axes are homed or error occurred
        
    def getUnhomedAxes(self):
        """Get list of unhomed axes"""
        if not self.status:
            return []
            
        try:
            homed_status = self.status.homed()
            unhomed_axes = []
            
            for i, axis_name in enumerate(self.axis_names):
                if i < len(homed_status) and not homed_status[i]:
                    unhomed_axes.append(axis_name)
                    
            return unhomed_axes
            
        except Exception as e:
            LOG.error(f"Error getting unhomed axes: {e}")
            return []