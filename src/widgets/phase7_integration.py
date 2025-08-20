#!/usr/bin/env python

"""
Phase 7 Safety Integration Module
Integrates all Phase 7 safety, homing, limits, overrides & warmup components
"""

import os
from qtpy.QtCore import QObject, Signal, QTimer
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

from widgets.homing_manager.homing_manager import HomingManager
from widgets.limit_override.limit_override import LimitOverrideManager
from widgets.spindle_warmup.spindle_warmup import SpindleWarmupWidget
from widgets.maintenance_reminders.maintenance_reminders import MaintenanceRemindersWidget

LOG = logger.getLogger(__name__)

class Phase7SafetyManager(QObject):
    """
    Centralized safety manager for Phase 7 features
    Coordinates between homing, limits, warmup, and maintenance systems
    """
    
    # Safety state signals
    homingRequired = Signal(str)  # operation requiring homing
    limitOverrideActive = Signal(bool)  # limit override state
    maintenanceOverdue = Signal(list)  # overdue maintenance tasks
    
    def __init__(self, parent=None):
        super(Phase7SafetyManager, self).__init__(parent)
        
        self.status = getPlugin('status')
        self.command = getPlugin('command')
        
        # Component instances
        self.homing_manager = None
        self.limit_manager = None
        self.warmup_widget = None
        self.maintenance_widget = None
        
        # Safety state
        self.safety_interlocks_active = True
        self.last_homing_check = None
        
        # Monitor timer
        self.safety_timer = QTimer()
        self.safety_timer.timeout.connect(self.checkSafetyConditions)
        self.safety_timer.start(1000)  # Check every second
        
    def registerComponents(self, homing_manager, limit_manager, warmup_widget, maintenance_widget):
        """Register the Phase 7 components with the safety manager"""
        self.homing_manager = homing_manager
        self.limit_manager = limit_manager
        self.warmup_widget = warmup_widget
        self.maintenance_widget = maintenance_widget
        
        # Connect component signals
        if self.homing_manager:
            self.homing_manager.homingRequired.connect(self.onHomingRequired)
            
        if self.limit_manager:
            self.limit_manager.limitTriggered.connect(self.onLimitTriggered)
            self.limit_manager.overrideExpired.connect(self.onOverrideExpired)
            
        if self.warmup_widget:
            self.warmup_widget.warmupCompleted.connect(self.onWarmupCompleted)
            
        if self.maintenance_widget:
            self.maintenance_widget.maintenanceRequired.connect(self.onMaintenanceRequired)
            
        LOG.info("Phase 7 safety components registered")
        
    def checkSafetyConditions(self):
        """Periodic safety condition check"""
        if not self.status:
            return
            
        try:
            # Check if machine is in a safe state
            estop_ok = not self.status.estop()
            machine_on = self.status.enabled()
            
            if not estop_ok or not machine_on:
                self.safety_interlocks_active = True
                return
                
            # Additional safety checks can be added here
            
        except Exception as e:
            LOG.error(f"Error checking safety conditions: {e}")
            
    def checkHomingBeforeOperation(self, operation_name):
        """
        Check if homing is required before an operation
        Returns True if operation can proceed, False if homing is required
        """
        if not self.homing_manager:
            return True  # No homing manager, assume OK
            
        unhomed_axes = self.homing_manager.getUnhomedAxes()
        
        if unhomed_axes:
            LOG.warning(f"Homing required for operation '{operation_name}': {unhomed_axes}")
            self.homingRequired.emit(operation_name)
            
            # Show homing dialog
            return self.homing_manager.checkHomingRequired(operation_name)
            
        return True
        
    def checkJoggingAllowed(self):
        """Check if jogging is allowed based on safety conditions"""
        # Check homing first
        if not self.checkHomingBeforeOperation("jogging"):
            return False
            
        # Check if limit override is active (may restrict jogging)
        if self.limit_manager and self.limit_manager.isOverrideActive():
            LOG.warning("Jogging restricted due to active limit override")
            return False
            
        return True
        
    def checkProgramRunAllowed(self):
        """Check if program execution is allowed"""
        # Check homing
        if not self.checkHomingBeforeOperation("program execution"):
            return False
            
        # Check maintenance status
        if self.maintenance_widget:
            overdue_tasks = self.maintenance_widget.getOverdueTasks()
            if overdue_tasks:
                # Check if any are critical priority
                critical_tasks = [t for t in overdue_tasks if t.get('urgency') == 'critical']
                if critical_tasks:
                    LOG.error(f"Critical maintenance overdue - program execution blocked: {[t.get('title') for t in critical_tasks]}")
                    return False
                    
        return True
        
    def onHomingRequired(self, operation):
        """Handle homing required signal"""
        LOG.info(f"Homing required for operation: {operation}")
        self.homingRequired.emit(operation)
        
    def onLimitTriggered(self, triggered_axes):
        """Handle limit triggered signal"""
        LOG.warning(f"Soft limits triggered: {triggered_axes}")
        
        # The limit manager will handle the override dialog
        # This is just for logging and coordination
        
    def onOverrideExpired(self):
        """Handle limit override expiration"""
        LOG.info("Limit override expired - normal limits restored")
        self.limitOverrideActive.emit(False)
        
    def onWarmupCompleted(self, spindle_hours):
        """Handle warmup completion"""
        LOG.info(f"Spindle warmup completed - Total hours: {spindle_hours:.1f}")
        
        # Update maintenance system with spindle hours
        if self.maintenance_widget:
            # This would update the maintenance system with actual spindle runtime
            pass
            
    def onMaintenanceRequired(self, overdue_tasks):
        """Handle maintenance required signal"""
        LOG.warning(f"Maintenance required: {[t.get('title') for t in overdue_tasks]}")
        self.maintenanceOverdue.emit(overdue_tasks)
        
    def getSafetyStatus(self):
        """Get overall safety status summary"""
        status = {
            'homing_ok': True,
            'limits_ok': True,
            'maintenance_ok': True,
            'override_active': False,
            'messages': []
        }
        
        # Check homing
        if self.homing_manager:
            unhomed_axes = self.homing_manager.getUnhomedAxes()
            if unhomed_axes:
                status['homing_ok'] = False
                status['messages'].append(f"Unhomed axes: {', '.join(unhomed_axes)}")
                
        # Check limit override
        if self.limit_manager and self.limit_manager.isOverrideActive():
            status['override_active'] = True
            remaining_time = self.limit_manager.getRemainingTime()
            status['messages'].append(f"Limit override active ({remaining_time:.0f}s remaining)")
            
        # Check maintenance
        if self.maintenance_widget:
            overdue_tasks = self.maintenance_widget.getOverdueTasks()
            if overdue_tasks:
                status['maintenance_ok'] = False
                status['messages'].append(f"Overdue maintenance: {len(overdue_tasks)} task(s)")
                
        return status

