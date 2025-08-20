#!/usr/bin/env python

"""
Tool Table Editor Widget - Phase 8 Implementation

A comprehensive widget for editing LinuxCNC tool.tbl with full CRUD operations,
CSV import/export, and bulk tool management functionality.

Key Features:
- Complete tool table editing (add, remove, modify)
- Tool radius, length, notes, and all parameters
- Bulk operations (clear all, import sets)
- CSV import/export for tool libraries
- Real-time tool.tbl persistence
- Integration with toolsetter results
"""

import os
import csv
import json
import shutil
from qtpy.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                           QLabel, QLineEdit, QPushButton, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QFileDialog, 
                           QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox,
                           QGroupBox, QTabWidget, QFrame, QTextEdit,
                           QCheckBox, QSplitter, QAbstractItemView)
from qtpy.QtGui import QFont, QValidator, QDoubleValidator, QIntValidator

try:
    from qtpyvcp.widgets.base_widgets.base_widget import VCPBaseWidget
    from qtpyvcp.plugins import getPlugin
    from qtpyvcp.utilities import logger
    HAS_QTPYVCP = True
except ImportError:
    # Fallback for testing without QtPyVCP
    HAS_QTPYVCP = False
    VCPBaseWidget = QWidget
    def getPlugin(name):
        return None

LOG = logger.getLogger(__name__) if HAS_QTPYVCP else None

