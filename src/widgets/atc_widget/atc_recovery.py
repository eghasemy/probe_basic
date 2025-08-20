import os

import linuxcnc

# Workarround for nvidia propietary drivers
import ctypes
import ctypes.util
ctypes.CDLL(ctypes.util.find_library("GL"), mode=ctypes.RTLD_GLOBAL)
# end of Workarround

from qtpy.QtCore import Property, Slot, Signal, QUrl
from qtpy.QtGui import QColor
from qtpy.QtQuickWidgets import QQuickWidget

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)
STATUS = getPlugin('status')
IN_DESIGNER = os.getenv('DESIGNER', False)
WIDGET_PATH = os.path.dirname(os.path.abspath(__file__))
INIFILE = linuxcnc.ini(os.getenv("INI_FILE_NAME"))

class ATCRecovery(QQuickWidget):
    """Phase 5 - ATC Recovery Wizard Widget"""
    
    # Signals for UI updates
    recoveryStatusSig = Signal(str, arguments=["status"])
    recoveryStepSig = Signal(str, arguments=["step"])
    recoveryProgressSig = Signal(int, arguments=["progress"])
    
    def __init__(self, parent=None):
        super(ATCRecovery, self).__init__(parent)

        self._background_color = QColor(40, 40, 40)
        self.recovery_active = False
        self.current_step = ""
        self.recovery_progress = 0
        
        self.engine().rootContext().setContextProperty("atc_recovery", self)
        qml_path = os.path.join(WIDGET_PATH, "atc_recovery.qml")
        url = QUrl.fromLocalFile(qml_path)

        if not IN_DESIGNER:
            self.setSource(url)
        
    @Property(QColor)
    def backgroundColor(self):
        return self._background_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._background_color = color
        
    @Slot()
    def start_recovery(self):
        """Start ATC recovery process"""
        self.recovery_active = True
        self.recovery_progress = 0
        self.current_step = "Starting recovery..."
        self.recoveryStatusSig.emit("Starting recovery process...")
        self.recoveryStepSig.emit(self.current_step)
        self.recoveryProgressSig.emit(self.recovery_progress)
        LOG.info("ATC Recovery: Starting recovery process")
        
    @Slot()
    def resume_mid_change(self):
        """Resume a tool change that was interrupted mid-process"""
        self.current_step = "Resuming tool change..."
        self.recovery_progress = 25
        self.recoveryStepSig.emit(self.current_step)
        self.recoveryProgressSig.emit(self.recovery_progress)
        
        # Simulate recovery steps
        self._simulate_recovery_step("Checking ATC position...", 40)
        self._simulate_recovery_step("Verifying tool position...", 60)
        self._simulate_recovery_step("Completing tool change...", 80)
        self._simulate_recovery_step("Recovery complete", 100)
        
        LOG.info("ATC Recovery: Resumed mid-change")
        
    @Slot()
    def home_atc(self):
        """Home the ATC to known position"""
        self.current_step = "Homing ATC..."
        self.recovery_progress = 10
        self.recoveryStepSig.emit(self.current_step)
        self.recoveryProgressSig.emit(self.recovery_progress)
        
        # Simulate homing process
        self._simulate_recovery_step("Moving to home position...", 30)
        self._simulate_recovery_step("Checking sensors...", 60)
        self._simulate_recovery_step("ATC homed successfully", 100)
        
        LOG.info("ATC Recovery: ATC homed")
        
    @Slot(int)
    def manual_jog_to_pocket(self, pocket):
        """Manually jog ATC to specific pocket"""
        self.current_step = f"Jogging to pocket {pocket}..."
        self.recovery_progress = 20
        self.recoveryStepSig.emit(self.current_step)
        self.recoveryProgressSig.emit(self.recovery_progress)
        
        # Simulate manual jog
        self._simulate_recovery_step(f"Moving to pocket {pocket}...", 50)
        self._simulate_recovery_step(f"Positioned at pocket {pocket}", 100)
        
        LOG.info(f"ATC Recovery: Manually jogged to pocket {pocket}")
        
    @Slot()
    def clear_fault(self):
        """Clear ATC fault and return to Ready state"""
        self.current_step = "Clearing fault..."
        self.recovery_progress = 30
        self.recoveryStepSig.emit(self.current_step)
        self.recoveryProgressSig.emit(self.recovery_progress)
        
        # Simulate fault clearing
        self._simulate_recovery_step("Resetting ATC state...", 60)
        self._simulate_recovery_step("Fault cleared successfully", 100)
        
        # Signal the main ATC widget to return to Ready state
        try:
            # Get the main ATC widget and clear the fault
            LOG.info("ATC Recovery: Attempting to clear ATC fault")
            # This would normally communicate with the actual ATC widget
        except Exception as e:
            LOG.error(f"ATC Recovery: Failed to clear fault: {e}")
        
        LOG.info("ATC Recovery: Fault cleared")
        
    @Slot()
    def complete_recovery(self):
        """Complete the recovery process"""
        self.recovery_active = False
        self.current_step = "Recovery completed"
        self.recovery_progress = 100
        self.recoveryStepSig.emit(self.current_step)
        self.recoveryProgressSig.emit(self.recovery_progress)
        self.recoveryStatusSig.emit("Recovery completed successfully")
        
        LOG.info("ATC Recovery: Recovery process completed")
        
    def _simulate_recovery_step(self, step, progress):
        """Helper method to simulate recovery steps with delays"""
        # In a real implementation, this would be actual recovery logic
        # For now, just update the UI
        self.current_step = step
        self.recovery_progress = progress
        self.recoveryStepSig.emit(step)
        self.recoveryProgressSig.emit(progress)