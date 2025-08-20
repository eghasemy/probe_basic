"""
Probing Wizards Widget
Phase 4 - Unified probing flows with safety checklist and dry-run preview
"""

import os
from qtpyvcp import SETTINGS
from qtpyvcp.widgets.base_widgets.base_widget import VCPBaseWidget
from qtpyvcp.widgets.qtdesigner import WidgetExtension
from qtpyvcp.utilities.logger import getLogger

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QGroupBox, QLabel, QPushButton, QSpinBox, QDoubleSpinBox,
                           QComboBox, QCheckBox, QTextEdit, QProgressBar, QListWidget,
                           QGridLayout, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor

LOG = getLogger(__name__)

class SafetyChecklist(QWidget):
    """Safety checklist widget for probing operations"""
    
    checklistComplete = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        self.checklist_items = [
            "Probe is properly connected and responding",
            "Probe tip is clean and undamaged", 
            "Work piece is securely clamped",
            "Spindle is stopped",
            "Tool length offset is correct",
            "Safe Z height is set appropriately",
            "Emergency stop is accessible"
        ]
        
        self.checkboxes = []
        for item in self.checklist_items:
            cb = QCheckBox(item)
            cb.toggled.connect(self.checkComplete)
            self.checkboxes.append(cb)
            layout.addWidget(cb)
            
        self.setLayout(layout)
        
    def checkComplete(self):
        """Check if all items are checked"""
        all_checked = all(cb.isChecked() for cb in self.checkboxes)
        self.checklistComplete.emit(all_checked)
        
    def reset(self):
        """Reset all checkboxes"""
        for cb in self.checkboxes:
            cb.setChecked(False)

