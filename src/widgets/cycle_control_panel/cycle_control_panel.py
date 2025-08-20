#!/usr/bin/env python

import os
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame
from qtpy.QtGui import QFont, QIcon
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger
from qtpyvcp.actions import machine_actions

LOG = logger.getLogger(__name__)

class CycleControlPanel(QWidget):
    """
    Enhanced Cycle Control Panel Widget
    Provides Start/Hold/Stop, Single Block, and Optional Stop controls
    Based on Phase 1 requirements
    """
    
    def __init__(self, parent=None):
        super(CycleControlPanel, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.setupUI()
        self.connectSignals()
        
        # Update timer for button state refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateButtonStates)
        self.update_timer.start(100)  # Update every 100ms
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("cycleControlPanel")
        self.setMinimumSize(400, 60)
        self.setMaximumSize(800, 80)
        
        # Main layout
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create control buttons
        self.buttons = {}
        
        # Cycle Start button
        self.addControlButton("cycle_start", "CYCLE START", "#4CAF50", self.onCycleStart, "Start program execution")
        
        # Cycle Hold/Resume button  
        self.addControlButton("cycle_hold", "HOLD", "#FF9800", self.onCycleHold, "Hold/Resume program execution")
        
        # Cycle Stop button
        self.addControlButton("cycle_stop", "STOP", "#F44336", self.onCycleStop, "Stop program execution")
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Single Block toggle
        self.addToggleButton("single_block", "SINGLE BLOCK", "#2196F3", self.onSingleBlockToggle, "Execute one block at a time")
        
        # Optional Stop toggle  
        self.addToggleButton("optional_stop", "OPTIONAL STOP", "#9C27B0", self.onOptionalStopToggle, "Honor optional stop codes (M1)")
        
        self.setLayout(layout)
        
    def addControlButton(self, key, text, color, callback, tooltip):
        """Add a control button to the layout"""
        button = QPushButton(text)
        button.setMinimumSize(100, 50)
        button.setMaximumSize(150, 60)
        button.setToolTip(tooltip)
        button.setObjectName(f"cycle_{key}_button")
        button.clicked.connect(callback)
        
        # Style the button
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #333;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:hover {{
                border-color: #fff;
            }}
            QPushButton:pressed {{
                background-color: #555;
            }}
            QPushButton:disabled {{
                background-color: #666;
                color: #999;
            }}
        """)
        
        self.buttons[key] = button
        self.layout().addWidget(button)
        
    def addToggleButton(self, key, text, color, callback, tooltip):
        """Add a toggle button to the layout"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setMinimumSize(100, 50)
        button.setMaximumSize(150, 60)
        button.setToolTip(tooltip)
        button.setObjectName(f"cycle_{key}_button")
        button.toggled.connect(callback)
        
        # Style the toggle button
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #666;
                border: 2px solid #333;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
            QPushButton:checked {{
                background-color: {color};
                border-color: #fff;
            }}
            QPushButton:hover {{
                border-color: #fff;
            }}
            QPushButton:disabled {{
                background-color: #444;
                color: #999;
            }}
        """)
        
        self.buttons[key] = button
        self.layout().addWidget(button)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.task_state.notify(self.updateButtonStates)
            self.status.interp_state.notify(self.updateButtonStates)
            self.status.enabled.notify(self.updateButtonStates)
            
    def updateButtonStates(self):
        """Update button states based on current LinuxCNC status"""
        if not self.status:
            return
            
        try:
            task_state = self.status.task_state()
            interp_state = self.status.interp_state()
            machine_on = self.status.enabled()
            
            # Update cycle start button
            # Can start if machine is on and not already running
            can_start = machine_on and task_state == 1  # TASK_STATE_ON
            self.buttons["cycle_start"].setEnabled(can_start)
            
            # Update cycle hold button
            # Can hold if program is running
            can_hold = machine_on and task_state == 1 and interp_state in [2, 3]  # INTERP_RUNNING or INTERP_PAUSED
            self.buttons["cycle_hold"].setEnabled(can_hold)
            
            # Update hold button text based on state
            if interp_state == 3:  # INTERP_PAUSED
                self.buttons["cycle_hold"].setText("RESUME")
            else:
                self.buttons["cycle_hold"].setText("HOLD")
                
            # Update cycle stop button
            # Can stop if machine is on and something is running/paused
            can_stop = machine_on and interp_state in [2, 3]  # INTERP_RUNNING or INTERP_PAUSED
            self.buttons["cycle_stop"].setEnabled(can_stop)
            
            # Update toggle buttons - always enabled when machine is on
            self.buttons["single_block"].setEnabled(machine_on)
            self.buttons["optional_stop"].setEnabled(machine_on)
            
        except Exception as e:
            LOG.error(f"Error updating cycle control states: {e}")
    
    def onCycleStart(self):
        """Handle cycle start button click"""
        try:
            machine_actions.program.run()
            LOG.info("Cycle start requested")
        except Exception as e:
            LOG.error(f"Error starting cycle: {e}")
            
    def onCycleHold(self):
        """Handle cycle hold/resume button click"""
        try:
            if self.status and self.status.interp_state() == 3:  # INTERP_PAUSED
                machine_actions.program.resume()
                LOG.info("Cycle resume requested")
            else:
                machine_actions.program.pause()
                LOG.info("Cycle hold requested")
        except Exception as e:
            LOG.error(f"Error holding/resuming cycle: {e}")
            
    def onCycleStop(self):
        """Handle cycle stop button click"""
        try:
            machine_actions.program.stop()
            LOG.info("Cycle stop requested")
        except Exception as e:
            LOG.error(f"Error stopping cycle: {e}")
            
    def onSingleBlockToggle(self, checked):
        """Handle single block toggle"""
        try:
            machine_actions.program.block_delete(checked)
            LOG.info(f"Single block mode: {checked}")
        except Exception as e:
            LOG.error(f"Error toggling single block: {e}")
            
    def onOptionalStopToggle(self, checked):
        """Handle optional stop toggle"""
        try:
            machine_actions.program.optional_stop(checked)
            LOG.info(f"Optional stop mode: {checked}")
        except Exception as e:
            LOG.error(f"Error toggling optional stop: {e}")