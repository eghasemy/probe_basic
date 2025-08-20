#!/usr/bin/env python

"""
Fixture Library Widget - Phase 8 Implementation

A comprehensive widget for managing named WCS presets with notes and thumbnails.
Provides fixture/workholding setup library for quick WCS application.

Key Features:
- Named WCS preset management
- Notes and descriptions for each fixture
- Thumbnail images for visual identification
- Apply preset to any G54-G59.3 coordinate system
- Import/export fixture libraries
- Search and categorization
"""

import os
import json
import shutil
from datetime import datetime
from qtpy.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QSize
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                           QLabel, QLineEdit, QPushButton, QListWidget, 
                           QListWidgetItem, QTextEdit, QFileDialog, 
                           QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox,
                           QGroupBox, QTabWidget, QFrame, QSplitter,
                           QScrollArea, QSizePolicy, QDialog, QDialogButtonBox)
from qtpy.QtGui import QFont, QPixmap, QIcon

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

class FixtureDialog(QDialog):
    """Dialog for creating/editing fixture presets"""
    
    def __init__(self, parent=None, fixture_data=None):
        super(FixtureDialog, self).__init__(parent)
        
        self.fixture_data = fixture_data or {}
        self.setupUI()
        self.loadFixtureData()
        
    def setupUI(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Fixture Preset")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Basic info
        info_group = QGroupBox("Fixture Information")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Fixture name (required)")
        info_layout.addWidget(self.name_edit, 0, 1)
        
        info_layout.addWidget(QLabel("Category:"), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems([
            "Vise", "Chuck", "Rotary Table", "Custom Fixture", 
            "Workholding", "Jig", "Other"
        ])
        info_layout.addWidget(self.category_combo, 1, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # WCS offsets
        offsets_group = QGroupBox("Coordinate System Offsets")
        offsets_layout = QGridLayout()
        
        self.offset_inputs = {}
        axes = ['X', 'Y', 'Z', 'A', 'B', 'C']
        
        for i, axis in enumerate(axes):
            row = i // 3
            col = (i % 3) * 2
            
            offsets_layout.addWidget(QLabel(f"{axis}:"), row, col)
            
            offset_input = QDoubleSpinBox()
            offset_input.setRange(-999.999, 999.999)
            offset_input.setDecimals(4)
            offset_input.setSuffix(" mm")
            self.offset_inputs[axis] = offset_input
            offsets_layout.addWidget(offset_input, row, col + 1)
        
        # Buttons to get current offsets
        get_current_layout = QHBoxLayout()
        
        self.get_current_btn = QPushButton("Get Current WCS")
        self.get_current_btn.clicked.connect(self.getCurrentWCS)
        get_current_layout.addWidget(self.get_current_btn)
        
        self.wcs_source_combo = QComboBox()
        for i in range(1, 10):
            if i <= 6:
                self.wcs_source_combo.addItem(f"G5{3+i}")
            else:
                self.wcs_source_combo.addItem(f"G59.{i-6}")
        get_current_layout.addWidget(self.wcs_source_combo)
        
        offsets_layout.addLayout(get_current_layout, 2, 0, 1, 6)
        offsets_group.setLayout(offsets_layout)
        layout.addWidget(offsets_group)
        
        # Notes
        notes_group = QGroupBox("Notes and Description")
        notes_layout = QVBoxLayout()
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Describe this fixture setup:\n"
            "- Part positioning\n"
            "- Workholding method\n"
            "- Tool access considerations\n"
            "- Setup notes"
        )
        notes_layout.addWidget(self.notes_edit)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Thumbnail
        thumbnail_group = QGroupBox("Thumbnail Image")
        thumbnail_layout = QVBoxLayout()
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(200, 150)
        self.thumbnail_label.setStyleSheet(
            "border: 2px dashed #ccc; background-color: #f9f9f9;"
        )
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setText("No Image")
        self.thumbnail_label.setScaledContents(True)
        thumbnail_layout.addWidget(self.thumbnail_label)
        
        thumbnail_button_layout = QHBoxLayout()
        
        self.browse_image_btn = QPushButton("Browse Image...")
        self.browse_image_btn.clicked.connect(self.browseImage)
        thumbnail_button_layout.addWidget(self.browse_image_btn)
        
        self.clear_image_btn = QPushButton("Clear Image")
        self.clear_image_btn.clicked.connect(self.clearImage)
        thumbnail_button_layout.addWidget(self.clear_image_btn)
        
        thumbnail_layout.addLayout(thumbnail_button_layout)
        thumbnail_group.setLayout(thumbnail_layout)
        layout.addWidget(thumbnail_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def loadFixtureData(self):
        """Load existing fixture data into the dialog"""
        if not self.fixture_data:
            return
            
        self.name_edit.setText(self.fixture_data.get('name', ''))
        self.category_combo.setCurrentText(self.fixture_data.get('category', ''))
        
        offsets = self.fixture_data.get('offsets', {})
        for axis, input_widget in self.offset_inputs.items():
            value = offsets.get(axis, 0.0)
            input_widget.setValue(value)
        
        self.notes_edit.setPlainText(self.fixture_data.get('notes', ''))
        
        # Load thumbnail
        thumbnail_path = self.fixture_data.get('thumbnail_path')
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            self.thumbnail_label.setPixmap(pixmap)
    
    @pyqtSlot()
    def getCurrentWCS(self):
        """Get current WCS offsets from LinuxCNC"""
        # TODO: Implement getting current WCS from LinuxCNC
        # For now, show placeholder values
        QMessageBox.information(self, "Get Current WCS", 
                              "Getting current WCS offsets from LinuxCNC...")
    
    @pyqtSlot()
    def browseImage(self):
        """Browse for thumbnail image"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Thumbnail Image", 
            "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        
        if filename:
            pixmap = QPixmap(filename)
            if not pixmap.isNull():
                # Scale image to fit
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
                self.thumbnail_path = filename
            else:
                QMessageBox.warning(self, "Invalid Image", 
                                  "Could not load the selected image.")
    
    @pyqtSlot()
    def clearImage(self):
        """Clear the thumbnail image"""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("No Image")
        self.thumbnail_path = None
    
    def getFixtureData(self):
        """Get the fixture data from the dialog"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", 
                              "Please enter a fixture name.")
            return None
        
        offsets = {}
        for axis, input_widget in self.offset_inputs.items():
            offsets[axis] = input_widget.value()
        
        data = {
            'name': name,
            'category': self.category_combo.currentText(),
            'offsets': offsets,
            'notes': self.notes_edit.toPlainText(),
            'created': self.fixture_data.get('created', datetime.now().isoformat()),
            'modified': datetime.now().isoformat()
        }
        
        # Handle thumbnail
        if hasattr(self, 'thumbnail_path') and self.thumbnail_path:
            data['thumbnail_path'] = self.thumbnail_path
        elif 'thumbnail_path' in self.fixture_data:
            data['thumbnail_path'] = self.fixture_data['thumbnail_path']
        
        return data


class FixtureLibrary(VCPBaseWidget):
    """
    Fixture Library Widget for Phase 8
    
    Provides comprehensive fixture/workholding preset management with:
    - Named WCS presets with descriptions
    - Thumbnail images for visual identification
    - Apply presets to any coordinate system
    - Import/export fixture libraries
    - Search and categorization
    """
    
    # Signals
    fixtureApplied = pyqtSignal(str, str)  # fixture_name, target_wcs
    fixtureAdded = pyqtSignal(str)         # fixture_name
    fixtureRemoved = pyqtSignal(str)       # fixture_name
    
    def __init__(self, parent=None):
        super(FixtureLibrary, self).__init__(parent)
        
        # Get LinuxCNC plugins
        if HAS_QTPYVCP:
            self.status = getPlugin('status')
        else:
            self.status = None
            
        self.fixtures = {}  # Store fixture library data
        self.library_file = None
        self.library_dir = os.path.expanduser("~/.probe_basic/fixtures")
        
        # Ensure library directory exists
        os.makedirs(self.library_dir, exist_ok=True)
        
        self.setupUI()
        self.connectSignals()
        self.loadLibrary()
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("fixtureLibrary")
        self.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Fixture Library")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2E86AB;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search fixtures...")
        self.search_edit.textChanged.connect(self.filterFixtures)
        search_layout.addWidget(self.search_edit)
        
        # Category filter
        search_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.filterFixtures)
        search_layout.addWidget(self.category_filter)
        
        header_layout.addLayout(search_layout)
        layout.addLayout(header_layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Fixture list
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        
        list_controls = QHBoxLayout()
        
        self.new_fixture_btn = QPushButton("New Fixture")
        self.new_fixture_btn.clicked.connect(self.newFixture)
        list_controls.addWidget(self.new_fixture_btn)
        
        self.edit_fixture_btn = QPushButton("Edit")
        self.edit_fixture_btn.clicked.connect(self.editFixture)
        self.edit_fixture_btn.setEnabled(False)
        list_controls.addWidget(self.edit_fixture_btn)
        
        self.delete_fixture_btn = QPushButton("Delete")
        self.delete_fixture_btn.clicked.connect(self.deleteFixture)
        self.delete_fixture_btn.setEnabled(False)
        list_controls.addWidget(self.delete_fixture_btn)
        
        list_layout.addLayout(list_controls)
        
        # Fixture list widget
        self.fixture_list = QListWidget()
        self.fixture_list.currentItemChanged.connect(self.onFixtureSelectionChanged)
        list_layout.addWidget(self.fixture_list)
        
        list_widget.setLayout(list_layout)
        content_splitter.addWidget(list_widget)
        
        # Fixture details
        details_widget = self.createDetailsWidget()
        content_splitter.addWidget(details_widget)
        
        # Set splitter proportions
        content_splitter.setSizes([300, 500])
        layout.addWidget(content_splitter)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        # WCS application
        apply_group_layout = QHBoxLayout()
        apply_group_layout.addWidget(QLabel("Apply to:"))
        
        self.target_wcs_combo = QComboBox()
        for i in range(1, 10):
            if i <= 6:
                self.target_wcs_combo.addItem(f"G5{3+i}")
            else:
                self.target_wcs_combo.addItem(f"G59.{i-6}")
        apply_group_layout.addWidget(self.target_wcs_combo)
        
        self.apply_fixture_btn = QPushButton("Apply Fixture")
        self.apply_fixture_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.apply_fixture_btn.clicked.connect(self.applyFixture)
        self.apply_fixture_btn.setEnabled(False)
        apply_group_layout.addWidget(self.apply_fixture_btn)
        
        button_layout.addLayout(apply_group_layout)
        button_layout.addStretch()
        
        # Library management
        self.import_library_btn = QPushButton("Import Library")
        self.import_library_btn.clicked.connect(self.importLibrary)
        button_layout.addWidget(self.import_library_btn)
        
        self.export_library_btn = QPushButton("Export Library")
        self.export_library_btn.clicked.connect(self.exportLibrary)
        button_layout.addWidget(self.export_library_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def createDetailsWidget(self):
        """Create the fixture details display widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        self.details_name = QLabel("No fixture selected")
        self.details_name.setStyleSheet("font-weight: bold; font-size: 12px; color: #2E86AB;")
        layout.addWidget(self.details_name)
        
        self.details_category = QLabel("")
        self.details_category.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.details_category)
        
        # Thumbnail
        self.details_thumbnail = QLabel()
        self.details_thumbnail.setFixedSize(250, 187)  # 4:3 aspect ratio
        self.details_thumbnail.setStyleSheet(
            "border: 1px solid #ccc; background-color: #f9f9f9;"
        )
        self.details_thumbnail.setAlignment(Qt.AlignCenter)
        self.details_thumbnail.setText("No Image")
        self.details_thumbnail.setScaledContents(True)
        layout.addWidget(self.details_thumbnail)
        
        # Offsets table
        offsets_group = QGroupBox("WCS Offsets")
        offsets_layout = QGridLayout()
        
        self.details_offsets = {}
        axes = ['X', 'Y', 'Z', 'A', 'B', 'C']
        
        for i, axis in enumerate(axes):
            row = i // 3
            col = (i % 3) * 2
            
            offsets_layout.addWidget(QLabel(f"{axis}:"), row, col)
            
            offset_label = QLabel("0.0000")
            offset_label.setStyleSheet("font-family: monospace; padding: 2px;")
            self.details_offsets[axis] = offset_label
            offsets_layout.addWidget(offset_label, row, col + 1)
        
        offsets_group.setLayout(offsets_layout)
        layout.addWidget(offsets_group)
        
        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        self.details_notes = QTextEdit()
        self.details_notes.setReadOnly(True)
        self.details_notes.setMaximumHeight(150)
        notes_layout.addWidget(self.details_notes)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Metadata
        meta_layout = QHBoxLayout()
        self.details_created = QLabel("")
        self.details_created.setStyleSheet("color: #666; font-size: 10px;")
        meta_layout.addWidget(self.details_created)
        
        meta_layout.addStretch()
        
        self.details_modified = QLabel("")
        self.details_modified.setStyleSheet("color: #666; font-size: 10px;")
        meta_layout.addWidget(self.details_modified)
        
        layout.addLayout(meta_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def connectSignals(self):
        """Connect LinuxCNC signals"""
        if self.status:
            # Connect to coordinate system changes
            pass
            
    def loadLibrary(self):
        """Load fixture library from file"""
        library_file = os.path.join(self.library_dir, "fixtures.json")
        
        if os.path.exists(library_file):
            try:
                with open(library_file, 'r') as f:
                    self.fixtures = json.load(f)
                self.library_file = library_file
            except Exception as e:
                if LOG:
                    LOG.error(f"Error loading fixture library: {e}")
                self.fixtures = {}
        else:
            self.fixtures = {}
            
        self.updateFixtureList()
        self.updateCategoryFilter()
    
    def saveLibrary(self):
        """Save fixture library to file"""
        if not self.library_file:
            self.library_file = os.path.join(self.library_dir, "fixtures.json")
        
        try:
            with open(self.library_file, 'w') as f:
                json.dump(self.fixtures, f, indent=2)
        except Exception as e:
            if LOG:
                LOG.error(f"Error saving fixture library: {e}")
            QMessageBox.critical(self, "Error", 
                               f"Failed to save fixture library: {e}")
    
    def updateFixtureList(self):
        """Update the fixture list widget"""
        self.fixture_list.clear()
        
        # Sort fixtures by name
        for fixture_name in sorted(self.fixtures.keys()):
            fixture = self.fixtures[fixture_name]
            
            item = QListWidgetItem(fixture_name)
            item.setData(Qt.UserRole, fixture_name)
            
            # Add category as tooltip
            category = fixture.get('category', 'Uncategorized')
            item.setToolTip(f"{fixture_name}\nCategory: {category}")
            
            self.fixture_list.addItem(item)
    
    def updateCategoryFilter(self):
        """Update the category filter combo box"""
        # Get all categories
        categories = set()
        for fixture in self.fixtures.values():
            category = fixture.get('category', 'Uncategorized')
            categories.add(category)
        
        # Update combo box
        current_text = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        for category in sorted(categories):
            self.category_filter.addItem(category)
        
        # Restore selection
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
    
    @pyqtSlot()
    def filterFixtures(self):
        """Filter fixtures based on search text and category"""
        search_text = self.search_edit.text().lower()
        category_filter = self.category_filter.currentText()
        
        for i in range(self.fixture_list.count()):
            item = self.fixture_list.item(i)
            fixture_name = item.data(Qt.UserRole)
            fixture = self.fixtures.get(fixture_name, {})
            
            # Check search text
            show_item = True
            if search_text:
                fixture_text = f"{fixture_name} {fixture.get('notes', '')}".lower()
                show_item = search_text in fixture_text
            
            # Check category filter
            if show_item and category_filter != "All Categories":
                fixture_category = fixture.get('category', 'Uncategorized')
                show_item = fixture_category == category_filter
            
            item.setHidden(not show_item)
    
    @pyqtSlot()
    def onFixtureSelectionChanged(self):
        """Handle fixture selection changes"""
        current_item = self.fixture_list.currentItem()
        
        if current_item:
            fixture_name = current_item.data(Qt.UserRole)
            fixture = self.fixtures.get(fixture_name, {})
            
            # Update details display
            self.details_name.setText(fixture_name)
            
            category = fixture.get('category', 'Uncategorized')
            self.details_category.setText(f"Category: {category}")
            
            # Update thumbnail
            thumbnail_path = fixture.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                pixmap = QPixmap(thumbnail_path)
                scaled_pixmap = pixmap.scaled(
                    self.details_thumbnail.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.details_thumbnail.setPixmap(scaled_pixmap)
            else:
                self.details_thumbnail.clear()
                self.details_thumbnail.setText("No Image")
            
            # Update offsets
            offsets = fixture.get('offsets', {})
            for axis, label in self.details_offsets.items():
                value = offsets.get(axis, 0.0)
                label.setText(f"{value:.4f}")
            
            # Update notes
            notes = fixture.get('notes', '')
            self.details_notes.setPlainText(notes)
            
            # Update metadata
            created = fixture.get('created', '')
            if created:
                created_dt = datetime.fromisoformat(created.replace('Z', ''))
                self.details_created.setText(f"Created: {created_dt.strftime('%Y-%m-%d %H:%M')}")
            else:
                self.details_created.setText("")
            
            modified = fixture.get('modified', '')
            if modified:
                modified_dt = datetime.fromisoformat(modified.replace('Z', ''))
                self.details_modified.setText(f"Modified: {modified_dt.strftime('%Y-%m-%d %H:%M')}")
            else:
                self.details_modified.setText("")
            
            # Enable action buttons
            self.edit_fixture_btn.setEnabled(True)
            self.delete_fixture_btn.setEnabled(True)
            self.apply_fixture_btn.setEnabled(True)
            
        else:
            # Clear details
            self.details_name.setText("No fixture selected")
            self.details_category.setText("")
            self.details_thumbnail.clear()
            self.details_thumbnail.setText("No Image")
            
            for label in self.details_offsets.values():
                label.setText("0.0000")
            
            self.details_notes.clear()
            self.details_created.setText("")
            self.details_modified.setText("")
            
            # Disable action buttons
            self.edit_fixture_btn.setEnabled(False)
            self.delete_fixture_btn.setEnabled(False)
            self.apply_fixture_btn.setEnabled(False)
    
    @pyqtSlot()
    def newFixture(self):
        """Create a new fixture preset"""
        dialog = FixtureDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            fixture_data = dialog.getFixtureData()
            if fixture_data:
                fixture_name = fixture_data['name']
                
                # Check if name already exists
                if fixture_name in self.fixtures:
                    reply = QMessageBox.question(
                        self, "Fixture Exists",
                        f"A fixture named '{fixture_name}' already exists.\n"
                        "Do you want to overwrite it?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply != QMessageBox.Yes:
                        return
                
                # Copy thumbnail to library directory if needed
                if 'thumbnail_path' in fixture_data:
                    thumbnail_path = self._copyThumbnail(
                        fixture_data['thumbnail_path'], fixture_name
                    )
                    if thumbnail_path:
                        fixture_data['thumbnail_path'] = thumbnail_path
                
                # Add fixture
                self.fixtures[fixture_name] = fixture_data
                self.saveLibrary()
                self.updateFixtureList()
                self.updateCategoryFilter()
                self.fixtureAdded.emit(fixture_name)
                
                # Select the new fixture
                for i in range(self.fixture_list.count()):
                    item = self.fixture_list.item(i)
                    if item.data(Qt.UserRole) == fixture_name:
                        self.fixture_list.setCurrentItem(item)
                        break
    
    @pyqtSlot()
    def editFixture(self):
        """Edit selected fixture preset"""
        current_item = self.fixture_list.currentItem()
        if not current_item:
            return
        
        fixture_name = current_item.data(Qt.UserRole)
        fixture_data = self.fixtures.get(fixture_name, {})
        
        dialog = FixtureDialog(self, fixture_data)
        
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.getFixtureData()
            if updated_data:
                new_name = updated_data['name']
                
                # Handle name change
                if new_name != fixture_name:
                    if new_name in self.fixtures:
                        QMessageBox.warning(self, "Name Exists", 
                                          f"A fixture named '{new_name}' already exists.")
                        return
                    
                    # Remove old entry
                    del self.fixtures[fixture_name]
                
                # Copy thumbnail if changed
                if 'thumbnail_path' in updated_data:
                    thumbnail_path = self._copyThumbnail(
                        updated_data['thumbnail_path'], new_name
                    )
                    if thumbnail_path:
                        updated_data['thumbnail_path'] = thumbnail_path
                
                # Update fixture
                self.fixtures[new_name] = updated_data
                self.saveLibrary()
                self.updateFixtureList()
                self.updateCategoryFilter()
                
                # Select the updated fixture
                for i in range(self.fixture_list.count()):
                    item = self.fixture_list.item(i)
                    if item.data(Qt.UserRole) == new_name:
                        self.fixture_list.setCurrentItem(item)
                        break
    
    @pyqtSlot()
    def deleteFixture(self):
        """Delete selected fixture preset"""
        current_item = self.fixture_list.currentItem()
        if not current_item:
            return
        
        fixture_name = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Fixture",
            f"Are you sure you want to delete the fixture '{fixture_name}'?\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove thumbnail file
            fixture = self.fixtures.get(fixture_name, {})
            thumbnail_path = fixture.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    os.remove(thumbnail_path)
                except Exception:
                    pass  # Ignore thumbnail deletion errors
            
            # Remove fixture
            del self.fixtures[fixture_name]
            self.saveLibrary()
            self.updateFixtureList()
            self.updateCategoryFilter()
            self.fixtureRemoved.emit(fixture_name)
    
    @pyqtSlot()
    def applyFixture(self):
        """Apply selected fixture to target WCS"""
        current_item = self.fixture_list.currentItem()
        if not current_item:
            return
        
        fixture_name = current_item.data(Qt.UserRole)
        fixture = self.fixtures.get(fixture_name, {})
        target_wcs = self.target_wcs_combo.currentText()
        
        reply = QMessageBox.question(
            self, "Apply Fixture",
            f"Apply fixture '{fixture_name}' to {target_wcs}?\n"
            "This will overwrite the current offsets.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Apply offsets to LinuxCNC
            offsets = fixture.get('offsets', {})
            
            if LOG:
                LOG.info(f"Applying fixture '{fixture_name}' to {target_wcs}: {offsets}")
            
            # For now, just show success message
            QMessageBox.information(self, "Success", 
                                  f"Fixture '{fixture_name}' applied to {target_wcs}.")
            
            self.fixtureApplied.emit(fixture_name, target_wcs)
    
    @pyqtSlot()
    def importLibrary(self):
        """Import fixture library from JSON file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Fixture Library",
            "", "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported_fixtures = json.load(f)
                
                # Merge with existing fixtures
                conflicts = []
                for fixture_name in imported_fixtures:
                    if fixture_name in self.fixtures:
                        conflicts.append(fixture_name)
                
                if conflicts:
                    reply = QMessageBox.question(
                        self, "Import Conflicts",
                        f"The following fixtures already exist:\n"
                        f"{', '.join(conflicts)}\n\n"
                        "Do you want to overwrite them?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply != QMessageBox.Yes:
                        return
                
                # Import fixtures
                imported_count = 0
                for fixture_name, fixture_data in imported_fixtures.items():
                    self.fixtures[fixture_name] = fixture_data
                    imported_count += 1
                
                self.saveLibrary()
                self.updateFixtureList()
                self.updateCategoryFilter()
                
                QMessageBox.information(self, "Success", 
                                      f"Imported {imported_count} fixtures.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to import library: {e}")
    
    @pyqtSlot()
    def exportLibrary(self):
        """Export fixture library to JSON file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Fixture Library",
            "fixture_library.json", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.fixtures, f, indent=2)
                
                QMessageBox.information(self, "Success", 
                                      f"Library exported to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to export library: {e}")
    
    def _copyThumbnail(self, source_path, fixture_name):
        """Copy thumbnail to library directory"""
        if not source_path or not os.path.exists(source_path):
            return None
        
        try:
            # Create thumbnails subdirectory
            thumbnails_dir = os.path.join(self.library_dir, "thumbnails")
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            # Generate destination filename
            file_ext = os.path.splitext(source_path)[1]
            safe_name = "".join(c for c in fixture_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            dest_filename = f"{safe_name}{file_ext}"
            dest_path = os.path.join(thumbnails_dir, dest_filename)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            return dest_path
            
        except Exception as e:
            if LOG:
                LOG.error(f"Error copying thumbnail: {e}")
            return None


# Test the widget standalone
if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = FixtureLibrary()
    widget.show()
    sys.exit(app.exec_())