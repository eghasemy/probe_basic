"""
File Browser Widget - Core Implementation
Phase 6: File browser with previews, metadata, and actions
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QFileSystemWatcher
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QLabel, QTextEdit, QPushButton,
                             QSplitter, QGroupBox, QFileDialog, QMessageBox,
                             QComboBox, QLineEdit, QProgressBar)
from PyQt5.QtGui import QPixmap, QFont

class FileBrowserWidget(QWidget):
    """File browser with preview and metadata capabilities"""
    
    # Signals
    file_selected = pyqtSignal(str)  # File path selected
    file_opened = pyqtSignal(str)    # File opened for execution
    
    def __init__(self, parent=None):
        super(FileBrowserWidget, self).__init__(parent)
        
        # File system state
        self.current_path = os.path.expanduser("~")
        self.profile_dir = os.path.expanduser("~/linuxcnc/configs")
        self.mounted_shares = []
        self.file_watcher = QFileSystemWatcher()
        
        # Metadata cache
        self.metadata_cache = {}
        self.metadata_file = os.path.join(self.profile_dir, "file_metadata.json")
        self.load_metadata()
        
        self.init_ui()
        self.setup_connections()
        self.refresh_file_list()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Path navigation
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.addItem("Local Profile", self.profile_dir)
        controls_layout.addWidget(QLabel("Location:"))
        controls_layout.addWidget(self.path_combo, 1)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Modified", "Size", "Type"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSortingEnabled(True)
        splitter.addWidget(self.file_tree)
        
        # Preview panel
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("Open File")
        self.open_btn.setEnabled(False)
        action_layout.addWidget(self.open_btn)
        
        self.duplicate_btn = QPushButton("Duplicate to Profile")
        self.duplicate_btn.setEnabled(False)
        action_layout.addWidget(self.duplicate_btn)
        
        self.folder_btn = QPushButton("Open Containing Folder")
        self.folder_btn.setEnabled(False)
        action_layout.addWidget(self.folder_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
    def create_preview_panel(self):
        """Create the file preview panel"""
        panel = QGroupBox("File Preview")
        layout = QVBoxLayout(panel)
        
        # File info
        info_layout = QVBoxLayout()
        
        self.filename_label = QLabel("No file selected")
        self.filename_label.setFont(QFont("", 10, QFont.Bold))
        info_layout.addWidget(self.filename_label)
        
        self.filepath_label = QLabel("")
        self.filepath_label.setWordWrap(True)
        info_layout.addWidget(self.filepath_label)
        
        self.fileinfo_label = QLabel("")
        info_layout.addWidget(self.fileinfo_label)
        
        layout.addLayout(info_layout)
        
        # Preview area (placeholder for gremlin integration)
        self.preview_area = QTextEdit()
        self.preview_area.setMaximumHeight(200)
        self.preview_area.setPlaceholderText("G-code preview will appear here")
        self.preview_area.setReadOnly(True)
        layout.addWidget(self.preview_area)
        
        # Metadata
        self.metadata_label = QLabel("Last run: Never")
        layout.addWidget(self.metadata_label)
        
        return panel
        
    def setup_connections(self):
        """Setup signal connections"""
        self.file_tree.itemSelectionChanged.connect(self.on_file_selected)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.path_combo.currentTextChanged.connect(self.on_path_changed)
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        self.open_btn.clicked.connect(self.open_selected_file)
        self.duplicate_btn.clicked.connect(self.duplicate_to_profile)
        self.folder_btn.clicked.connect(self.open_containing_folder)
        self.file_watcher.directoryChanged.connect(self.refresh_file_list)
        
    def load_metadata(self):
        """Load file metadata cache"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    self.metadata_cache = json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            self.metadata_cache = {}
            
    def save_metadata(self):
        """Save file metadata cache"""
        try:
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
            
    def refresh_file_list(self):
        """Refresh the file list display"""
        self.file_tree.clear()
        
        current_path = self.path_combo.currentData() or self.path_combo.currentText()
        if not current_path or not os.path.exists(current_path):
            return
            
        # Watch directory for changes
        if current_path not in self.file_watcher.directories():
            self.file_watcher.addPath(current_path)
            
        try:
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                
                # Skip hidden files
                if item.startswith('.'):
                    continue
                    
                tree_item = QTreeWidgetItem()
                tree_item.setText(0, item)
                tree_item.setData(0, Qt.UserRole, item_path)
                
                if os.path.isdir(item_path):
                    tree_item.setText(3, "Folder")
                    tree_item.setText(1, "")
                    tree_item.setText(2, "")
                else:
                    # File info
                    stat = os.stat(item_path)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    size = self.format_file_size(stat.st_size)
                    
                    tree_item.setText(1, modified)
                    tree_item.setText(2, size)
                    
                    # File type
                    if item.lower().endswith(('.ngc', '.nc', '.gcode')):
                        tree_item.setText(3, "G-code")
                    elif item.lower().endswith('.json'):
                        tree_item.setText(3, "JSON")
                    else:
                        tree_item.setText(3, "File")
                        
                self.file_tree.addTopLevelItem(tree_item)
                
        except Exception as e:
            print(f"Error refreshing file list: {e}")
            
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
            
    def on_file_selected(self):
        """Handle file selection"""
        items = self.file_tree.selectedItems()
        if not items:
            self.clear_preview()
            return
            
        item = items[0]
        file_path = item.data(0, Qt.UserRole)
        
        if os.path.isfile(file_path):
            self.show_file_preview(file_path)
            self.open_btn.setEnabled(True)
            self.duplicate_btn.setEnabled(True)
            self.folder_btn.setEnabled(True)
            self.file_selected.emit(file_path)
        else:
            self.clear_preview()
            self.open_btn.setEnabled(False)
            self.duplicate_btn.setEnabled(False)
            self.folder_btn.setEnabled(True)
            
    def on_file_double_clicked(self, item, column):
        """Handle file double-click"""
        file_path = item.data(0, Qt.UserRole)
        
        if os.path.isdir(file_path):
            # Navigate to directory
            self.path_combo.setCurrentText(file_path)
        else:
            # Open file
            self.open_selected_file()
            
    def on_path_changed(self, path):
        """Handle path change"""
        if os.path.exists(path):
            self.current_path = path
            self.refresh_file_list()
            
    def show_file_preview(self, file_path):
        """Show preview of selected file"""
        filename = os.path.basename(file_path)
        self.filename_label.setText(filename)
        self.filepath_label.setText(file_path)
        
        # File info
        try:
            stat = os.stat(file_path)
            size = self.format_file_size(stat.st_size)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            self.fileinfo_label.setText(f"Size: {size}, Modified: {modified}")
        except:
            self.fileinfo_label.setText("Unable to read file info")
            
        # Preview content (first few lines for G-code files)
        if file_path.lower().endswith(('.ngc', '.nc', '.gcode')):
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()[:20]  # First 20 lines
                    preview_text = ''.join(lines)
                    if len(lines) == 20:
                        preview_text += "\n... (file continues)"
                    self.preview_area.setPlainText(preview_text)
            except Exception as e:
                self.preview_area.setPlainText(f"Error reading file: {e}")
        else:
            self.preview_area.setPlainText("Preview not available for this file type")
            
        # Metadata
        metadata = self.metadata_cache.get(file_path, {})
        last_run = metadata.get('last_run', 'Never')
        if last_run != 'Never':
            last_run = datetime.fromisoformat(last_run).strftime("%Y-%m-%d %H:%M")
        self.metadata_label.setText(f"Last run: {last_run}")
        
    def clear_preview(self):
        """Clear the preview panel"""
        self.filename_label.setText("No file selected")
        self.filepath_label.setText("")
        self.fileinfo_label.setText("")
        self.preview_area.setPlainText("")
        self.metadata_label.setText("")
        self.open_btn.setEnabled(False)
        self.duplicate_btn.setEnabled(False)
        self.folder_btn.setEnabled(False)
        
    def open_selected_file(self):
        """Open the selected file"""
        items = self.file_tree.selectedItems()
        if not items:
            return
            
        file_path = items[0].data(0, Qt.UserRole)
        if os.path.isfile(file_path):
            # Update metadata
            self.metadata_cache[file_path] = {
                'last_run': datetime.now().isoformat(),
                'run_count': self.metadata_cache.get(file_path, {}).get('run_count', 0) + 1
            }
            self.save_metadata()
            self.show_file_preview(file_path)  # Refresh preview with new metadata
            self.file_opened.emit(file_path)
            
    def duplicate_to_profile(self):
        """Duplicate selected file to profile directory"""
        items = self.file_tree.selectedItems()
        if not items:
            return
            
        source_path = items[0].data(0, Qt.UserRole)
        if not os.path.isfile(source_path):
            return
            
        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.profile_dir, filename)
        
        # Handle name conflicts
        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            dest_path = os.path.join(self.profile_dir, f"{name}_{counter}{ext}")
            counter += 1
            
        try:
            shutil.copy2(source_path, dest_path)
            QMessageBox.information(self, "Success", f"File duplicated to:\n{dest_path}")
            
            # If we're viewing the profile directory, refresh
            if self.current_path == self.profile_dir:
                self.refresh_file_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to duplicate file:\n{e}")
            
    def open_containing_folder(self):
        """Open the containing folder in system file manager"""
        items = self.file_tree.selectedItems()
        if not items:
            return
            
        file_path = items[0].data(0, Qt.UserRole)
        folder_path = os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
        
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(['explorer', folder_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', folder_path])
            else:  # Linux
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not open folder:\n{e}")
            
    def add_mounted_share(self, name, path):
        """Add a mounted share to the location list"""
        if os.path.exists(path) and path not in [self.path_combo.itemData(i) for i in range(self.path_combo.count())]:
            self.path_combo.addItem(f"Share: {name}", path)
            self.mounted_shares.append((name, path))
            
    def remove_mounted_share(self, path):
        """Remove a mounted share from the location list"""
        for i in range(self.path_combo.count()):
            if self.path_combo.itemData(i) == path:
                self.path_combo.removeItem(i)
                break
        self.mounted_shares = [(n, p) for n, p in self.mounted_shares if p != path]