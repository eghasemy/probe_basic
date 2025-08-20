#!/usr/bin/env python

import os
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from qtpy.QtGui import QFont
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class ModalGroupHUD(QWidget):
    """
    Modal Group HUD Widget
    Displays active G-code modal groups in a compact, at-a-glance format
    Based on Phase 1 requirements: G0/G1, G17/18/19, G90/91, G54–G59.3, G20/21, G40/41/42, G43/49
    """
    
    def __init__(self, parent=None):
        super(ModalGroupHUD, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.setupUI()
        self.connectSignals()
        
        # Update timer for refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateModalGroups)
        self.update_timer.start(250)  # Update every 250ms
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("modalGroupHUD")
        self.setMinimumSize(300, 80)
        self.setMaximumSize(600, 100)
        
        # Main layout
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create modal group labels
        self.modal_labels = {}
        
        # Row 1: Motion, Plane, Distance Mode
        self.addModalLabel("motion", "G0", 0, 0, "Motion Mode")
        self.addModalLabel("plane", "G17", 0, 1, "Plane Selection") 
        self.addModalLabel("distance", "G90", 0, 2, "Distance Mode")
        
        # Row 2: Coordinate System, Units, Cutter Compensation
        self.addModalLabel("coordinate", "G54", 1, 0, "Coordinate System")
        self.addModalLabel("units", "G20", 1, 1, "Units")
        self.addModalLabel("cutter_comp", "G40", 1, 2, "Cutter Compensation")
        
        # Row 3: Tool Length Compensation (optional - can expand)
        self.addModalLabel("tool_length", "G49", 2, 0, "Tool Length Compensation")
        
        self.setLayout(layout)
        
    def addModalLabel(self, key, default_text, row, col, tooltip):
        """Add a modal group label to the layout"""
        label = QLabel(default_text)
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(80, 25)
        label.setMaximumSize(120, 30)
        label.setToolTip(tooltip)
        label.setObjectName(f"modal_{key}_label")
        
        # Style the label
        label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
            }
            QLabel:hover {
                border-color: #007acc;
            }
        """)
        
        self.modal_labels[key] = label
        self.layout().addWidget(label, row, col)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.gcodes.notify(self.updateModalGroups)
            
    def updateModalGroups(self):
        """Update modal group displays based on current LinuxCNC status"""
        if not self.status:
            return
            
        try:
            # Get active G-codes
            gcodes = self.status.gcodes()
            
            # Update motion mode (G0, G1, G2, G3, etc.)
            motion_modes = [0, 1, 2, 3, 33, 73, 76, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
            motion_code = next((g for g in gcodes if (g // 10) in motion_modes), None)
            if motion_code is not None:
                self.modal_labels["motion"].setText(f"G{motion_code // 10}")
            
            # Update plane selection (G17, G18, G19)
            plane_modes = [17, 18, 19]
            plane_code = next((g for g in gcodes if (g // 10) in plane_modes), None)
            if plane_code is not None:
                self.modal_labels["plane"].setText(f"G{plane_code // 10}")
                
            # Update distance mode (G90, G91)
            distance_modes = [90, 91]
            distance_code = next((g for g in gcodes if (g // 10) in distance_modes), None) 
            if distance_code is not None:
                self.modal_labels["distance"].setText(f"G{distance_code // 10}")
                
            # Update coordinate system (G54-G59.3)
            coord_modes = [54, 55, 56, 57, 58, 59]
            coord_code = next((g for g in gcodes if (g // 10) in coord_modes), None)
            if coord_code is not None:
                if coord_code == 540:  # G54
                    self.modal_labels["coordinate"].setText("G54")
                elif coord_code == 550:  # G55
                    self.modal_labels["coordinate"].setText("G55")
                elif coord_code == 560:  # G56
                    self.modal_labels["coordinate"].setText("G56")
                elif coord_code == 570:  # G57
                    self.modal_labels["coordinate"].setText("G57")
                elif coord_code == 580:  # G58
                    self.modal_labels["coordinate"].setText("G58")
                elif coord_code == 590:  # G59
                    self.modal_labels["coordinate"].setText("G59")
                    
            # Update units (G20, G21)
            unit_modes = [20, 21]
            unit_code = next((g for g in gcodes if (g // 10) in unit_modes), None)
            if unit_code is not None:
                self.modal_labels["units"].setText(f"G{unit_code // 10}")
                
            # Update cutter compensation (G40, G41, G42)
            cutter_modes = [40, 41, 42]
            cutter_code = next((g for g in gcodes if (g // 10) in cutter_modes), None)
            if cutter_code is not None:
                self.modal_labels["cutter_comp"].setText(f"G{cutter_code // 10}")
                
            # Update tool length compensation (G43, G49)
            tool_length_modes = [43, 49]
            tool_length_code = next((g for g in gcodes if (g // 10) in tool_length_modes), None)
            if tool_length_code is not None:
                self.modal_labels["tool_length"].setText(f"G{tool_length_code // 10}")
                
        except Exception as e:
            LOG.error(f"Error updating modal groups: {e}")