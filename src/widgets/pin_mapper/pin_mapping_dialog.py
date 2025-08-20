#!/usr/bin/env python

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton,
                           QDialogButtonBox, QGroupBox)
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class PinMappingDialog(QDialog):
    """
    Dialog for creating/editing pin mappings
    """
    
    def __init__(self, parent=None, function_name="", mapping_data=None):
        super(PinMappingDialog, self).__init__(parent)
        
        self.function_name = function_name
        self.mapping_data = mapping_data or {}
        
        self.setupUI()
        self.populateFields()
        
    def setupUI(self):
        """Setup the user interface"""
        self.setWindowTitle("Pin Mapping Editor")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Function group
        function_group = QGroupBox("Function")
        function_layout = QFormLayout(function_group)
        
        self.function_edit = QLineEdit()
        self.function_edit.setPlaceholderText("e.g., CycleStart, FeedHold, SpindleEnable")
        function_layout.addRow("Function Name:", self.function_edit)
        
        self.subsystem_combo = QComboBox()
        self.subsystem_combo.addItems(["input", "output", "spindle", "motion", "coolant", "atc"])
        function_layout.addRow("Subsystem:", self.subsystem_combo)
        
        layout.addWidget(function_group)
        
        # Signal group
        signal_group = QGroupBox("Signal")
        signal_layout = QFormLayout(signal_group)
        
        self.signal_edit = QLineEdit()
        self.signal_edit.setPlaceholderText("e.g., cycle-start, feed-hold, spindle-enable")
        signal_layout.addRow("Signal Name:", self.signal_edit)
        
        layout.addWidget(signal_group)
        
        # Pin group
        pin_group = QGroupBox("Pin")
        pin_layout = QFormLayout(pin_group)
        
        self.pin_edit = QLineEdit()
        self.pin_edit.setPlaceholderText("e.g., hm2_7i76e.0.7i76.0.0.input-00")
        pin_layout.addRow("Pin Address:", self.pin_edit)
        
        self.pin_type_combo = QComboBox()
        self.pin_type_combo.addItems(["bit", "float", "s32", "u32"])
        pin_layout.addRow("Pin Type:", self.pin_type_combo)
        
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["input", "output", "io"])
        pin_layout.addRow("Direction:", self.direction_combo)
        
        layout.addWidget(pin_group)
        
        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Optional notes about this mapping...")
        self.notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def populateFields(self):
        """Populate fields with existing data"""
        if self.function_name:
            self.function_edit.setText(self.function_name)
            
        if self.mapping_data:
            self.signal_edit.setText(self.mapping_data.get('signal', ''))
            self.pin_edit.setText(self.mapping_data.get('pin', ''))
            self.notes_edit.setPlainText(self.mapping_data.get('notes', ''))
            
            # Set combo box values
            subsystem = self.mapping_data.get('subsystem', 'input')
            idx = self.subsystem_combo.findText(subsystem)
            if idx >= 0:
                self.subsystem_combo.setCurrentIndex(idx)
                
            pin_type = self.mapping_data.get('pin_type', 'bit')
            idx = self.pin_type_combo.findText(pin_type)
            if idx >= 0:
                self.pin_type_combo.setCurrentIndex(idx)
                
            direction = self.mapping_data.get('direction', 'input')
            idx = self.direction_combo.findText(direction)
            if idx >= 0:
                self.direction_combo.setCurrentIndex(idx)
                
    def getFunction(self):
        """Get function name"""
        return self.function_edit.text().strip()
        
    def getMappingData(self):
        """Get mapping data"""
        return {
            'signal': self.signal_edit.text().strip(),
            'pin': self.pin_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
            'subsystem': self.subsystem_combo.currentText(),
            'pin_type': self.pin_type_combo.currentText(),
            'direction': self.direction_combo.currentText()
        }