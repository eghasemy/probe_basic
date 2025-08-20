#!/usr/bin/env python

import os
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from qtpy.QtGui import QFont, QPixmap
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class StatusTiles(QWidget):
    """
    Status Tiles Widget
    Displays machine status indicators in a tile format
    Based on Phase 1 requirements: ESTOP, Machine On, Homed per axis, Limits, Probe present, Spindle state
    """
    
    def __init__(self, parent=None):
        super(StatusTiles, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.setupUI()
        self.connectSignals()
        
        # Update timer for refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateStatus)
        self.update_timer.start(100)  # Update every 100ms for responsive status
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("statusTiles")
        self.setMinimumSize(400, 120)
        self.setMaximumSize(800, 180)
        
        # Main layout
        layout = QGridLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create status tiles
        self.status_tiles = {}
        
        # Row 1: Core machine status
        self.addStatusTile("estop", "ESTOP", 0, 0, "#ff4444", "#darkred", "Emergency Stop Status")
        self.addStatusTile("machine_on", "MACHINE", 0, 1, "#44ff44", "#darkgreen", "Machine On Status") 
        self.addStatusTile("limits", "LIMITS", 0, 2, "#ffff44", "#darkorange", "Limit Switch Status")
        
        # Row 2: Axis homing status
        self.addStatusTile("home_x", "HOME X", 1, 0, "#44ddff", "#darkblue", "X Axis Homed")
        self.addStatusTile("home_y", "HOME Y", 1, 1, "#44ddff", "#darkblue", "Y Axis Homed")
        self.addStatusTile("home_z", "HOME Z", 1, 2, "#44ddff", "#darkblue", "Z Axis Homed")
        
        # Row 3: Spindle and probe status
        self.addStatusTile("spindle", "SPINDLE", 2, 0, "#dd44ff", "#darkmagenta", "Spindle Status")
        self.addStatusTile("probe", "PROBE", 2, 1, "#44ff88", "#darkgreen", "Probe Status")
        
        self.setLayout(layout)
        
    def addStatusTile(self, key, text, row, col, active_color, inactive_color, tooltip):
        """Add a status tile to the layout"""
        tile = QLabel(text)
        tile.setAlignment(Qt.AlignCenter)
        tile.setMinimumSize(80, 35)
        tile.setMaximumSize(120, 45)
        tile.setToolTip(tooltip)
        tile.setObjectName(f"status_{key}_tile")
        
        # Default inactive style
        tile.setStyleSheet(f"""
            QLabel {{
                background-color: {inactive_color};
                border: 2px solid #333;
                border-radius: 5px;
                color: #ffffff;
                font-weight: bold;
                font-size: 10px;
                padding: 3px;
            }}
        """)
        
        self.status_tiles[key] = {
            'widget': tile,
            'active_color': active_color,
            'inactive_color': inactive_color,
            'active': False
        }
        
        self.layout().addWidget(tile, row, col)
        
    def setTileActive(self, key, active):
        """Set a tile's active state"""
        if key not in self.status_tiles:
            return
            
        tile_info = self.status_tiles[key]
        if tile_info['active'] != active:
            tile_info['active'] = active
            tile = tile_info['widget']
            
            color = tile_info['active_color'] if active else tile_info['inactive_color']
            border_color = '#ffffff' if active else '#333'
            
            tile.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border: 2px solid {border_color};
                    border-radius: 5px;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 10px;
                    padding: 3px;
                }}
            """)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            # Connect to various status signals
            self.status.estop.notify(self.updateStatus)
            self.status.enabled.notify(self.updateStatus)
            self.status.homed.notify(self.updateStatus)
            self.status.limit.notify(self.updateStatus)
            self.status.spindle.notify(self.updateStatus)
            
    def updateStatus(self):
        """Update status tiles based on current LinuxCNC status"""
        if not self.status:
            return
            
        try:
            # Update ESTOP status (inverted - active when NOT in estop)
            estop_active = not self.status.estop()
            self.setTileActive("estop", estop_active)
            
            # Update Machine On status
            machine_on = self.status.enabled()
            self.setTileActive("machine_on", machine_on)
            
            # Update limit switch status (active when NOT triggered)
            limits_ok = not any(self.status.limit())
            self.setTileActive("limits", limits_ok)
            
            # Update homing status for each axis
            homed_status = self.status.homed()
            if len(homed_status) >= 3:  # Ensure we have at least X, Y, Z
                self.setTileActive("home_x", homed_status[0])
                self.setTileActive("home_y", homed_status[1])
                self.setTileActive("home_z", homed_status[2])
                
            # Update spindle status
            spindle_enabled = self.status.spindle()['enabled']
            self.setTileActive("spindle", spindle_enabled)
            
            # Update probe status (for now, just show if probe input is configured)
            # This is a placeholder - actual probe detection would need hardware configuration
            probe_present = True  # Assume probe is configured for now
            self.setTileActive("probe", probe_present)
            
        except Exception as e:
            LOG.error(f"Error updating status tiles: {e}")