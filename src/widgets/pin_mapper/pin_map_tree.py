#!/usr/bin/env python

import os
import yaml
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox,
                           QMenu, QAction, QMessageBox, QHeaderView)
from qtpy.QtGui import QFont, QIcon
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class PinMapTree(QWidget):
    """
    Pin Mapper Tree Widget
    Displays Function ↔ Signal ↔ Pin mappings with CRUD operations
    Based on Phase 2 requirements from PB-Touch.md
    """
    
    mappingChanged = Signal()  # Emitted when mappings are modified
    
    def __init__(self, parent=None):
        super(PinMapTree, self).__init__(parent)
        
        self.config_dir = os.path.join(os.path.dirname(__file__), '../../../configs/probe_basic/config/pinmap.d')
        self.current_profile = 'default'
        self.mappings = {}
        
        self.setupUI()
        self.setupContextMenu()
        self.loadMappings()
        
    def setupUI(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        # Profile selector
        header_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("default")
        self.profile_combo.currentTextChanged.connect(self.onProfileChanged)
        header_layout.addWidget(self.profile_combo)
        
        # Search filter
        header_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter by function, signal, or pin...")
        self.search_edit.textChanged.connect(self.filterMappings)
        header_layout.addWidget(self.search_edit)
        
        # Subsystem filter
        header_layout.addWidget(QLabel("Subsystem:"))
        self.subsystem_combo = QComboBox()
        self.subsystem_combo.addItem("All")
        self.subsystem_combo.addItems(["Input", "Output", "Spindle", "Motion", "Coolant", "ATC"])
        self.subsystem_combo.currentTextChanged.connect(self.filterMappings)
        header_layout.addWidget(self.subsystem_combo)
        
        header_layout.addStretch()
        
        # Action buttons
        self.add_button = QPushButton("Add Mapping")
        self.add_button.clicked.connect(self.addMapping)
        header_layout.addWidget(self.add_button)
        
        self.generate_hal_button = QPushButton("Generate HAL")
        self.generate_hal_button.clicked.connect(self.generateHAL)
        header_layout.addWidget(self.generate_hal_button)
        
        layout.addLayout(header_layout)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Function", "Signal", "Pin", "Notes"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.itemDoubleClicked.connect(self.editMapping)
        
        layout.addWidget(self.tree)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
    def setupContextMenu(self):
        """Setup right-click context menu"""
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.showContextMenu)
        
    def showContextMenu(self, position):
        """Show context menu at position"""
        item = self.tree.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        edit_action = QAction("Edit Mapping", self)
        edit_action.triggered.connect(lambda: self.editMapping(item))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Mapping", self)
        delete_action.triggered.connect(lambda: self.deleteMapping(item))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        jump_action = QAction("Jump to HAL", self)
        jump_action.triggered.connect(lambda: self.jumpToHAL(item))
        menu.addAction(jump_action)
        
        test_action = QAction("Test Pin", self)
        test_action.triggered.connect(lambda: self.testPin(item))
        menu.addAction(test_action)
        
        menu.exec_(self.tree.mapToGlobal(position))
        
    def loadMappings(self):
        """Load mappings from YAML file"""
        try:
            config_file = os.path.join(self.config_dir, f"{self.current_profile}.yaml")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    self.mappings = data.get('mappings', {})
            else:
                self.mappings = {}
                
            self.populateTree()
            self.status_label.setText(f"Loaded {len(self.mappings)} mappings from {self.current_profile}.yaml")
            
        except Exception as e:
            LOG.error(f"Failed to load mappings: {e}")
            self.status_label.setText(f"Error loading mappings: {e}")
            
    def saveMappings(self):
        """Save mappings to YAML file"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config_file = os.path.join(self.config_dir, f"{self.current_profile}.yaml")
            
            data = {
                'mappings': self.mappings,
                'version': '1.0',
                'generated_by': 'PB-Touch Pin Mapper'
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)
                
            self.status_label.setText(f"Saved {len(self.mappings)} mappings to {self.current_profile}.yaml")
            self.mappingChanged.emit()
            
        except Exception as e:
            LOG.error(f"Failed to save mappings: {e}")
            self.status_label.setText(f"Error saving mappings: {e}")
            
    def populateTree(self):
        """Populate tree widget with current mappings"""
        self.tree.clear()
        
        for function_name, mapping in self.mappings.items():
            item = QTreeWidgetItem([
                function_name,
                mapping.get('signal', ''),
                mapping.get('pin', ''),
                mapping.get('notes', '')
            ])
            
            # Store mapping data in item
            item.setData(0, Qt.UserRole, mapping)
            
            # Color coding by subsystem
            subsystem = mapping.get('subsystem', 'unknown')
            if subsystem == 'input':
                item.setBackground(0, Qt.green)
            elif subsystem == 'output':
                item.setBackground(0, Qt.blue)
            elif subsystem == 'spindle':
                item.setBackground(0, Qt.yellow)
                
            self.tree.addTopLevelItem(item)
            
    def filterMappings(self):
        """Filter tree based on search and subsystem"""
        search_text = self.search_edit.text().lower()
        subsystem_filter = self.subsystem_combo.currentText()
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            mapping = item.data(0, Qt.UserRole)
            
            # Check search filter
            show_search = (not search_text or 
                          search_text in item.text(0).lower() or
                          search_text in item.text(1).lower() or
                          search_text in item.text(2).lower())
            
            # Check subsystem filter
            show_subsystem = (subsystem_filter == "All" or
                             mapping.get('subsystem', '').lower() == subsystem_filter.lower())
            
            item.setHidden(not (show_search and show_subsystem))
            
    def onProfileChanged(self, profile_name):
        """Handle profile change"""
        self.current_profile = profile_name
        self.loadMappings()
        
    def addMapping(self):
        """Add new mapping"""
        from .pin_mapping_dialog import PinMappingDialog
        
        dialog = PinMappingDialog(self)
        if dialog.exec_() == dialog.Accepted:
            function_name = dialog.getFunction()
            mapping_data = dialog.getMappingData()
            
            if function_name in self.mappings:
                reply = QMessageBox.question(self, "Overwrite Mapping", 
                                           f"Function '{function_name}' already exists. Overwrite?")
                if reply != QMessageBox.Yes:
                    return
                    
            self.mappings[function_name] = mapping_data
            self.saveMappings()
            self.populateTree()
            
    def editMapping(self, item):
        """Edit existing mapping"""
        if not item:
            return
            
        from .pin_mapping_dialog import PinMappingDialog
        
        function_name = item.text(0)
        mapping_data = item.data(0, Qt.UserRole)
        
        dialog = PinMappingDialog(self, function_name, mapping_data)
        if dialog.exec_() == dialog.Accepted:
            new_function_name = dialog.getFunction()
            new_mapping_data = dialog.getMappingData()
            
            # Remove old mapping if function name changed
            if function_name != new_function_name:
                del self.mappings[function_name]
                
            self.mappings[new_function_name] = new_mapping_data
            self.saveMappings()
            self.populateTree()
            
    def deleteMapping(self, item):
        """Delete mapping"""
        if not item:
            return
            
        function_name = item.text(0)
        reply = QMessageBox.question(self, "Delete Mapping", 
                                   f"Delete mapping for '{function_name}'?")
        if reply == QMessageBox.Yes:
            del self.mappings[function_name]
            self.saveMappings()
            self.populateTree()
            
    def jumpToHAL(self, item):
        """Jump to HAL file location"""
        # TODO: Implement HAL file navigation
        self.status_label.setText("Jump to HAL - Not implemented yet")
        
    def testPin(self, item):
        """Test pin functionality"""
        # TODO: Implement pin testing (blink/edge)
        self.status_label.setText("Pin testing - Not implemented yet")
        
    def generateHAL(self):
        """Generate HAL file from mappings"""
        from .hal_generator import HALGenerator
        
        try:
            generator = HALGenerator(self.mappings)
            hal_file = os.path.join(os.path.dirname(self.config_dir), '../hal/pb_touch_sim.hal')
            
            success = generator.generate(hal_file)
            if success:
                self.status_label.setText(f"HAL generated successfully: {hal_file}")
            else:
                self.status_label.setText("HAL generation failed")
                
        except Exception as e:
            LOG.error(f"HAL generation error: {e}")
            self.status_label.setText(f"HAL generation error: {e}")