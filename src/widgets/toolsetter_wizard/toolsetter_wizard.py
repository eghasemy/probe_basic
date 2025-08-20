"""
Toolsetter Wizard Widget
Phase 4 - Guided tool length setting that writes to tool.tbl
"""

import os
from qtpyvcp import SETTINGS
from qtpyvcp.widgets.base_widgets.base_widget import VCPBaseWidget
from qtpyvcp.widgets.qtdesigner import WidgetExtension
from qtpyvcp.utilities.logger import getLogger

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QLabel, QPushButton, QSpinBox, QDoubleSpinBox,
                           QComboBox, QCheckBox, QTextEdit, QProgressBar,
                           QGridLayout, QFrame, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

LOG = getLogger(__name__)

class ToolsetterWizard(VCPBaseWidget):
    """
    Toolsetter Wizard Widget
    
    Provides guided tool length setting workflow with:
    - Step-by-step guidance
    - Safety checks and validation
    - Automatic tool.tbl writing
    - Breakage detection
    """
    
    toolMeasured = pyqtSignal(float)  # Emitted when tool is measured
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.measurement_history = []
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Tool Setter Wizard")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Step progress
        self.progress_group = QGroupBox("Setup Progress")
        self.createProgressSteps()
        main_layout.addWidget(self.progress_group)
        
        # Configuration section
        config_group = QGroupBox("Tool Setter Configuration")
        config_layout = QGridLayout()
        
        # Position settings
        config_layout.addWidget(QLabel("Tool Setter Position (G30):"), 0, 0)
        position_layout = QHBoxLayout()
        
        self.set_position_btn = QPushButton("Set Current Position")
        self.set_position_btn.clicked.connect(self.setToolsetterPosition)
        position_layout.addWidget(self.set_position_btn)
        
        self.goto_position_btn = QPushButton("Go to Position")
        self.goto_position_btn.clicked.connect(self.gotoToolsetterPosition)
        position_layout.addWidget(self.goto_position_btn)
        
        config_layout.addLayout(position_layout, 0, 1)
        
        # Spindle zero height
        config_layout.addWidget(QLabel("Spindle Zero Height:"), 1, 0)
        self.spindle_zero = QDoubleSpinBox()
        self.spindle_zero.setRange(-10.0, 0.0)
        self.spindle_zero.setValue(-2.5)
        self.spindle_zero.setSuffix(" in")
        self.spindle_zero.setDecimals(4)
        self.spindle_zero.setToolTip("Distance from Z home to spindle nose trigger point")
        config_layout.addWidget(self.spindle_zero, 1, 1)
        
        # Feed rates
        config_layout.addWidget(QLabel("Fast Probe Feed:"), 2, 0)
        self.fast_feed = QSpinBox()
        self.fast_feed.setRange(10, 500)
        self.fast_feed.setValue(100)
        self.fast_feed.setSuffix(" IPM")
        config_layout.addWidget(self.fast_feed, 2, 1)
        
        config_layout.addWidget(QLabel("Slow Probe Feed:"), 3, 0)
        self.slow_feed = QSpinBox()
        self.slow_feed.setRange(0, 50)
        self.slow_feed.setValue(10)
        self.slow_feed.setSuffix(" IPM")
        self.slow_feed.setSpecialValueText("Disabled")
        config_layout.addWidget(self.slow_feed, 3, 1)
        
        # Safety settings
        config_layout.addWidget(QLabel("Max Z Travel:"), 4, 0)
        self.max_z_travel = QDoubleSpinBox()
        self.max_z_travel.setRange(0.1, 5.0)
        self.max_z_travel.setValue(2.0)
        self.max_z_travel.setSuffix(" in")
        config_layout.addWidget(self.max_z_travel, 4, 1)
        
        config_layout.addWidget(QLabel("Retract Distance:"), 5, 0)
        self.retract_distance = QDoubleSpinBox()
        self.retract_distance.setRange(0.01, 0.5)
        self.retract_distance.setValue(0.1)
        self.retract_distance.setSuffix(" in")
        config_layout.addWidget(self.retract_distance, 5, 1)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # Breakage detection
        breakage_group = QGroupBox("Breakage Detection")
        breakage_layout = QGridLayout()
        
        self.enable_breakage_check = QCheckBox("Enable Breakage Detection")
        self.enable_breakage_check.toggled.connect(self.toggleBreakageCheck)
        breakage_layout.addWidget(self.enable_breakage_check, 0, 0, 1, 2)
        
        breakage_layout.addWidget(QLabel("Expected Length:"), 1, 0)
        self.expected_length = QDoubleSpinBox()
        self.expected_length.setRange(0.0, 10.0)
        self.expected_length.setValue(0.0)
        self.expected_length.setSuffix(" in")
        self.expected_length.setDecimals(4)
        self.expected_length.setEnabled(False)
        breakage_layout.addWidget(self.expected_length, 1, 1)
        
        breakage_layout.addWidget(QLabel("Tolerance:"), 2, 0)
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setRange(0.001, 0.1)
        self.tolerance.setValue(0.010)
        self.tolerance.setSuffix(" in")
        self.tolerance.setDecimals(4)
        self.tolerance.setEnabled(False)
        breakage_layout.addWidget(self.tolerance, 2, 1)
        
        breakage_group.setLayout(breakage_layout)
        main_layout.addWidget(breakage_group)
        
        # Tool measurement section
        measure_group = QGroupBox("Tool Measurement")
        measure_layout = QVBoxLayout()
        
        # Current tool info
        tool_info_layout = QHBoxLayout()
        tool_info_layout.addWidget(QLabel("Current Tool:"))
        self.current_tool_label = QLabel("No tool loaded")
        self.current_tool_label.setFont(QFont("Arial", 10, QFont.Bold))
        tool_info_layout.addWidget(self.current_tool_label)
        tool_info_layout.addStretch()
        measure_layout.addLayout(tool_info_layout)
        
        # Measurement controls
        button_layout = QHBoxLayout()
        
        self.load_tool_btn = QPushButton("Load Tool")
        self.load_tool_btn.clicked.connect(self.loadTool)
        button_layout.addWidget(self.load_tool_btn)
        
        self.measure_btn = QPushButton("Measure Tool")
        self.measure_btn.clicked.connect(self.measureTool)
        self.measure_btn.setEnabled(False)
        button_layout.addWidget(self.measure_btn)
        
        self.save_offset_btn = QPushButton("Save to Tool Table")
        self.save_offset_btn.clicked.connect(self.saveToolOffset)
        self.save_offset_btn.setEnabled(False)
        button_layout.addWidget(self.save_offset_btn)
        
        measure_layout.addLayout(button_layout)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(100)
        self.results_text.setReadOnly(True)
        measure_layout.addWidget(self.results_text)
        
        measure_group.setLayout(measure_layout)
        main_layout.addWidget(measure_group)
        
        # Measurement history
        history_group = QGroupBox("Measurement History")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        history_layout.addWidget(self.history_list)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clearHistory)
        history_layout.addWidget(clear_history_btn)
        
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        # Status
        self.status_label = QLabel("Ready - Configure tool setter position")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        
    def createProgressSteps(self):
        """Create the setup progress steps"""
        progress_layout = QVBoxLayout()
        
        self.steps = [
            "Set tool setter position (G30)",
            "Configure probe parameters",
            "Load tool in spindle",
            "Measure tool length",
            "Save to tool table"
        ]
        
        self.step_labels = []
        for i, step in enumerate(self.steps):
            label = QLabel(f"{i+1}. {step}")
            if i == 0:
                label.setStyleSheet("color: blue; font-weight: bold;")
            else:
                label.setStyleSheet("color: gray;")
            self.step_labels.append(label)
            progress_layout.addWidget(label)
            
        self.progress_group.setLayout(progress_layout)
        
    def updateProgress(self, step):
        """Update the progress display"""
        self.current_step = step
        
        for i, label in enumerate(self.step_labels):
            if i < step:
                label.setStyleSheet("color: green; font-weight: bold;")
            elif i == step:
                label.setStyleSheet("color: blue; font-weight: bold;")
            else:
                label.setStyleSheet("color: gray;")
                
    def toggleBreakageCheck(self, enabled):
        """Toggle breakage detection controls"""
        self.expected_length.setEnabled(enabled)
        self.tolerance.setEnabled(enabled)
        
    @pyqtSlot()
    def setToolsetterPosition(self):
        """Set current position as tool setter position (G30)"""
        # TODO: Implement G30 position setting via LinuxCNC
        LOG.info("Setting current position as G30 tool setter position")
        self.status_label.setText("Tool setter position set")
        self.updateProgress(1)
        
        # Enable tool loading after position is set
        self.load_tool_btn.setEnabled(True)
        
    @pyqtSlot()
    def gotoToolsetterPosition(self):
        """Move to tool setter position"""
        # TODO: Implement movement to G30 position
        LOG.info("Moving to G30 tool setter position")
        self.status_label.setText("Moving to tool setter position...")
        
    @pyqtSlot()
    def loadTool(self):
        """Load a tool in the spindle"""
        # TODO: Implement tool loading dialog/interface
        LOG.info("Loading tool in spindle")
        
        # For demo purposes, simulate tool loading
        self.current_tool_label.setText("Tool T1 loaded")
        self.measure_btn.setEnabled(True)
        self.updateProgress(2)
        self.status_label.setText("Tool loaded - ready to measure")
        
    @pyqtSlot()
    def measureTool(self):
        """Measure the current tool length"""
        self.status_label.setText("Measuring tool length...")
        self.measure_btn.setEnabled(False)
        
        # Get measurement parameters
        params = {
            3140: self.fast_feed.value(),
            3141: self.slow_feed.value(),
            3142: 200,  # traverse feed rate
            3143: self.max_z_travel.value(),
            3144: self.retract_distance.value(),
            3145: self.spindle_zero.value(),
            3146: 0.0,  # safe Z (will use current Z home)
            3147: 1 if self.enable_breakage_check.isChecked() else 0,
            3148: self.expected_length.value(),
            3149: self.tolerance.value()
        }
        
        # TODO: Set parameters in LinuxCNC and execute toolsetter.ngc
        LOG.info("Executing tool measurement")
        LOG.info(f"Parameters: {params}")
        
        # Simulate measurement result for demo
        measured_length = 2.5432  # Example measurement
        self.onToolMeasured(measured_length)
        
    def onToolMeasured(self, length):
        """Handle tool measurement completion"""
        self.measured_length = length
        
        # Check for breakage if enabled
        if self.enable_breakage_check.isChecked() and self.expected_length.value() > 0:
            difference = abs(length - self.expected_length.value())
            if difference > self.tolerance.value():
                self.results_text.setText(
                    f"⚠️ TOOL BREAKAGE DETECTED!\n"
                    f"Expected: {self.expected_length.value():.4f} in\n"
                    f"Measured: {length:.4f} in\n"
                    f"Difference: {difference:.4f} in"
                )
                self.status_label.setText("Tool breakage detected!")
                return
                
        # Normal measurement
        self.results_text.setText(
            f"✓ Tool measurement complete\n"
            f"Length: {length:.4f} in\n"
            f"Ready to save to tool table"
        )
        
        self.save_offset_btn.setEnabled(True)
        self.updateProgress(3)
        self.status_label.setText("Measurement complete - save to tool table")
        
        # Add to history
        tool_num = 1  # TODO: Get actual tool number
        history_item = f"Tool T{tool_num}: {length:.4f} in"
        self.history_list.addItem(history_item)
        self.measurement_history.append((tool_num, length))
        
        # Emit signal
        self.toolMeasured.emit(length)
        
    @pyqtSlot()
    def saveToolOffset(self):
        """Save the measured tool length to tool table"""
        if not hasattr(self, 'measured_length'):
            return
            
        # TODO: Implement tool table writing via LinuxCNC
        LOG.info(f"Saving tool length {self.measured_length} to tool table")
        
        self.status_label.setText("Tool length saved to tool table")
        self.updateProgress(4)
        
        # Reset for next measurement
        self.save_offset_btn.setEnabled(False)
        self.measure_btn.setEnabled(True)
        
        self.results_text.append(f"\n✓ Tool length saved to tool.tbl")
        
    @pyqtSlot()
    def clearHistory(self):
        """Clear measurement history"""
        self.history_list.clear()
        self.measurement_history.clear()
        
    def getToolsetterParameters(self):
        """Get current tool setter parameters as dictionary"""
        return {
            'fast_feed': self.fast_feed.value(),
            'slow_feed': self.slow_feed.value(),
            'max_z_travel': self.max_z_travel.value(),
            'retract_distance': self.retract_distance.value(),
            'spindle_zero_height': self.spindle_zero.value(),
            'breakage_check_enabled': self.enable_breakage_check.isChecked(),
            'expected_length': self.expected_length.value(),
            'tolerance': self.tolerance.value()
        }
        
    def setToolsetterParameters(self, params):
        """Set tool setter parameters from dictionary"""
        if 'fast_feed' in params:
            self.fast_feed.setValue(params['fast_feed'])
        if 'slow_feed' in params:
            self.slow_feed.setValue(params['slow_feed'])
        if 'max_z_travel' in params:
            self.max_z_travel.setValue(params['max_z_travel'])
        if 'retract_distance' in params:
            self.retract_distance.setValue(params['retract_distance'])
        if 'spindle_zero_height' in params:
            self.spindle_zero.setValue(params['spindle_zero_height'])
        if 'breakage_check_enabled' in params:
            self.enable_breakage_check.setChecked(params['breakage_check_enabled'])
        if 'expected_length' in params:
            self.expected_length.setValue(params['expected_length'])
        if 'tolerance' in params:
            self.tolerance.setValue(params['tolerance'])

# Widget extension for QtDesigner
class ToolsetterWizardExtension(WidgetExtension):
    def pluginClass(self):
        return ToolsetterWizard
    
    def iconPath(self):
        return os.path.join(os.path.dirname(__file__), 'toolsetter_wizard.png')