class ToolTableEditor(VCPBaseWidget):
    """
    Tool Table Editor Widget for Phase 8
    
    Provides comprehensive tool.tbl editing with:
    - Full CRUD operations (Create, Read, Update, Delete)
    - Tool radius, length, notes editing
    - Bulk operations and management
    - CSV import/export functionality  
    - Real-time tool.tbl persistence
    """
    
    # Signals
    toolChanged = pyqtSignal(int)  # tool number
    toolAdded = pyqtSignal(int)    # tool number
    toolRemoved = pyqtSignal(int)  # tool number
    
    # Tool table columns
    COLUMNS = [
        ('Tool', 'T', 60, int),
        ('Pocket', 'P', 60, int), 
        ('Length', 'Z', 80, float),
        ('Radius', 'R', 80, float),
        ('Diameter', 'D', 80, float),
        ('Front Angle', 'A', 80, float),
        ('Back Angle', 'B', 80, float),
        ('Orientation', 'Q', 80, int),
        ('Notes', 'Comment', 200, str)
    ]
    
    def __init__(self, parent=None):
        super(ToolTableEditor, self).__init__(parent)
        
        # Get LinuxCNC plugins
        if HAS_QTPYVCP:
            self.status = getPlugin('status')
            self.tooltable = getPlugin('tooltable')
        else:
            self.status = None
            self.tooltable = None
            
        self.tool_data = {}  # Store tool table data
        self.tool_file_path = None
        self.unsaved_changes = False
        
        self.setupUI()
        self.connectSignals()
        
        # Load current tool table
        self.loadToolTable()
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("toolTableEditor")
        self.setMinimumSize(1000, 700)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title and status
        header_layout = QHBoxLayout()
        
        title = QLabel("Tool Table Editor")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2E86AB;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Tool file path display
        self.file_path_label = QLabel("No tool file loaded")
        self.file_path_label.setStyleSheet("color: #666; font-style: italic;")
        header_layout.addWidget(self.file_path_label)
        
        # Unsaved changes indicator
        self.unsaved_indicator = QLabel("●")
        self.unsaved_indicator.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
        self.unsaved_indicator.setVisible(False)
        header_layout.addWidget(self.unsaved_indicator)
        
        layout.addLayout(header_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Tool Table Tab
        self.table_tab = self.createToolTableTab()
        self.tab_widget.addTab(self.table_tab, "Tool Table")
        
        # Tool Details Tab  
        self.details_tab = self.createToolDetailsTab()
        self.tab_widget.addTab(self.details_tab, "Tool Details")
        
        # Bulk Operations Tab
        self.bulk_tab = self.createBulkOperationsTab()
        self.tab_widget.addTab(self.bulk_tab, "Bulk Operations")
        
        # Import/Export Tab
        self.import_export_tab = self.createImportExportTab()
        self.tab_widget.addTab(self.import_export_tab, "Import/Export")
        
        layout.addWidget(self.tab_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.new_tool_btn = QPushButton("Add Tool")
        self.new_tool_btn.clicked.connect(self.addNewTool)
        button_layout.addWidget(self.new_tool_btn)
        
        self.delete_tool_btn = QPushButton("Delete Tool")
        self.delete_tool_btn.clicked.connect(self.deleteTool)
        button_layout.addWidget(self.delete_tool_btn)
        
        self.reload_btn = QPushButton("Reload")
        self.reload_btn.clicked.connect(self.loadToolTable)
        button_layout.addWidget(self.reload_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Tool Table")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.saveToolTable)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def createToolTableTab(self):
        """Create the main tool table tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Current tool display
        current_tool_layout = QHBoxLayout()
        current_tool_layout.addWidget(QLabel("Current Tool:"))
        self.current_tool_label = QLabel("T0")
        self.current_tool_label.setStyleSheet("font-weight: bold; color: #2E86AB;")
        current_tool_layout.addWidget(self.current_tool_label)
        current_tool_layout.addStretch()
        
        # Filter/search
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search tools...")
        self.filter_edit.textChanged.connect(self.filterTools)
        filter_layout.addWidget(self.filter_edit)
        
        current_tool_layout.addLayout(filter_layout)
        layout.addLayout(current_tool_layout)
        
        # Tool table
        self.tool_table = QTableWidget()
        self.tool_table.setColumnCount(len(self.COLUMNS))
        
        # Set headers and column widths
        headers = [col[0] for col in self.COLUMNS]
        self.tool_table.setHorizontalHeaderLabels(headers)
        
        for i, (_, _, width, _) in enumerate(self.COLUMNS):
            self.tool_table.setColumnWidth(i, width)
        
        # Configure table
        self.tool_table.setAlternatingRowColors(True)
        self.tool_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tool_table.setSortingEnabled(True)
        
        # Connect selection change
        self.tool_table.itemSelectionChanged.connect(self.onToolSelectionChanged)
        self.tool_table.itemChanged.connect(self.onToolDataChanged)
        
        layout.addWidget(self.tool_table)
        
        widget.setLayout(layout)
        return widget
        
    def createToolDetailsTab(self):
        """Create the tool details editing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Selected tool info
        selected_layout = QHBoxLayout()
        selected_layout.addWidget(QLabel("Selected Tool:"))
        self.selected_tool_label = QLabel("None")
        self.selected_tool_label.setStyleSheet("font-weight: bold; color: #2E86AB;")
        selected_layout.addWidget(self.selected_tool_label)
        selected_layout.addStretch()
        layout.addLayout(selected_layout)
        
        # Tool details form
        details_group = QGroupBox("Tool Parameters")
        details_layout = QGridLayout()
        
        # Create input fields for each parameter
        self.detail_inputs = {}
        
        # Tool number (read-only when editing existing)
        details_layout.addWidget(QLabel("Tool Number:"), 0, 0)
        self.detail_inputs['tool'] = QSpinBox()
        self.detail_inputs['tool'].setRange(0, 99999)
        details_layout.addWidget(self.detail_inputs['tool'], 0, 1)
        
        # Pocket number
        details_layout.addWidget(QLabel("Pocket:"), 0, 2)
        self.detail_inputs['pocket'] = QSpinBox()
        self.detail_inputs['pocket'].setRange(0, 99999)
        details_layout.addWidget(self.detail_inputs['pocket'], 0, 3)
        
        # Length offset
        details_layout.addWidget(QLabel("Length Offset (Z):"), 1, 0)
        self.detail_inputs['length'] = QDoubleSpinBox()
        self.detail_inputs['length'].setRange(-999.999, 999.999)
        self.detail_inputs['length'].setDecimals(4)
        self.detail_inputs['length'].setSuffix(" mm")
        details_layout.addWidget(self.detail_inputs['length'], 1, 1)
        
        # Radius
        details_layout.addWidget(QLabel("Radius:"), 1, 2)
        self.detail_inputs['radius'] = QDoubleSpinBox()
        self.detail_inputs['radius'].setRange(0.0, 999.999)
        self.detail_inputs['radius'].setDecimals(4)
        self.detail_inputs['radius'].setSuffix(" mm")
        details_layout.addWidget(self.detail_inputs['radius'], 1, 3)
        
        # Diameter (computed from radius)
        details_layout.addWidget(QLabel("Diameter:"), 2, 0)
        self.detail_inputs['diameter'] = QDoubleSpinBox()
        self.detail_inputs['diameter'].setRange(0.0, 999.999)
        self.detail_inputs['diameter'].setDecimals(4)
        self.detail_inputs['diameter'].setSuffix(" mm")
        self.detail_inputs['diameter'].setReadOnly(True)  # Computed field
        details_layout.addWidget(self.detail_inputs['diameter'], 2, 1)
        
        # Connect radius to diameter
        self.detail_inputs['radius'].valueChanged.connect(
            lambda v: self.detail_inputs['diameter'].setValue(v * 2.0))
        
        # Front angle
        details_layout.addWidget(QLabel("Front Angle:"), 2, 2)
        self.detail_inputs['front_angle'] = QDoubleSpinBox()
        self.detail_inputs['front_angle'].setRange(-180.0, 180.0)
        self.detail_inputs['front_angle'].setDecimals(2)
        self.detail_inputs['front_angle'].setSuffix("°")
        details_layout.addWidget(self.detail_inputs['front_angle'], 2, 3)
        
        # Back angle
        details_layout.addWidget(QLabel("Back Angle:"), 3, 0)
        self.detail_inputs['back_angle'] = QDoubleSpinBox()
        self.detail_inputs['back_angle'].setRange(-180.0, 180.0)
        self.detail_inputs['back_angle'].setDecimals(2)
        self.detail_inputs['back_angle'].setSuffix("°")
        details_layout.addWidget(self.detail_inputs['back_angle'], 3, 1)
        
        # Orientation
        details_layout.addWidget(QLabel("Orientation:"), 3, 2)
        self.detail_inputs['orientation'] = QSpinBox()
        self.detail_inputs['orientation'].setRange(0, 9)
        details_layout.addWidget(self.detail_inputs['orientation'], 3, 3)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Notes section
        notes_group = QGroupBox("Tool Notes")
        notes_layout = QVBoxLayout()
        
        self.detail_inputs['notes'] = QTextEdit()
        self.detail_inputs['notes'].setMaximumHeight(100)
        self.detail_inputs['notes'].setPlaceholderText("Tool description, material, speeds, etc...")
        notes_layout.addWidget(self.detail_inputs['notes'])
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Detail control buttons
        detail_button_layout = QHBoxLayout()
        
        self.clear_details_btn = QPushButton("Clear")
        self.clear_details_btn.clicked.connect(self.clearToolDetails)
        detail_button_layout.addWidget(self.clear_details_btn)
        
        detail_button_layout.addStretch()
        
        self.apply_details_btn = QPushButton("Apply Changes")
        self.apply_details_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        self.apply_details_btn.clicked.connect(self.applyToolDetails)
        detail_button_layout.addWidget(self.apply_details_btn)
        
        layout.addLayout(detail_button_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def createBulkOperationsTab(self):
        """Create the bulk operations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Clear operations
        clear_group = QGroupBox("Clear Operations")
        clear_layout = QVBoxLayout()
        
        clear_desc = QLabel("Remove multiple tools or reset all tool data")
        clear_desc.setStyleSheet("color: #666; font-style: italic;")
        clear_layout.addWidget(clear_desc)
        
        clear_button_layout = QHBoxLayout()
        
        self.clear_all_btn = QPushButton("Clear All Tools")
        self.clear_all_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.clear_all_btn.clicked.connect(self.clearAllTools)
        clear_button_layout.addWidget(self.clear_all_btn)
        
        self.clear_unused_btn = QPushButton("Clear Unused Tools")
        self.clear_unused_btn.clicked.connect(self.clearUnusedTools)
        clear_button_layout.addWidget(self.clear_unused_btn)
        
        clear_layout.addLayout(clear_button_layout)
        clear_group.setLayout(clear_layout)
        layout.addWidget(clear_group)
        
        # Tool range operations
        range_group = QGroupBox("Range Operations")
        range_layout = QGridLayout()
        
        range_layout.addWidget(QLabel("From Tool:"), 0, 0)
        self.range_from = QSpinBox()
        self.range_from.setRange(1, 99999)
        self.range_from.setValue(1)
        range_layout.addWidget(self.range_from, 0, 1)
        
        range_layout.addWidget(QLabel("To Tool:"), 0, 2)
        self.range_to = QSpinBox()
        self.range_to.setRange(1, 99999)
        self.range_to.setValue(10)
        range_layout.addWidget(self.range_to, 0, 3)
        
        range_button_layout = QHBoxLayout()
        
        self.auto_number_btn = QPushButton("Auto-Number Range")
        self.auto_number_btn.clicked.connect(self.autoNumberRange)
        range_button_layout.addWidget(self.auto_number_btn)
        
        self.clear_range_btn = QPushButton("Clear Range")
        self.clear_range_btn.clicked.connect(self.clearToolRange)
        range_button_layout.addWidget(self.clear_range_btn)
        
        range_layout.addLayout(range_button_layout, 1, 0, 1, 4)
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        # Default tool creation
        default_group = QGroupBox("Default Tool Creation")
        default_layout = QGridLayout()
        
        default_layout.addWidget(QLabel("Tool Count:"), 0, 0)
        self.default_count = QSpinBox()
        self.default_count.setRange(1, 100)
        self.default_count.setValue(10)
        default_layout.addWidget(self.default_count, 0, 1)
        
        default_layout.addWidget(QLabel("Default Diameter:"), 0, 2)
        self.default_diameter = QDoubleSpinBox()
        self.default_diameter.setRange(0.1, 50.0)
        self.default_diameter.setValue(6.0)
        self.default_diameter.setSuffix(" mm")
        default_layout.addWidget(self.default_diameter, 0, 3)
        
        self.create_defaults_btn = QPushButton("Create Default Tools")
        self.create_defaults_btn.clicked.connect(self.createDefaultTools)
        default_layout.addWidget(self.create_defaults_btn, 1, 0, 1, 4)
        
        default_group.setLayout(default_layout)
        layout.addWidget(default_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def createImportExportTab(self):
        """Create the import/export tab for CSV operations"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Export section
        export_group = QGroupBox("Export Tool Table")
        export_layout = QVBoxLayout()
        
        export_desc = QLabel("Export tool table to CSV for backup or sharing")
        export_desc.setStyleSheet("color: #666; font-style: italic;")
        export_layout.addWidget(export_desc)
        
        export_button_layout = QHBoxLayout()
        
        self.export_all_tools_btn = QPushButton("Export All Tools")
        self.export_all_tools_btn.clicked.connect(self.exportAllTools)
        export_button_layout.addWidget(self.export_all_tools_btn)
        
        self.export_used_tools_btn = QPushButton("Export Used Tools Only")
        self.export_used_tools_btn.clicked.connect(self.exportUsedTools)
        export_button_layout.addWidget(self.export_used_tools_btn)
        
        export_layout.addLayout(export_button_layout)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Import section
        import_group = QGroupBox("Import Tool Table")
        import_layout = QVBoxLayout()
        
        import_desc = QLabel("Import tools from CSV file (will add to existing tools)")
        import_desc.setStyleSheet("color: #666; font-style: italic;")
        import_layout.addWidget(import_desc)
        
        import_options_layout = QHBoxLayout()
        self.overwrite_existing = QCheckBox("Overwrite Existing Tools")
        self.overwrite_existing.setChecked(False)
        import_options_layout.addWidget(self.overwrite_existing)
        import_options_layout.addStretch()
        import_layout.addLayout(import_options_layout)
        
        import_button_layout = QHBoxLayout()
        
        self.import_tools_btn = QPushButton("Import from CSV")
        self.import_tools_btn.clicked.connect(self.importToolsFromCSV)
        import_button_layout.addWidget(self.import_tools_btn)
        
        self.validate_tool_csv_btn = QPushButton("Validate CSV")
        self.validate_tool_csv_btn.clicked.connect(self.validateToolCSV)
        import_button_layout.addWidget(self.validate_tool_csv_btn)
        
        import_layout.addLayout(import_button_layout)
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def connectSignals(self):
        """Connect LinuxCNC signals"""
        if self.status:
            # Connect to tool changes
            # self.status.tool_in_spindle.notify.connect(self.updateCurrentTool)
            pass
            
    def loadToolTable(self):
        """Load tool table from LinuxCNC"""
        try:
            # TODO: Get tool table path from LinuxCNC configuration
            # For now, use a default path
            tool_file = "/tmp/tool.tbl"  # Placeholder
            
            if os.path.exists(tool_file):
                self.tool_file_path = tool_file
                self.file_path_label.setText(f"File: {tool_file}")
                self._loadToolFile(tool_file)
            else:
                # Create empty tool table
                self.tool_data = {}
                self._populateToolTable()
                
            self.markSaved()
            
        except Exception as e:
            if LOG:
                LOG.error(f"Error loading tool table: {e}")
            QMessageBox.warning(self, "Warning", 
                              f"Could not load tool table: {e}")
    
    def _loadToolFile(self, filename):
        """Load tool table from file"""
        self.tool_data = {}
        
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith(';'):
                        continue
                        
                    # Parse tool line: T1 P1 Z0.0 R0.5 ; comment
                    parts = line.split(';', 1)
                    tool_def = parts[0].strip()
                    comment = parts[1].strip() if len(parts) > 1 else ""
                    
                    # Parse tool parameters
                    tool_params = self._parseToolDefinition(tool_def)
                    if tool_params:
                        tool_params['comment'] = comment
                        tool_num = tool_params.get('T', 0)
                        if tool_num > 0:
                            self.tool_data[tool_num] = tool_params
                            
        except Exception as e:
            if LOG:
                LOG.error(f"Error parsing tool file: {e}")
            raise
            
        self._populateToolTable()
    
    def _parseToolDefinition(self, tool_def):
        """Parse a tool definition line"""
        params = {}
        
        # Split into parameter parts
        parts = tool_def.split()
        
        for part in parts:
            if len(part) < 2:
                continue
                
            param_char = part[0].upper()
            param_value = part[1:]
            
            try:
                if param_char in ['T', 'P', 'Q']:  # Integer parameters
                    params[param_char] = int(param_value)
                elif param_char in ['Z', 'R', 'D', 'A', 'B']:  # Float parameters
                    params[param_char] = float(param_value)
            except ValueError:
                continue
                
        return params if 'T' in params else None
    
    def _populateToolTable(self):
        """Populate the tool table widget"""
        self.tool_table.setRowCount(len(self.tool_data))
        
        # Disconnect signals temporarily
        self.tool_table.itemChanged.disconnect()
        
        row = 0
        for tool_num in sorted(self.tool_data.keys()):
            tool = self.tool_data[tool_num]
            
            # Tool number
            self.tool_table.setItem(row, 0, QTableWidgetItem(str(tool_num)))
            
            # Pocket
            pocket = tool.get('P', tool_num)
            self.tool_table.setItem(row, 1, QTableWidgetItem(str(pocket)))
            
            # Length
            length = tool.get('Z', 0.0)
            self.tool_table.setItem(row, 2, QTableWidgetItem(f"{length:.4f}"))
            
            # Radius
            radius = tool.get('R', 0.0)
            self.tool_table.setItem(row, 3, QTableWidgetItem(f"{radius:.4f}"))
            
            # Diameter
            diameter = tool.get('D', radius * 2.0)
            self.tool_table.setItem(row, 4, QTableWidgetItem(f"{diameter:.4f}"))
            
            # Front angle
            front_angle = tool.get('A', 0.0)
            self.tool_table.setItem(row, 5, QTableWidgetItem(f"{front_angle:.2f}"))
            
            # Back angle
            back_angle = tool.get('B', 0.0)
            self.tool_table.setItem(row, 6, QTableWidgetItem(f"{back_angle:.2f}"))
            
            # Orientation
            orientation = tool.get('Q', 0)
            self.tool_table.setItem(row, 7, QTableWidgetItem(str(orientation)))
            
            # Notes
            notes = tool.get('comment', '')
            self.tool_table.setItem(row, 8, QTableWidgetItem(notes))
            
            row += 1
            
        # Reconnect signals
        self.tool_table.itemChanged.connect(self.onToolDataChanged)
        
        # Update current tool display
        if self.status:
            # current_tool = self.status.tool_in_spindle
            # self.current_tool_label.setText(f"T{current_tool}")
            pass
    
    @pyqtSlot()
    def onToolSelectionChanged(self):
        """Handle tool selection changes"""
        current_row = self.tool_table.currentRow()
        if current_row >= 0:
            tool_item = self.tool_table.item(current_row, 0)
            if tool_item:
                tool_num = int(tool_item.text())
                self.selected_tool_label.setText(f"T{tool_num}")
                self._loadToolDetails(tool_num)
    
    def _loadToolDetails(self, tool_num):
        """Load tool details into the details tab"""
        if tool_num in self.tool_data:
            tool = self.tool_data[tool_num]
            
            # Disconnect signals temporarily
            for input_widget in self.detail_inputs.values():
                if hasattr(input_widget, 'valueChanged'):
                    input_widget.valueChanged.disconnect()
                elif hasattr(input_widget, 'textChanged'):
                    input_widget.textChanged.disconnect()
            
            # Load values
            self.detail_inputs['tool'].setValue(tool_num)
            self.detail_inputs['pocket'].setValue(tool.get('P', tool_num))
            self.detail_inputs['length'].setValue(tool.get('Z', 0.0))
            self.detail_inputs['radius'].setValue(tool.get('R', 0.0))
            self.detail_inputs['diameter'].setValue(tool.get('D', tool.get('R', 0.0) * 2.0))
            self.detail_inputs['front_angle'].setValue(tool.get('A', 0.0))
            self.detail_inputs['back_angle'].setValue(tool.get('B', 0.0))
            self.detail_inputs['orientation'].setValue(tool.get('Q', 0))
            self.detail_inputs['notes'].setPlainText(tool.get('comment', ''))
            
            # Reconnect signals
            self.detail_inputs['radius'].valueChanged.connect(
                lambda v: self.detail_inputs['diameter'].setValue(v * 2.0))
    
    @pyqtSlot(QTableWidgetItem)
    def onToolDataChanged(self, item):
        """Handle changes to tool data in table"""
        row = item.row()
        col = item.column()
        
        # Get tool number from first column
        tool_item = self.tool_table.item(row, 0)
        if not tool_item:
            return
            
        try:
            tool_num = int(tool_item.text())
            
            # Update tool data
            if tool_num not in self.tool_data:
                self.tool_data[tool_num] = {'T': tool_num}
            
            # Update specific parameter based on column
            col_name, param_char, _, data_type = self.COLUMNS[col]
            
            if data_type == int:
                value = int(item.text())
            elif data_type == float:
                value = float(item.text())
            else:
                value = item.text()
            
            if param_char == 'Comment':
                self.tool_data[tool_num]['comment'] = value
            else:
                self.tool_data[tool_num][param_char] = value
            
            self.markUnsaved()
            self.toolChanged.emit(tool_num)
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", 
                              f"Invalid value for {self.COLUMNS[col][0]}: {e}")
            # Revert to previous value
            if tool_num in self.tool_data:
                tool = self.tool_data[tool_num]
                col_name, param_char, _, data_type = self.COLUMNS[col]
                if param_char == 'Comment':
                    prev_value = tool.get('comment', '')
                else:
                    prev_value = tool.get(param_char, 0)
                item.setText(str(prev_value))
    
    @pyqtSlot()
    def addNewTool(self):
        """Add a new tool to the table"""
        # Find next available tool number
        if self.tool_data:
            next_tool = max(self.tool_data.keys()) + 1
        else:
            next_tool = 1
        
        # Add new tool with defaults
        self.tool_data[next_tool] = {
            'T': next_tool,
            'P': next_tool,
            'Z': 0.0,
            'R': 3.0,  # Default 6mm diameter
            'D': 6.0,
            'A': 0.0,
            'B': 0.0,
            'Q': 0,
            'comment': f'Tool {next_tool}'
        }
        
        self._populateToolTable()
        self.markUnsaved()
        self.toolAdded.emit(next_tool)
        
        # Select the new tool
        for row in range(self.tool_table.rowCount()):
            item = self.tool_table.item(row, 0)
            if item and int(item.text()) == next_tool:
                self.tool_table.selectRow(row)
                break
    
    @pyqtSlot()
    def deleteTool(self):
        """Delete selected tool"""
        current_row = self.tool_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "No Selection", 
                                  "Please select a tool to delete.")
            return
        
        tool_item = self.tool_table.item(current_row, 0)
        if not tool_item:
            return
            
        tool_num = int(tool_item.text())
        
        reply = QMessageBox.question(self, "Delete Tool", 
                                   f"Are you sure you want to delete Tool T{tool_num}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if tool_num in self.tool_data:
                del self.tool_data[tool_num]
                self._populateToolTable()
                self.markUnsaved()
                self.toolRemoved.emit(tool_num)
    
    @pyqtSlot()
    def clearToolDetails(self):
        """Clear all tool detail inputs"""
        for key, input_widget in self.detail_inputs.items():
            if hasattr(input_widget, 'setValue'):
                input_widget.setValue(0)
            elif hasattr(input_widget, 'setPlainText'):
                input_widget.setPlainText('')
                
        self.selected_tool_label.setText("None")
    
    @pyqtSlot()
    def applyToolDetails(self):
        """Apply tool details to the tool table"""
        tool_num = self.detail_inputs['tool'].value()
        
        if tool_num <= 0:
            QMessageBox.warning(self, "Invalid Tool", 
                              "Tool number must be greater than 0.")
            return
        
        # Create or update tool
        tool_data = {
            'T': tool_num,
            'P': self.detail_inputs['pocket'].value(),
            'Z': self.detail_inputs['length'].value(),
            'R': self.detail_inputs['radius'].value(),
            'D': self.detail_inputs['diameter'].value(),
            'A': self.detail_inputs['front_angle'].value(),
            'B': self.detail_inputs['back_angle'].value(),
            'Q': self.detail_inputs['orientation'].value(),
            'comment': self.detail_inputs['notes'].toPlainText()
        }
        
        self.tool_data[tool_num] = tool_data
        self._populateToolTable()
        self.markUnsaved()
        self.toolChanged.emit(tool_num)
        
        QMessageBox.information(self, "Success", 
                              f"Tool T{tool_num} updated successfully.")
    
    @pyqtSlot()
    def filterTools(self):
        """Filter tools based on search text"""
        filter_text = self.filter_edit.text().lower()
        
        for row in range(self.tool_table.rowCount()):
            show_row = False
            
            # Check each column for match
            for col in range(self.tool_table.columnCount()):
                item = self.tool_table.item(row, col)
                if item and filter_text in item.text().lower():
                    show_row = True
                    break
            
            self.tool_table.setRowHidden(row, not show_row)
    
    @pyqtSlot()
    def clearAllTools(self):
        """Clear all tools from the table"""
        reply = QMessageBox.question(self, "Clear All Tools", 
                                   "Are you sure you want to delete ALL tools?\n"
                                   "This cannot be undone!",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.tool_data.clear()
            self._populateToolTable()
            self.markUnsaved()
    
    @pyqtSlot()
    def clearUnusedTools(self):
        """Clear tools that have default values"""
        removed_count = 0
        to_remove = []
        
        for tool_num, tool in self.tool_data.items():
            # Consider unused if length and radius are both 0
            if tool.get('Z', 0.0) == 0.0 and tool.get('R', 0.0) == 0.0:
                to_remove.append(tool_num)
        
        if to_remove:
            reply = QMessageBox.question(self, "Clear Unused Tools", 
                                       f"Remove {len(to_remove)} unused tools?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                for tool_num in to_remove:
                    del self.tool_data[tool_num]
                    removed_count += 1
                
                self._populateToolTable()
                self.markUnsaved()
                
                QMessageBox.information(self, "Success", 
                                      f"Removed {removed_count} unused tools.")
        else:
            QMessageBox.information(self, "No Unused Tools", 
                                  "No unused tools found.")
    
    @pyqtSlot()
    def autoNumberRange(self):
        """Auto-number tools in a range"""
        from_tool = self.range_from.value()
        to_tool = self.range_to.value()
        
        if from_tool > to_tool:
            QMessageBox.warning(self, "Invalid Range", 
                              "From tool must be less than or equal to To tool.")
            return
        
        for tool_num in range(from_tool, to_tool + 1):
            if tool_num not in self.tool_data:
                self.tool_data[tool_num] = {
                    'T': tool_num,
                    'P': tool_num,
                    'Z': 0.0,
                    'R': 3.0,
                    'D': 6.0,
                    'A': 0.0,
                    'B': 0.0,
                    'Q': 0,
                    'comment': f'Tool {tool_num}'
                }
        
        self._populateToolTable()
        self.markUnsaved()
        
        QMessageBox.information(self, "Success", 
                              f"Created tools T{from_tool} to T{to_tool}.")
    
    @pyqtSlot()
    def clearToolRange(self):
        """Clear tools in a range"""
        from_tool = self.range_from.value()
        to_tool = self.range_to.value()
        
        if from_tool > to_tool:
            QMessageBox.warning(self, "Invalid Range", 
                              "From tool must be less than or equal to To tool.")
            return
        
        reply = QMessageBox.question(self, "Clear Tool Range", 
                                   f"Delete tools T{from_tool} to T{to_tool}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            removed_count = 0
            for tool_num in range(from_tool, to_tool + 1):
                if tool_num in self.tool_data:
                    del self.tool_data[tool_num]
                    removed_count += 1
            
            self._populateToolTable()
            self.markUnsaved()
            
            QMessageBox.information(self, "Success", 
                                  f"Removed {removed_count} tools.")
    
    @pyqtSlot()
    def createDefaultTools(self):
        """Create default tools with specified parameters"""
        count = self.default_count.value()
        diameter = self.default_diameter.value()
        radius = diameter / 2.0
        
        # Find starting tool number
        if self.tool_data:
            start_tool = max(self.tool_data.keys()) + 1
        else:
            start_tool = 1
        
        for i in range(count):
            tool_num = start_tool + i
            self.tool_data[tool_num] = {
                'T': tool_num,
                'P': tool_num,
                'Z': 0.0,
                'R': radius,
                'D': diameter,
                'A': 0.0,
                'B': 0.0,
                'Q': 0,
                'comment': f'{diameter}mm End Mill'
            }
        
        self._populateToolTable()
        self.markUnsaved()
        
        QMessageBox.information(self, "Success", 
                              f"Created {count} default tools (T{start_tool} to T{start_tool + count - 1}).")
    
    @pyqtSlot()
    def saveToolTable(self):
        """Save tool table to file"""
        if not self.tool_file_path:
            # Choose save location
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Tool Table", 
                "tool.tbl", "Tool Table Files (*.tbl);;All Files (*)")
            
            if not filename:
                return
                
            self.tool_file_path = filename
            self.file_path_label.setText(f"File: {filename}")
        
        try:
            # Backup existing file
            if os.path.exists(self.tool_file_path):
                backup_path = self.tool_file_path + ".backup"
                shutil.copy2(self.tool_file_path, backup_path)
            
            # Write tool table
            with open(self.tool_file_path, 'w') as f:
                f.write("; Tool table file\n")
                f.write("; Format: T<tool> P<pocket> Z<length> R<radius> D<diameter> A<front_angle> B<back_angle> Q<orientation> ; <comment>\n")
                f.write(";\n")
                
                for tool_num in sorted(self.tool_data.keys()):
                    tool = self.tool_data[tool_num]
                    
                    line = f"T{tool_num}"
                    if 'P' in tool: line += f" P{tool['P']}"
                    if 'Z' in tool: line += f" Z{tool['Z']:.4f}"
                    if 'R' in tool: line += f" R{tool['R']:.4f}"
                    if 'D' in tool: line += f" D{tool['D']:.4f}"
                    if 'A' in tool: line += f" A{tool['A']:.2f}"
                    if 'B' in tool: line += f" B{tool['B']:.2f}"
                    if 'Q' in tool: line += f" Q{tool['Q']}"
                    
                    comment = tool.get('comment', '')
                    if comment:
                        line += f" ; {comment}"
                    
                    f.write(line + "\n")
            
            # TODO: Reload tool table in LinuxCNC
            self.markSaved()
            
            QMessageBox.information(self, "Success", 
                                  f"Tool table saved to {self.tool_file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to save tool table: {e}")
    
    @pyqtSlot()
    def exportAllTools(self):
        """Export all tools to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export All Tools", 
            "tool_table.csv", "CSV Files (*.csv)")
        
        if filename:
            try:
                self._exportToolsToCSV(filename, all_tools=True)
                QMessageBox.information(self, "Success", 
                                      f"All tools exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to export: {e}")
    
    @pyqtSlot()
    def exportUsedTools(self):
        """Export only used tools (non-zero length or radius) to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Used Tools", 
            "used_tools.csv", "CSV Files (*.csv)")
        
        if filename:
            try:
                self._exportToolsToCSV(filename, all_tools=False)
                QMessageBox.information(self, "Success", 
                                      f"Used tools exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to export: {e}")
    
    def _exportToolsToCSV(self, filename, all_tools=True):
        """Export tools to CSV file"""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            headers = [col[0] for col in self.COLUMNS]
            writer.writerow(headers)
            
            # Write tool data
            for tool_num in sorted(self.tool_data.keys()):
                tool = self.tool_data[tool_num]
                
                # Skip unused tools if requested
                if not all_tools:
                    if tool.get('Z', 0.0) == 0.0 and tool.get('R', 0.0) == 0.0:
                        continue
                
                row_data = [
                    tool_num,
                    tool.get('P', tool_num),
                    tool.get('Z', 0.0),
                    tool.get('R', 0.0),
                    tool.get('D', tool.get('R', 0.0) * 2.0),
                    tool.get('A', 0.0),
                    tool.get('B', 0.0),
                    tool.get('Q', 0),
                    tool.get('comment', '')
                ]
                
                writer.writerow(row_data)
    
    @pyqtSlot()
    def importToolsFromCSV(self):
        """Import tools from CSV file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Tools from CSV", 
            "", "CSV Files (*.csv)")
        
        if filename:
            try:
                if self._validateToolCSVFile(filename):
                    imported_count = self._importToolsFromCSV(filename)
                    QMessageBox.information(self, "Success", 
                                          f"Imported {imported_count} tools from CSV.")
                else:
                    QMessageBox.warning(self, "Invalid CSV", 
                                      "CSV file format is invalid.")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to import: {e}")
    
    @pyqtSlot()
    def validateToolCSV(self):
        """Validate CSV file format"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Validate Tool CSV", 
            "", "CSV Files (*.csv)")
        
        if filename:
            try:
                if self._validateToolCSVFile(filename):
                    QMessageBox.information(self, "Valid", 
                                          "CSV file format is valid.")
                else:
                    QMessageBox.warning(self, "Invalid", 
                                      "CSV file format is invalid.")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to validate: {e}")
    
    def _validateToolCSVFile(self, filename):
        """Validate CSV file format for tools"""
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                
                # Check header
                expected_header = [col[0] for col in self.COLUMNS]
                if header != expected_header:
                    return False
                
                # Check data rows
                for row in reader:
                    if len(row) != len(expected_header):
                        return False
                    
                    # Validate tool number (must be positive integer)
                    try:
                        tool_num = int(row[0])
                        if tool_num <= 0:
                            return False
                    except ValueError:
                        return False
                    
                    # Validate numeric values
                    for i, (_, _, _, data_type) in enumerate(self.COLUMNS):
                        if i == 0:  # Skip tool number, already validated
                            continue
                        if i == len(self.COLUMNS) - 1:  # Skip notes column
                            continue
                            
                        try:
                            if data_type == int:
                                int(row[i])
                            elif data_type == float:
                                float(row[i])
                        except ValueError:
                            return False
                
                return True
        except Exception:
            return False
    
    def _importToolsFromCSV(self, filename):
        """Import tools from CSV file"""
        imported_count = 0
        overwrite = self.overwrite_existing.isChecked()
        
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            
            for row_data in reader:
                tool_num = int(row_data[0])
                
                # Skip if tool exists and not overwriting
                if tool_num in self.tool_data and not overwrite:
                    continue
                
                # Create tool data
                tool_data = {
                    'T': tool_num,
                    'P': int(row_data[1]) if row_data[1] else tool_num,
                    'Z': float(row_data[2]) if row_data[2] else 0.0,
                    'R': float(row_data[3]) if row_data[3] else 0.0,
                    'D': float(row_data[4]) if row_data[4] else 0.0,
                    'A': float(row_data[5]) if row_data[5] else 0.0,
                    'B': float(row_data[6]) if row_data[6] else 0.0,
                    'Q': int(row_data[7]) if row_data[7] else 0,
                    'comment': row_data[8] if len(row_data) > 8 else ''
                }
                
                self.tool_data[tool_num] = tool_data
                imported_count += 1
        
        self._populateToolTable()
        self.markUnsaved()
        
        return imported_count
    
    def markUnsaved(self):
        """Mark the tool table as having unsaved changes"""
        self.unsaved_changes = True
        self.unsaved_indicator.setVisible(True)
    
    def markSaved(self):
        """Mark the tool table as saved"""
        self.unsaved_changes = False
        self.unsaved_indicator.setVisible(False)


# Test the widget standalone
if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = ToolTableEditor()
    widget.show()
    sys.exit(app.exec_())