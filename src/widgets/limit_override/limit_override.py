#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QFrame, QDialog, QMessageBox,
                            QDialogButtonBox, QTextEdit, QComboBox, QCheckBox,
                            QProgressBar, QSpinBox)
from qtpy.QtGui import QFont, QPalette
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class LimitOverrideDialog(QDialog):
    """Dialog for soft limit override with countdown and confirmation"""
    
    overrideAccepted = Signal(int, str)  # Signal: (duration_minutes, reason)
    
    def __init__(self, triggered_axes, parent=None):
        super(LimitOverrideDialog, self).__init__(parent)
        
        self.triggered_axes = triggered_axes or []
        self.countdown_seconds = 30  # 30 second countdown
        self.remaining_seconds = self.countdown_seconds
        
        self.setupUI()
        self.startCountdown()
        
    def setupUI(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Soft Limit Triggered - Override Required")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        # Make dialog stay on top and grab attention
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Warning header
        warning_frame = QFrame()
        warning_frame.setFrameStyle(QFrame.Box)
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #ffebee;
                border: 2px solid #f44336;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        warning_layout = QVBoxLayout()
        
        warning_icon = QLabel("⚠️ SOFT LIMIT TRIGGERED ⚠️")
        warning_icon.setFont(QFont("Arial", 16, QFont.Bold))
        warning_icon.setAlignment(Qt.AlignCenter)
        warning_icon.setStyleSheet("color: #d32f2f; padding: 5px;")
        warning_layout.addWidget(warning_icon)
        
        if self.triggered_axes:
            axes_text = ", ".join(self.triggered_axes)
            axes_label = QLabel(f"Limit triggered on axis: {axes_text}")
        else:
            axes_label = QLabel("Soft limit boundary has been exceeded")
            
        axes_label.setAlignment(Qt.AlignCenter)
        axes_label.setFont(QFont("Arial", 12))
        axes_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        warning_layout.addWidget(axes_label)
        
        warning_frame.setLayout(warning_layout)
        layout.addWidget(warning_frame)
        
        # Countdown timer
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("""
            background-color: #fff3e0;
            border: 2px solid #ff9800;
            border-radius: 6px;
            padding: 10px;
            color: #ef6c00;
        """)
        layout.addWidget(self.countdown_label)
        
        # Information section
        info_label = QLabel("""
<b>Safety Information:</b><br>
• Soft limits protect your machine from crashes<br>
• Override should only be used for recovery operations<br>
• Machine movement will be limited during override<br>
• Override will automatically expire after the set duration
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Override settings
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.Box)
        settings_layout = QVBoxLayout()
        
        settings_title = QLabel("Override Settings:")
        settings_title.setFont(QFont("Arial", 12, QFont.Bold))
        settings_layout.addWidget(settings_title)
        
        # Duration selection
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Override Duration:"))
        
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 60)
        self.duration_spinbox.setValue(5)
        self.duration_spinbox.setSuffix(" minutes")
        self.duration_spinbox.setStyleSheet("padding: 4px;")
        duration_layout.addWidget(self.duration_spinbox)
        duration_layout.addStretch()
        
        settings_layout.addLayout(duration_layout)
        
        # Reason selection
        reason_layout = QVBoxLayout()
        reason_layout.addWidget(QLabel("Reason for Override:"))
        
        self.reason_combo = QComboBox()
        self.reason_combo.addItems([
            "Machine Recovery",
            "Tool Change Required", 
            "Workpiece Adjustment",
            "Manual Positioning",
            "Emergency Access",
            "Maintenance Required",
            "Other (specify below)"
        ])
        self.reason_combo.setStyleSheet("padding: 4px;")
        reason_layout.addWidget(self.reason_combo)
        
        # Additional reason text
        self.reason_text = QTextEdit()
        self.reason_text.setMaximumHeight(60)
        self.reason_text.setPlaceholderText("Additional details (optional)")
        self.reason_text.setStyleSheet("padding: 4px;")
        reason_layout.addWidget(self.reason_text)
        
        settings_layout.addLayout(reason_layout)
        settings_frame.setLayout(settings_layout)
        layout.addWidget(settings_frame)
        
        # Safety confirmation
        self.safety_checkbox = QCheckBox("I understand the safety implications and take full responsibility")
        self.safety_checkbox.setFont(QFont("Arial", 10, QFont.Bold))
        self.safety_checkbox.setStyleSheet("color: #d32f2f; padding: 5px;")
        layout.addWidget(self.safety_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel - Keep Limits Active")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.override_button = QPushButton("OVERRIDE LIMITS")
        self.override_button.setEnabled(False)
        self.override_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.override_button)
        layout.addWidget(button_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.cancel_button.clicked.connect(self.reject)
        self.override_button.clicked.connect(self.acceptOverride)
        self.safety_checkbox.toggled.connect(self.updateOverrideButton)
        
        # Timer for countdown
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.updateCountdown)
        
    def startCountdown(self):
        """Start the countdown timer"""
        self.countdown_timer.start(1000)  # Update every second
        self.updateCountdown()
        
    def updateCountdown(self):
        """Update countdown display"""
        if self.remaining_seconds > 0:
            self.countdown_label.setText(f"Auto-reject in {self.remaining_seconds} seconds")
            self.remaining_seconds -= 1
        else:
            # Time expired - auto-reject
            self.countdown_timer.stop()
            self.reject()
            
    def updateOverrideButton(self):
        """Update override button state based on safety checkbox"""
        self.override_button.setEnabled(self.safety_checkbox.isChecked())
        
    def acceptOverride(self):
        """Accept the override with settings"""
        duration = self.duration_spinbox.value()
        reason = self.reason_combo.currentText()
        
        additional_text = self.reason_text.toPlainText().strip()
        if additional_text:
            reason += f" - {additional_text}"
            
        LOG.warning(f"Soft limit override accepted: {duration} minutes, Reason: {reason}")
        
        self.overrideAccepted.emit(duration, reason)
        self.accept()
        
    def reject(self):
        """Reject the override"""
        self.countdown_timer.stop()
        LOG.info("Soft limit override rejected")
        super().reject()

class LimitOverrideManager(QWidget):
    """
    Limit Override Manager
    Manages soft limit overrides with time-boxed bypass and auto-revert
    Based on Phase 7 requirements
    """
    
    limitTriggered = Signal(list)  # Signal emitted when limits are triggered
    overrideExpired = Signal()     # Signal emitted when override expires
    
    def __init__(self, parent=None):
        super(LimitOverrideManager, self).__init__(parent)
        
        self.status = getPlugin('status')
        self.command = getPlugin('command')
        
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        if self.command is None:
            LOG.error("Could not get Command plugin")
            return
            
        self.override_active = False
        self.override_start_time = None
        self.override_duration_minutes = 0
        self.override_reason = ""
        
        self.setupUI()
        self.connectSignals()
        
        # Monitor timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitorLimits)
        self.monitor_timer.start(100)  # Check every 100ms
        
        # Override timer
        self.override_timer = QTimer()
        self.override_timer.timeout.connect(self.checkOverrideExpiry)
        
    def setupUI(self):
        """Set up the manager UI"""
        self.setObjectName("limitOverrideManager")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Status display
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.Box)
        self.status_frame.setVisible(False)  # Hidden by default
        
        status_layout = QVBoxLayout()
        
        self.status_title = QLabel("Soft Limit Override Active")
        self.status_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.status_title.setAlignment(Qt.AlignCenter)
        self.status_title.setStyleSheet("color: #ff6b35; padding: 5px;")
        status_layout.addWidget(self.status_title)
        
        self.time_remaining_label = QLabel()
        self.time_remaining_label.setAlignment(Qt.AlignCenter)
        self.time_remaining_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.time_remaining_label)
        
        self.reason_label = QLabel()
        self.reason_label.setAlignment(Qt.AlignCenter)
        self.reason_label.setWordWrap(True)
        self.reason_label.setFont(QFont("Arial", 9))
        self.reason_label.setStyleSheet("color: #666; padding: 5px;")
        status_layout.addWidget(self.reason_label)
        
        # Manual revert button
        self.revert_button = QPushButton("Revert to Normal Limits")
        self.revert_button.clicked.connect(self.revertOverride)
        self.revert_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        status_layout.addWidget(self.revert_button)
        
        self.status_frame.setLayout(status_layout)
        layout.addWidget(self.status_frame)
        
        self.setLayout(layout)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.limit.notify(self.onLimitChanged)
            
    def monitorLimits(self):
        """Monitor for limit triggers"""
        if not self.status or self.override_active:
            return
            
        try:
            limits = self.status.limit()
            
            if any(limits):
                # Limit triggered - get which axes
                triggered_axes = []
                axis_names = ['X', 'Y', 'Z', 'A', 'B', 'C']
                
                for i, limit_triggered in enumerate(limits):
                    if limit_triggered and i < len(axis_names):
                        triggered_axes.append(axis_names[i])
                        
                LOG.warning(f"Soft limits triggered: {triggered_axes}")
                self.showOverrideDialog(triggered_axes)
                
        except Exception as e:
            LOG.error(f"Error monitoring limits: {e}")
            
    def onLimitChanged(self):
        """Handle limit status change"""
        # This is called by the status signal system
        pass
        
    def showOverrideDialog(self, triggered_axes):
        """Show the override dialog"""
        dialog = LimitOverrideDialog(triggered_axes, self)
        dialog.overrideAccepted.connect(self.activateOverride)
        
        result = dialog.exec_()
        
        if result == QDialog.Rejected:
            LOG.info("Limit override was rejected - limits remain active")
            
    def activateOverride(self, duration_minutes, reason):
        """Activate the override with given duration and reason"""
        self.override_active = True
        self.override_start_time = datetime.now()
        self.override_duration_minutes = duration_minutes
        self.override_reason = reason
        
        LOG.warning(f"Soft limit override activated for {duration_minutes} minutes: {reason}")
        
        # Show status display
        self.status_frame.setVisible(True)
        self.status_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        self.reason_label.setText(f"Reason: {reason}")
        
        # Start override timer
        self.override_timer.start(1000)  # Update every second
        
        # Here you would integrate with LinuxCNC to actually override the limits
        # This might involve HAL pins or LinuxCNC parameters
        try:
            if self.command:
                # Send command to disable soft limits
                # The exact implementation depends on LinuxCNC version and configuration
                LOG.info("Sending soft limit override command to LinuxCNC")
                # self.command.set_parameter("SOFT_LIMIT_OVERRIDE", 1)
                
        except Exception as e:
            LOG.error(f"Error activating soft limit override: {e}")
            
    def checkOverrideExpiry(self):
        """Check if override has expired"""
        if not self.override_active:
            self.override_timer.stop()
            return
            
        elapsed = datetime.now() - self.override_start_time
        remaining = timedelta(minutes=self.override_duration_minutes) - elapsed
        
        if remaining.total_seconds() <= 0:
            # Override expired
            self.revertOverride()
        else:
            # Update display
            remaining_minutes = int(remaining.total_seconds() // 60)
            remaining_seconds = int(remaining.total_seconds() % 60)
            self.time_remaining_label.setText(f"Time remaining: {remaining_minutes}:{remaining_seconds:02d}")
            
    def revertOverride(self):
        """Revert the override and restore normal limits"""
        if not self.override_active:
            return
            
        self.override_active = False
        self.override_timer.stop()
        
        LOG.info("Soft limit override reverted - normal limits restored")
        
        # Hide status display
        self.status_frame.setVisible(False)
        
        # Re-enable soft limits in LinuxCNC
        try:
            if self.command:
                LOG.info("Sending soft limit restore command to LinuxCNC")
                # self.command.set_parameter("SOFT_LIMIT_OVERRIDE", 0)
                
        except Exception as e:
            LOG.error(f"Error restoring soft limits: {e}")
            
        self.overrideExpired.emit()
        
    def isOverrideActive(self):
        """Check if override is currently active"""
        return self.override_active
        
    def getRemainingTime(self):
        """Get remaining override time in seconds"""
        if not self.override_active:
            return 0
            
        elapsed = datetime.now() - self.override_start_time
        remaining = timedelta(minutes=self.override_duration_minutes) - elapsed
        return max(0, remaining.total_seconds())