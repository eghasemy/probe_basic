#!/usr/bin/env python

"""
Dashboard Integration Example for Phase 1 Dashboard Parity
This file shows how to integrate the new dashboard widgets into the main UI
"""

import os
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qtpy.QtCore import Qt

# Import the new dashboard widgets
try:
    from widgets.modal_group_hud.modal_group_hud import ModalGroupHUD
    from widgets.status_tiles.status_tiles import StatusTiles
    from widgets.cycle_control_panel.cycle_control_panel import CycleControlPanel
    from widgets.alarms_panel.alarms_panel import AlarmsPanel
    from widgets.tool_info_panel.tool_info_panel import ToolInfoPanel
except ImportError as e:
    print(f"Widget import error: {e}")
    # Define placeholder classes for development
    class ModalGroupHUD(QWidget):
        pass
    class StatusTiles(QWidget): 
        pass
    class CycleControlPanel(QWidget):
        pass
    class AlarmsPanel(QWidget):
        pass
    class ToolInfoPanel(QWidget):
        pass

class DashboardContainer(QWidget):
    """
    Container widget that organizes all Phase 1 dashboard components
    This would be integrated into the main UI's MAIN tab
    """
    
    def __init__(self, parent=None):
        super(DashboardContainer, self).__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        """Set up the dashboard layout"""
        self.setObjectName("dashboardContainer")
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top row: Modal Groups HUD and Status Tiles
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        # Modal groups HUD
        self.modal_hud = ModalGroupHUD()
        top_row.addWidget(self.modal_hud)
        
        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        top_row.addWidget(separator1)
        
        # Status tiles
        self.status_tiles = StatusTiles()
        top_row.addWidget(self.status_tiles)
        
        main_layout.addLayout(top_row)
        
        # Add horizontal separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator2)
        
        # Second row: Tool Info Panel and Cycle Control Panel
        second_row = QHBoxLayout()
        second_row.setSpacing(10)
        
        # Tool info panel
        self.tool_info = ToolInfoPanel()
        second_row.addWidget(self.tool_info)
        
        # Add separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.VLine)
        separator3.setFrameShadow(QFrame.Sunken)
        second_row.addWidget(separator3)
        
        # Cycle controls
        self.cycle_controls = CycleControlPanel()
        second_row.addWidget(self.cycle_controls)
        
        main_layout.addLayout(second_row)
        
        # Add horizontal separator
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.HLine)
        separator4.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator4)
        
        # Bottom row: Alarms Panel
        self.alarms_panel = AlarmsPanel()
        main_layout.addWidget(self.alarms_panel)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
        
        self.setLayout(main_layout)

# Example of how this would be integrated into the main probe_basic.py
"""
Integration Instructions for probe_basic.py:

1. Import the DashboardContainer:
   from .dashboard_integration import DashboardContainer

2. In the ProbeBasic.__init__ method, after UI setup:
   # Add dashboard to main tab
   self.dashboard = DashboardContainer()
   # Insert into the main tab's layout at appropriate position
   # This would require modifying the main UI layout

3. The dashboard widgets automatically connect to LinuxCNC status
   and will update in real-time when the machine is running
"""