class Phase7IntegrationPanel(QWidget):
    """
    Integration panel combining all Phase 7 widgets
    Provides a unified interface for safety, homing, limits, and maintenance
    """
    
    def __init__(self, parent=None):
        super(Phase7IntegrationPanel, self).__init__(parent)
        
        self.safety_manager = Phase7SafetyManager()
        self.setupUI()
        
    def setupUI(self):
        """Set up the integration panel UI"""
        self.setObjectName("phase7IntegrationPanel")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("🛡️ Phase 7 - Safety & Maintenance")
        title_label.setFont(title_label.font())
        title_label.font().setPointSize(16)
        title_label.font().setBold(True)
        title_label.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(title_label)
        
        # Top row: Homing and Limits
        top_row = QHBoxLayout()
        
        # Homing Manager
        self.homing_manager = HomingManager()
        homing_frame = QFrame()
        homing_frame.setFrameStyle(QFrame.Box)
        homing_layout = QVBoxLayout()
        homing_layout.addWidget(self.homing_manager)
        homing_frame.setLayout(homing_layout)
        top_row.addWidget(homing_frame)
        
        # Limit Override Manager  
        self.limit_manager = LimitOverrideManager()
        limit_frame = QFrame()
        limit_frame.setFrameStyle(QFrame.Box)
        limit_layout = QVBoxLayout()
        limit_layout.addWidget(self.limit_manager)
        limit_frame.setLayout(limit_layout)
        top_row.addWidget(limit_frame)
        
        layout.addLayout(top_row)
        
        # Bottom row: Warmup and Maintenance
        bottom_row = QHBoxLayout()
        
        # Spindle Warmup
        self.warmup_widget = SpindleWarmupWidget()
        warmup_frame = QFrame()
        warmup_frame.setFrameStyle(QFrame.Box)
        warmup_layout = QVBoxLayout()
        warmup_layout.addWidget(self.warmup_widget)
        warmup_frame.setLayout(warmup_layout)
        bottom_row.addWidget(warmup_frame)
        
        # Maintenance Reminders
        self.maintenance_widget = MaintenanceRemindersWidget()
        maintenance_frame = QFrame()
        maintenance_frame.setFrameStyle(QFrame.Box)
        maintenance_layout = QVBoxLayout()
        maintenance_layout.addWidget(self.maintenance_widget)
        maintenance_frame.setLayout(maintenance_layout)
        bottom_row.addWidget(maintenance_frame)
        
        layout.addLayout(bottom_row)
        
        self.setLayout(layout)
        
        # Register components with safety manager
        self.safety_manager.registerComponents(
            self.homing_manager,
            self.limit_manager, 
            self.warmup_widget,
            self.maintenance_widget
        )
        
    def getSafetyManager(self):
        """Get the safety manager instance"""
        return self.safety_manager
        
    def checkHomingBeforeOperation(self, operation_name):
        """Convenience method to check homing"""
        return self.safety_manager.checkHomingBeforeOperation(operation_name)
        
    def checkJoggingAllowed(self):
        """Convenience method to check jogging"""
        return self.safety_manager.checkJoggingAllowed()
        
    def checkProgramRunAllowed(self):
        """Convenience method to check program run"""
        return self.safety_manager.checkProgramRunAllowed()