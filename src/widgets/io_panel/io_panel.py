#!/usr/bin/env python

import os
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QFrame, QPushButton, QComboBox, QCheckBox,
                            QGroupBox, QScrollArea, QSplitter)
from qtpy.QtGui import QFont, QPalette
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class IOPanel(QWidget):
    """
    IO Panel Widget for Phase 3
    Real-time IO view with live states, filters, and safe output forcing
    """
    
    def __init__(self, parent=None):
        super(IOPanel, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.hal = getPlugin('hal')
        if self.hal is None:
            LOG.warning("HAL plugin not available - IO panel will run in simulation mode")
            
        self.setupUI()
        self.connectSignals()
        
        # Update timer for real-time IO monitoring
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateIOStatus)
        self.update_timer.start(100)  # Update every 100ms for responsive IO monitoring
        
        # Mock IO data for simulation/demo
        self.mock_inputs = {
            'estop': False,
            'home_x': False,
            'home_y': False, 
            'home_z': False,
            'limit_x_min': False,
            'limit_x_max': False,
            'limit_y_min': False,
            'limit_y_max': False,
            'limit_z_min': False,
            'limit_z_max': False,
            'probe': False,
            'tool_change': False,
        }
        
        self.mock_outputs = {
            'spindle_enable': False,
            'spindle_dir': False,
            'coolant_flood': False,
            'coolant_mist': False,
            'axis_enable_x': False,
            'axis_enable_y': False,
            'axis_enable_z': False,
        }
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("ioPanel")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with title and filters
        header_layout = QHBoxLayout()
        
        title = QLabel("IO Panel - Real-time Input/Output Status")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter controls
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Inputs Only", "Outputs Only", "Active Only"])
        self.filter_combo.currentTextChanged.connect(self.updateFilter)
        
        self.safety_checkbox = QCheckBox("Safety Mode")
        self.safety_checkbox.setChecked(True)
        self.safety_checkbox.setToolTip("When enabled, output forcing requires Machine On && !ESTOP")
        
        header_layout.addWidget(filter_label)
        header_layout.addWidget(self.filter_combo)
        header_layout.addWidget(self.safety_checkbox)
        
        main_layout.addLayout(header_layout)
        
        # Splitter for inputs and outputs
        splitter = QSplitter(Qt.Horizontal)
        
        # Inputs section
        inputs_group = self.createInputsSection()
        splitter.addWidget(inputs_group)
        
        # Outputs section  
        outputs_group = self.createOutputsSection()
        splitter.addWidget(outputs_group)
        
        # Equal sizing
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready - IO monitoring active")
        self.safety_status = QLabel("Safety: ACTIVE")
        self.safety_status.setStyleSheet("color: green; font-weight: bold;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.safety_status)
        
        main_layout.addLayout(status_layout)
        self.setLayout(main_layout)
        
    def createInputsSection(self):
        """Create the inputs monitoring section"""
        group = QGroupBox("Digital Inputs")
        layout = QVBoxLayout()
        
        # Create scroll area for inputs
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout()
        
        # Input labels and indicators
        self.input_widgets = {}
        
        inputs_config = [
            ('estop', 'Emergency Stop', 0, 0),
            ('home_x', 'Home X Switch', 0, 1),
            ('home_y', 'Home Y Switch', 1, 0),
            ('home_z', 'Home Z Switch', 1, 1),
            ('limit_x_min', 'X- Limit', 2, 0),
            ('limit_x_max', 'X+ Limit', 2, 1),
            ('limit_y_min', 'Y- Limit', 3, 0),
            ('limit_y_max', 'Y+ Limit', 3, 1),
            ('limit_z_min', 'Z- Limit', 4, 0),
            ('limit_z_max', 'Z+ Limit', 4, 1),
            ('probe', 'Touch Probe', 5, 0),
            ('tool_change', 'Tool Change', 5, 1),
        ]
        
        for pin_name, display_name, row, col in inputs_config:
            self.addIOIndicator(scroll_layout, pin_name, display_name, row, col, is_input=True)
            
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        
        layout.addWidget(scroll)
        
        # Simulation controls for inputs
        sim_group = QGroupBox("Simulation Controls")
        sim_layout = QGridLayout()
        
        self.input_sim_buttons = {}
        for i, (pin_name, display_name, _, _) in enumerate(inputs_config[:6]):  # First 6 for demo
            btn = QPushButton(f"Toggle {display_name}")
            btn.clicked.connect(lambda checked, p=pin_name: self.toggleMockInput(p))
            btn.setMaximumHeight(30)
            sim_layout.addWidget(btn, i // 2, i % 2)
            self.input_sim_buttons[pin_name] = btn
            
        sim_group.setLayout(sim_layout)
        layout.addWidget(sim_group)
        
        group.setLayout(layout)
        return group
        
    def createOutputsSection(self):
        """Create the outputs control section"""
        group = QGroupBox("Digital Outputs")
        layout = QVBoxLayout()
        
        # Create scroll area for outputs
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout()
        
        # Output controls and indicators
        self.output_widgets = {}
        
        outputs_config = [
            ('spindle_enable', 'Spindle Enable', 0, 0),
            ('spindle_dir', 'Spindle Direction', 0, 1),
            ('coolant_flood', 'Coolant Flood', 1, 0),
            ('coolant_mist', 'Coolant Mist', 1, 1),
            ('axis_enable_x', 'X Axis Enable', 2, 0),
            ('axis_enable_y', 'Y Axis Enable', 2, 1),
            ('axis_enable_z', 'Z Axis Enable', 3, 0),
        ]
        
        for pin_name, display_name, row, col in outputs_config:
            self.addIOIndicator(scroll_layout, pin_name, display_name, row, col, is_input=False)
            
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        
        layout.addWidget(scroll)
        
        # Output forcing controls
        force_group = QGroupBox("Output Forcing")
        force_layout = QVBoxLayout()
        
        warning_label = QLabel("⚠️ Output forcing only available when Machine On && !ESTOP")
        warning_label.setStyleSheet("color: orange; font-weight: bold;")
        force_layout.addWidget(warning_label)
        
        self.force_buttons = {}
        for pin_name, display_name, _, _ in outputs_config:
            btn = QPushButton(f"Force {display_name}")
            btn.clicked.connect(lambda checked, p=pin_name: self.forceOutput(p))
            btn.setEnabled(False)  # Disabled by default due to safety
            btn.setMaximumHeight(30)
            force_layout.addWidget(btn)
            self.force_buttons[pin_name] = btn
            
        force_group.setLayout(force_layout)
        layout.addWidget(force_group)
        
        group.setLayout(layout)
        return group
        
    def addIOIndicator(self, layout, pin_name, display_name, row, col, is_input=True):
        """Add an IO indicator widget"""
        # Container frame
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setMinimumHeight(60)
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        label = QLabel(display_name)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold;")
        
        # Status indicator
        status = QLabel("●")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("font-size: 20px; color: red;")
        
        # Pin name
        pin_label = QLabel(pin_name)
        pin_label.setAlignment(Qt.AlignCenter)
        pin_label.setStyleSheet("font-size: 8px; color: gray;")
        
        frame_layout.addWidget(label)
        frame_layout.addWidget(status)
        frame_layout.addWidget(pin_label)
        frame.setLayout(frame_layout)
        
        # Store widgets for updates
        widget_key = f"{'input' if is_input else 'output'}_{pin_name}"
        self.input_widgets[widget_key] = {
            'frame': frame,
            'label': label,
            'status': status,
            'pin_name': pin_name,
            'is_input': is_input,
            'active': False
        }
        
        layout.addWidget(frame, row, col)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            # Connect to machine status for safety checks
            self.status.estop.notify(self.updateSafetyStatus)
            self.status.enabled.notify(self.updateSafetyStatus)
            
    def updateFilter(self, filter_text):
        """Update the display filter"""
        # TODO: Implement filtering logic based on selection
        LOG.info(f"Filter changed to: {filter_text}")
        
    def updateIOStatus(self):
        """Update IO status indicators"""
        if not self.status:
            return
            
        try:
            # Update safety status first
            self.updateSafetyStatus()
            
            # Update input indicators
            for key, widget_info in self.input_widgets.items():
                if widget_info['is_input']:
                    pin_name = widget_info['pin_name']
                    # Use mock data for simulation
                    active = self.mock_inputs.get(pin_name, False)
                    self.setIOIndicatorState(widget_info, active)
                else:
                    pin_name = widget_info['pin_name']
                    # Use mock data for simulation
                    active = self.mock_outputs.get(pin_name, False)
                    self.setIOIndicatorState(widget_info, active)
                    
        except Exception as e:
            LOG.error(f"Error updating IO status: {e}")
            
    def setIOIndicatorState(self, widget_info, active):
        """Set the state of an IO indicator"""
        if widget_info['active'] != active:
            widget_info['active'] = active
            status_widget = widget_info['status']
            
            if active:
                status_widget.setStyleSheet("font-size: 20px; color: green;")
            else:
                status_widget.setStyleSheet("font-size: 20px; color: red;")
                
    def updateSafetyStatus(self):
        """Update safety status and enable/disable output forcing"""
        if not self.status:
            return
            
        try:
            machine_on = self.status.enabled()
            estop_active = self.status.estop()
            
            # Safety condition: Machine On && !ESTOP
            safety_ok = machine_on and not estop_active
            
            if safety_ok:
                self.safety_status.setText("Safety: OK - Output forcing enabled")
                self.safety_status.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.safety_status.setText("Safety: BLOCKED - Output forcing disabled")
                self.safety_status.setStyleSheet("color: red; font-weight: bold;")
                
            # Enable/disable force buttons based on safety and checkbox
            force_enabled = safety_ok and self.safety_checkbox.isChecked()
            for btn in self.force_buttons.values():
                btn.setEnabled(force_enabled)
                
        except Exception as e:
            LOG.error(f"Error updating safety status: {e}")
            
    def toggleMockInput(self, pin_name):
        """Toggle a mock input for simulation"""
        if pin_name in self.mock_inputs:
            self.mock_inputs[pin_name] = not self.mock_inputs[pin_name]
            LOG.info(f"Toggled mock input {pin_name} to {self.mock_inputs[pin_name]}")
            
    def forceOutput(self, pin_name):
        """Force an output (with safety checks)"""
        if not self.status:
            LOG.warning("Cannot force output - no status plugin")
            return
            
        try:
            machine_on = self.status.enabled()
            estop_active = self.status.estop()
            
            if not (machine_on and not estop_active):
                LOG.warning("Output forcing blocked by safety interlock")
                return
                
            # Toggle the mock output
            if pin_name in self.mock_outputs:
                self.mock_outputs[pin_name] = not self.mock_outputs[pin_name]
                LOG.info(f"Forced output {pin_name} to {self.mock_outputs[pin_name]}")
                
        except Exception as e:
            LOG.error(f"Error forcing output {pin_name}: {e}")