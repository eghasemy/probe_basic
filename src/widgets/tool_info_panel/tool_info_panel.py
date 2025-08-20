#!/usr/bin/env python

import os
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from qtpy.QtGui import QFont, QPixmap
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class ToolInfoPanel(QWidget):
    """
    Tool Info Panel Widget
    Displays active tool information: number, length, radius, notes, and toolpath preview
    Based on Phase 1 requirements
    """
    
    def __init__(self, parent=None):
        super(ToolInfoPanel, self).__init__(parent)
        
        self.status = getPlugin('status')
        self.tool_table = getPlugin('tooltable')
        
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.setupUI()
        self.connectSignals()
        
        # Update timer for tool info refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateToolInfo)
        self.update_timer.start(250)  # Update every 250ms
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("toolInfoPanel")
        self.setMinimumSize(300, 120)
        self.setMaximumSize(600, 200)
        
        # Main layout
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Left side: Tool information
        info_layout = QVBoxLayout()
        
        # Tool header
        header_layout = QHBoxLayout()
        
        tool_label = QLabel("ACTIVE TOOL")
        tool_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #00AAFF;")
        
        # Tool preview button (placeholder for Phase 1)
        self.preview_button = QPushButton("PREVIEW")
        self.preview_button.setMaximumSize(80, 25)
        self.preview_button.setToolTip("Show toolpath preview (Future implementation)")
        self.preview_button.setEnabled(False)  # Disabled for Phase 1
        self.preview_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                border: 1px solid #333;
                border-radius: 3px;
                color: white;
                font-size: 10px;
            }
        """)
        
        header_layout.addWidget(tool_label)
        header_layout.addStretch()
        header_layout.addWidget(self.preview_button)
        
        info_layout.addLayout(header_layout)
        
        # Tool details
        details_layout = QVBoxLayout()
        
        # Tool number and description
        self.tool_number_label = QLabel("Tool: T0")
        self.tool_number_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.tool_description_label = QLabel("No tool loaded")
        self.tool_description_label.setStyleSheet("color: #CCC; font-size: 11px;")
        self.tool_description_label.setWordWrap(True)
        
        details_layout.addWidget(self.tool_number_label)
        details_layout.addWidget(self.tool_description_label)
        
        # Tool measurements grid
        measurements_frame = QFrame()
        measurements_frame.setFrameStyle(QFrame.Box)
        measurements_frame.setLineWidth(1)
        measurements_frame.setStyleSheet("QFrame { border: 1px solid #555; border-radius: 3px; }")
        
        measurements_layout = QHBoxLayout()
        measurements_layout.setContentsMargins(5, 5, 5, 5)
        
        # Length column
        length_layout = QVBoxLayout()
        length_header = QLabel("LENGTH")
        length_header.setAlignment(Qt.AlignCenter)
        length_header.setStyleSheet("font-weight: bold; font-size: 10px; color: #AAA;")
        
        self.tool_length_label = QLabel("0.0000")
        self.tool_length_label.setAlignment(Qt.AlignCenter)
        self.tool_length_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #00FF88;")
        
        length_layout.addWidget(length_header)
        length_layout.addWidget(self.tool_length_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        
        # Radius column  
        radius_layout = QVBoxLayout()
        radius_header = QLabel("RADIUS")
        radius_header.setAlignment(Qt.AlignCenter)
        radius_header.setStyleSheet("font-weight: bold; font-size: 10px; color: #AAA;")
        
        self.tool_radius_label = QLabel("0.0000")
        self.tool_radius_label.setAlignment(Qt.AlignCenter)
        self.tool_radius_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #00FF88;")
        
        radius_layout.addWidget(radius_header)
        radius_layout.addWidget(self.tool_radius_label)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        
        # Diameter column
        diameter_layout = QVBoxLayout()
        diameter_header = QLabel("DIAMETER")
        diameter_header.setAlignment(Qt.AlignCenter)
        diameter_header.setStyleSheet("font-weight: bold; font-size: 10px; color: #AAA;")
        
        self.tool_diameter_label = QLabel("0.0000")
        self.tool_diameter_label.setAlignment(Qt.AlignCenter)
        self.tool_diameter_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #00FF88;")
        
        diameter_layout.addWidget(diameter_header)
        diameter_layout.addWidget(self.tool_diameter_label)
        
        measurements_layout.addLayout(length_layout)
        measurements_layout.addWidget(separator1)
        measurements_layout.addLayout(radius_layout)
        measurements_layout.addWidget(separator2)
        measurements_layout.addLayout(diameter_layout)
        
        measurements_frame.setLayout(measurements_layout)
        
        details_layout.addWidget(measurements_frame)
        details_layout.addStretch()
        
        info_layout.addLayout(details_layout)
        
        # Right side: Tool visual representation (placeholder)
        visual_frame = QFrame()
        visual_frame.setFrameStyle(QFrame.Box)
        visual_frame.setLineWidth(1)
        visual_frame.setMinimumSize(80, 80)
        visual_frame.setMaximumSize(120, 120)
        visual_frame.setStyleSheet("QFrame { border: 1px solid #555; border-radius: 3px; background-color: #333; }")
        
        visual_layout = QVBoxLayout()
        visual_layout.setContentsMargins(5, 5, 5, 5)
        
        # Tool icon placeholder
        self.tool_icon_label = QLabel("🔧")
        self.tool_icon_label.setAlignment(Qt.AlignCenter)
        self.tool_icon_label.setStyleSheet("font-size: 24px;")
        
        tool_visual_label = QLabel("Tool Visual")
        tool_visual_label.setAlignment(Qt.AlignCenter)
        tool_visual_label.setStyleSheet("font-size: 10px; color: #777;")
        
        visual_layout.addWidget(self.tool_icon_label)
        visual_layout.addWidget(tool_visual_label)
        
        visual_frame.setLayout(visual_layout)
        
        layout.addLayout(info_layout, 2)  # Give info more space
        layout.addWidget(visual_frame)
        
        self.setLayout(layout)
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.tool_in_spindle.notify(self.updateToolInfo)
            if self.tool_table:
                self.tool_table.current_tool.notify(self.updateToolInfo)
                
    def updateToolInfo(self):
        """Update tool information display"""
        if not self.status:
            return
            
        try:
            # Get current tool number
            current_tool = self.status.tool_in_spindle()
            
            self.tool_number_label.setText(f"Tool: T{current_tool}")
            
            # Get tool table information if available
            if self.tool_table and current_tool > 0:
                try:
                    tool_info = self.tool_table.getToolInfo(current_tool)
                    
                    # Update description/comment
                    comment = tool_info.get('comment', 'No description')
                    self.tool_description_label.setText(comment if comment else 'No description')
                    
                    # Update measurements
                    length = tool_info.get('Z', 0.0)
                    radius = tool_info.get('R', 0.0)
                    diameter = radius * 2.0
                    
                    # Format with appropriate precision
                    self.tool_length_label.setText(f"{length:.4f}")
                    self.tool_radius_label.setText(f"{radius:.4f}")
                    self.tool_diameter_label.setText(f"{diameter:.4f}")
                    
                    # Update tool icon based on tool type (simplified)
                    if 'drill' in comment.lower():
                        self.tool_icon_label.setText("🗳")
                    elif 'mill' in comment.lower() or 'end' in comment.lower():
                        self.tool_icon_label.setText("⚙")
                    elif 'tap' in comment.lower():
                        self.tool_icon_label.setText("🔩")
                    else:
                        self.tool_icon_label.setText("🔧")
                        
                except Exception as e:
                    LOG.error(f"Error getting tool info: {e}")
                    self.tool_description_label.setText("Tool data unavailable")
                    self.tool_length_label.setText("0.0000")
                    self.tool_radius_label.setText("0.0000") 
                    self.tool_diameter_label.setText("0.0000")
            else:
                # No tool or no tool table
                if current_tool == 0:
                    self.tool_description_label.setText("No tool loaded")
                else:
                    self.tool_description_label.setText("Tool table unavailable")
                    
                self.tool_length_label.setText("0.0000")
                self.tool_radius_label.setText("0.0000")
                self.tool_diameter_label.setText("0.0000")
                self.tool_icon_label.setText("❓")
                
        except Exception as e:
            LOG.error(f"Error updating tool info: {e}")