class ProbeDiagram(QWidget):
    """Visual diagram widget showing probe positioning"""
    
    def __init__(self):
        super().__init__()
        self.probe_type = "edge"
        self.probe_direction = 0
        self.setMinimumSize(200, 200)
        
    def setProbeType(self, probe_type, direction=0):
        """Set the probe type and direction for diagram"""
        self.probe_type = probe_type
        self.probe_direction = direction
        self.update()
        
    def paintEvent(self, event):
        """Draw the probe diagram"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw workpiece (gray rectangle)
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.fillRect(50, 50, 100, 100, QColor(200, 200, 200))
        
        # Draw probe position (red circle)
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        
        if self.probe_type == "edge":
            self.drawEdgeProbe(painter)
        elif self.probe_type == "corner":
            self.drawCornerProbe(painter)
        elif self.probe_type == "boss_pocket":
            self.drawBossPocketProbe(painter)
        elif self.probe_type == "z_touchoff":
            self.drawZTouchoffProbe(painter)
            
    def drawEdgeProbe(self, painter):
        """Draw edge probe positioning"""
        if self.probe_direction == 0:  # X+
            painter.drawEllipse(165, 95, 10, 10)
        elif self.probe_direction == 1:  # X-
            painter.drawEllipse(25, 95, 10, 10)
        elif self.probe_direction == 2:  # Y+
            painter.drawEllipse(95, 25, 10, 10)
        elif self.probe_direction == 3:  # Y-
            painter.drawEllipse(95, 165, 10, 10)
            
    def drawCornerProbe(self, painter):
        """Draw corner probe positioning"""
        # Show two probe positions for corner
        painter.drawEllipse(70, 30, 8, 8)  # Y probe
        painter.drawEllipse(30, 70, 8, 8)  # X probe
        
    def drawBossPocketProbe(self, painter):
        """Draw boss/pocket probe positioning"""
        # Show center position
        painter.drawEllipse(95, 95, 10, 10)
        
    def drawZTouchoffProbe(self, painter):
        """Draw Z touchoff probe positioning"""
        # Show probe above surface
        painter.drawEllipse(95, 20, 10, 10)

class ProbingWizards(VCPBaseWidget):
    """
    Probing Wizards Widget
    
    Provides guided probing workflows with:
    - Visual diagrams and safety checklists
    - Parameter entry for probe settings
    - Dry-run preview capability
    - Integration with NGC probing macros
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.probe_params = {}
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        
        # Create tab widget for different probe types
        self.tab_widget = QTabWidget()
        
        # Edge probing tab
        self.edge_tab = self.createEdgeTab()
        self.tab_widget.addTab(self.edge_tab, "Edges")
        
        # Corner probing tab
        self.corner_tab = self.createCornerTab()
        self.tab_widget.addTab(self.corner_tab, "Corners")
        
        # Boss/Pocket tab
        self.boss_pocket_tab = self.createBossPocketTab()
        self.tab_widget.addTab(self.boss_pocket_tab, "Boss/Pocket")
        
        # Z Touch-off tab
        self.z_touchoff_tab = self.createZTouchoffTab()
        self.tab_widget.addTab(self.z_touchoff_tab, "Z Touch-off")
        
        # Tool Setter tab
        self.toolsetter_tab = self.createToolsetterTab()
        self.tab_widget.addTab(self.toolsetter_tab, "Tool Setter")
        
        # Calibration tab
        self.calibration_tab = self.createCalibrationTab()
        self.tab_widget.addTab(self.calibration_tab, "Calibration")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready for probing operations")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        
    def createEdgeTab(self):
        """Create the edge probing tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Left side - parameters and controls
        left_panel = QVBoxLayout()
        
        # Parameters group
        params_group = QGroupBox("Probe Parameters")
        params_layout = QGridLayout()
        
        # Probe diameter
        params_layout.addWidget(QLabel("Probe Diameter:"), 0, 0)
        self.edge_probe_dia = QDoubleSpinBox()
        self.edge_probe_dia.setRange(0.001, 1.0)
        self.edge_probe_dia.setValue(0.118)  # 3mm default
        self.edge_probe_dia.setSuffix(" in")
        params_layout.addWidget(self.edge_probe_dia, 0, 1)
        
        # Feed rates
        params_layout.addWidget(QLabel("Approach Feed:"), 1, 0)
        self.edge_approach_feed = QSpinBox()
        self.edge_approach_feed.setRange(1, 1000)
        self.edge_approach_feed.setValue(100)
        self.edge_approach_feed.setSuffix(" IPM")
        params_layout.addWidget(self.edge_approach_feed, 1, 1)
        
        params_layout.addWidget(QLabel("Probe Feed:"), 2, 0)
        self.edge_probe_feed = QSpinBox()
        self.edge_probe_feed.setRange(1, 100)
        self.edge_probe_feed.setValue(10)
        self.edge_probe_feed.setSuffix(" IPM")
        params_layout.addWidget(self.edge_probe_feed, 2, 1)
        
        # Distances
        params_layout.addWidget(QLabel("Clearance:"), 3, 0)
        self.edge_clearance = QDoubleSpinBox()
        self.edge_clearance.setRange(0.01, 5.0)
        self.edge_clearance.setValue(0.5)
        self.edge_clearance.setSuffix(" in")
        params_layout.addWidget(self.edge_clearance, 3, 1)
        
        params_layout.addWidget(QLabel("Retract:"), 4, 0)
        self.edge_retract = QDoubleSpinBox()
        self.edge_retract.setRange(0.01, 1.0)
        self.edge_retract.setValue(0.1)
        self.edge_retract.setSuffix(" in")
        params_layout.addWidget(self.edge_retract, 4, 1)
        
        # Direction selection
        params_layout.addWidget(QLabel("Direction:"), 5, 0)
        self.edge_direction = QComboBox()
        self.edge_direction.addItems(["X+", "X-", "Y+", "Y-"])
        self.edge_direction.currentIndexChanged.connect(self.updateEdgeDiagram)
        params_layout.addWidget(self.edge_direction, 5, 1)
        
        # WCS update option
        self.edge_update_wcs = QCheckBox("Update WCS")
        self.edge_update_wcs.setChecked(True)
        params_layout.addWidget(self.edge_update_wcs, 6, 0, 1, 2)
        
        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        
        # Safety checklist
        safety_group = QGroupBox("Safety Checklist")
        self.edge_safety = SafetyChecklist()
        self.edge_safety.checklistComplete.connect(lambda complete: self.edge_run_btn.setEnabled(complete))
        safety_group_layout = QVBoxLayout()
        safety_group_layout.addWidget(self.edge_safety)
        safety_group.setLayout(safety_group_layout)
        left_panel.addWidget(safety_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.edge_dry_run_btn = QPushButton("Dry Run")
        self.edge_dry_run_btn.clicked.connect(lambda: self.dryRunProbe("edge"))
        button_layout.addWidget(self.edge_dry_run_btn)
        
        self.edge_run_btn = QPushButton("Run Probe")
        self.edge_run_btn.setEnabled(False)
        self.edge_run_btn.clicked.connect(lambda: self.runProbe("edge"))
        button_layout.addWidget(self.edge_run_btn)
        
        left_panel.addLayout(button_layout)
        
        layout.addLayout(left_panel)
        
        # Right side - diagram
        right_panel = QVBoxLayout()
        diagram_group = QGroupBox("Probe Position")
        self.edge_diagram = ProbeDiagram()
        self.edge_diagram.setProbeType("edge", 0)
        diagram_layout = QVBoxLayout()
        diagram_layout.addWidget(self.edge_diagram)
        diagram_group.setLayout(diagram_layout)
        right_panel.addWidget(diagram_group)
        
        layout.addLayout(right_panel)
        tab.setLayout(layout)
        return tab
        
    def createCornerTab(self):
        """Create the corner probing tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Similar structure to edge tab but for corners
        # Left side - parameters
        left_panel = QVBoxLayout()
        
        params_group = QGroupBox("Corner Parameters")
        params_layout = QGridLayout()
        
        # Basic probe parameters
        params_layout.addWidget(QLabel("Probe Diameter:"), 0, 0)
        self.corner_probe_dia = QDoubleSpinBox()
        self.corner_probe_dia.setRange(0.001, 1.0)
        self.corner_probe_dia.setValue(0.118)
        self.corner_probe_dia.setSuffix(" in")
        params_layout.addWidget(self.corner_probe_dia, 0, 1)
        
        # Corner type
        params_layout.addWidget(QLabel("Corner Type:"), 1, 0)
        self.corner_type = QComboBox()
        self.corner_type.addItems(["Inside", "Outside"])
        params_layout.addWidget(self.corner_type, 1, 1)
        
        # Corner position
        params_layout.addWidget(QLabel("Position:"), 2, 0)
        self.corner_position = QComboBox()
        self.corner_position.addItems(["Front-Left", "Front-Right", "Back-Left", "Back-Right"])
        params_layout.addWidget(self.corner_position, 2, 1)
        
        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        
        # Right side - diagram
        right_panel = QVBoxLayout()
        self.corner_diagram = ProbeDiagram()
        self.corner_diagram.setProbeType("corner")
        right_panel.addWidget(self.corner_diagram)
        
        layout.addLayout(left_panel)
        layout.addLayout(right_panel)
        tab.setLayout(layout)
        return tab
        
    def createBossPocketTab(self):
        """Create the boss/pocket probing tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Similar structure for boss/pocket
        left_panel = QVBoxLayout()
        
        params_group = QGroupBox("Boss/Pocket Parameters")
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Feature Type:"), 0, 0)
        self.boss_pocket_type = QComboBox()
        self.boss_pocket_type.addItems(["Boss", "Pocket"])
        params_layout.addWidget(self.boss_pocket_type, 0, 1)
        
        params_layout.addWidget(QLabel("Approx. Size:"), 1, 0)
        self.boss_pocket_size = QDoubleSpinBox()
        self.boss_pocket_size.setRange(0.1, 10.0)
        self.boss_pocket_size.setValue(1.0)
        self.boss_pocket_size.setSuffix(" in")
        params_layout.addWidget(self.boss_pocket_size, 1, 1)
        
        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        
        layout.addLayout(left_panel)
        tab.setLayout(layout)
        return tab
        
    def createZTouchoffTab(self):
        """Create the Z touch-off tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        left_panel = QVBoxLayout()
        
        params_group = QGroupBox("Z Touch-off Parameters")
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Z Offset:"), 0, 0)
        self.z_offset = QDoubleSpinBox()
        self.z_offset.setRange(-5.0, 5.0)
        self.z_offset.setValue(0.0)
        self.z_offset.setSuffix(" in")
        params_layout.addWidget(self.z_offset, 0, 1)
        
        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        
        layout.addLayout(left_panel)
        tab.setLayout(layout)
        return tab
        
    def createToolsetterTab(self):
        """Create the tool setter tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Tool setter parameters
        params_group = QGroupBox("Tool Setter Parameters")
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Fast Probe Feed:"), 0, 0)
        self.tool_fast_feed = QSpinBox()
        self.tool_fast_feed.setRange(1, 500)
        self.tool_fast_feed.setValue(100)
        self.tool_fast_feed.setSuffix(" IPM")
        params_layout.addWidget(self.tool_fast_feed, 0, 1)
        
        params_layout.addWidget(QLabel("Slow Probe Feed:"), 1, 0)
        self.tool_slow_feed = QSpinBox()
        self.tool_slow_feed.setRange(0, 50)
        self.tool_slow_feed.setValue(10)
        self.tool_slow_feed.setSuffix(" IPM")
        params_layout.addWidget(self.tool_slow_feed, 1, 1)
        
        params_layout.addWidget(QLabel("Spindle Zero Height:"), 2, 0)
        self.spindle_zero = QDoubleSpinBox()
        self.spindle_zero.setRange(-10.0, 0.0)
        self.spindle_zero.setValue(-2.5)
        self.spindle_zero.setSuffix(" in")
        params_layout.addWidget(self.spindle_zero, 2, 1)
        
        # Breakage check
        self.enable_breakage_check = QCheckBox("Enable Breakage Check")
        params_layout.addWidget(self.enable_breakage_check, 3, 0, 1, 2)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Tool setter position
        position_group = QGroupBox("Tool Setter Position (G30)")
        position_layout = QHBoxLayout()
        
        self.set_g30_btn = QPushButton("Set Current Position as G30")
        self.set_g30_btn.clicked.connect(self.setG30Position)
        position_layout.addWidget(self.set_g30_btn)
        
        self.goto_g30_btn = QPushButton("Go to G30")
        self.goto_g30_btn.clicked.connect(self.gotoG30)
        position_layout.addWidget(self.goto_g30_btn)
        
        position_group.setLayout(position_layout)
        layout.addWidget(position_group)
        
        # Tool measurement
        measure_group = QGroupBox("Tool Measurement")
        measure_layout = QVBoxLayout()
        
        self.measure_tool_btn = QPushButton("Measure Current Tool")
        self.measure_tool_btn.clicked.connect(self.measureTool)
        measure_layout.addWidget(self.measure_tool_btn)
        
        measure_group.setLayout(measure_layout)
        layout.addWidget(measure_group)
        
        tab.setLayout(layout)
        return tab
        
    def createCalibrationTab(self):
        """Create the probe calibration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Calibration parameters
        params_group = QGroupBox("Calibration Parameters")
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Standard Diameter:"), 0, 0)
        self.cal_standard_dia = QDoubleSpinBox()
        self.cal_standard_dia.setRange(0.1, 10.0)
        self.cal_standard_dia.setValue(1.0)
        self.cal_standard_dia.setSuffix(" in")
        params_layout.addWidget(self.cal_standard_dia, 0, 1)
        
        params_layout.addWidget(QLabel("Standard Type:"), 1, 0)
        self.cal_standard_type = QComboBox()
        self.cal_standard_type.addItems(["Ring Gauge", "Pin Gauge"])
        params_layout.addWidget(self.cal_standard_type, 1, 1)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Calibration actions
        cal_group = QGroupBox("Calibration Actions")
        cal_layout = QVBoxLayout()
        
        self.calibrate_btn = QPushButton("Run Calibration")
        self.calibrate_btn.clicked.connect(self.runCalibration)
        cal_layout.addWidget(self.calibrate_btn)
        
        # Results display
        self.cal_results = QTextEdit()
        self.cal_results.setMaximumHeight(100)
        self.cal_results.setReadOnly(True)
        cal_layout.addWidget(self.cal_results)
        
        cal_group.setLayout(cal_layout)
        layout.addWidget(cal_group)
        
        tab.setLayout(layout)
        return tab
        
    def updateEdgeDiagram(self):
        """Update the edge probe diagram based on direction"""
        direction = self.edge_direction.currentIndex()
        self.edge_diagram.setProbeType("edge", direction)
        
    @pyqtSlot()
    def dryRunProbe(self, probe_type):
        """Run a dry-run preview of the probe operation"""
        self.status_label.setText(f"Dry run: {probe_type} probing preview")
        LOG.info(f"Dry run preview for {probe_type} probing")
        
        # TODO: Implement actual dry-run visualization
        # This would show the planned tool path without actually moving
        
    @pyqtSlot()
    def runProbe(self, probe_type):
        """Execute the actual probe operation"""
        self.status_label.setText(f"Running {probe_type} probe...")
        LOG.info(f"Executing {probe_type} probing operation")
        
        # Get parameters based on probe type
        if probe_type == "edge":
            params = self.getEdgeParameters()
            ngc_file = "edges.ngc"
        elif probe_type == "corner":
            params = self.getCornerParameters()
            ngc_file = "corners.ngc"
        elif probe_type == "boss_pocket":
            params = self.getBossPocketParameters()
            ngc_file = "boss_pocket.ngc"
        elif probe_type == "z_touchoff":
            params = self.getZTouchoffParameters()
            ngc_file = "z_touchoff.ngc"
        else:
            return
            
        # Set parameters in LinuxCNC
        self.setProbeParameters(params)
        
        # Execute the NGC macro
        self.executeNGCMacro(ngc_file)
        
    def getEdgeParameters(self):
        """Get edge probing parameters from UI"""
        return {
            3100: self.edge_probe_dia.value(),
            3101: self.edge_approach_feed.value(),
            3102: self.edge_probe_feed.value(),
            3103: self.edge_clearance.value(),
            3104: self.edge_retract.value(),
            3105: self.edge_direction.currentIndex(),
            3106: 1 if self.edge_update_wcs.isChecked() else 0
        }
        
    def getCornerParameters(self):
        """Get corner probing parameters from UI"""
        return {
            3110: self.corner_probe_dia.value(),
            3115: self.corner_type.currentIndex(),
            3116: self.corner_position.currentIndex(),
        }
        
    def getBossPocketParameters(self):
        """Get boss/pocket parameters from UI"""
        return {
            3125: self.boss_pocket_type.currentIndex(),
            3126: self.boss_pocket_size.value(),
        }
        
    def getZTouchoffParameters(self):
        """Get Z touch-off parameters from UI"""
        return {
            3135: self.z_offset.value(),
        }
        
    def setProbeParameters(self, params):
        """Set parameters in LinuxCNC parameter system"""
        # TODO: Implement parameter setting via LinuxCNC
        for param_num, value in params.items():
            LOG.info(f"Setting parameter #{param_num} = {value}")
            
    def executeNGCMacro(self, filename):
        """Execute NGC macro file"""
        # TODO: Implement NGC macro execution
        LOG.info(f"Executing NGC macro: {filename}")
        
    @pyqtSlot()
    def setG30Position(self):
        """Set current position as G30 (tool setter position)"""
        # TODO: Implement G30 position setting
        LOG.info("Setting current position as G30")
        
    @pyqtSlot()
    def gotoG30(self):
        """Move to G30 position"""
        # TODO: Implement G30 movement
        LOG.info("Moving to G30 position")
        
    @pyqtSlot()
    def measureTool(self):
        """Measure current tool length"""
        self.status_label.setText("Measuring tool length...")
        
        # Get tool setter parameters
        params = {
            3140: self.tool_fast_feed.value(),
            3141: self.tool_slow_feed.value(),
            3145: self.spindle_zero.value(),
            3147: 1 if self.enable_breakage_check.isChecked() else 0
        }
        
        self.setProbeParameters(params)
        self.executeNGCMacro("toolsetter.ngc")
        
    @pyqtSlot()
    def runCalibration(self):
        """Run probe calibration"""
        self.status_label.setText("Running probe calibration...")
        
        params = {
            3150: self.cal_standard_dia.value(),
            3155: self.cal_standard_type.currentIndex()
        }
        
        self.setProbeParameters(params)
        self.executeNGCMacro("probe_calibration.ngc")
        
        # TODO: Read back calibration results and display
        self.cal_results.setText("Calibration completed. Check results in parameters.")

# Widget extension for QtDesigner
class ProbingWizardsExtension(WidgetExtension):
    def pluginClass(self):
        return ProbingWizards
    
    def iconPath(self):
        return os.path.join(os.path.dirname(__file__), 'probing_wizards.png')