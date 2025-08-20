#!/usr/bin/env python
"""
Phase 10 Help Overlay System
Contextual help system with "?" button for probe_basic widgets
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

try:
    from PyQt5.QtWidgets import (
        QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
        QTextEdit, QDialog, QFrame, QApplication, QScrollArea
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPalette, QPixmap
    QT_AVAILABLE = True
except ImportError:
    # Define dummy classes when Qt is not available
    QT_AVAILABLE = False
    
    class QDialog:
        def __init__(self, *args, **kwargs): pass
        def setWindowTitle(self, title): pass
        def setModal(self, modal): pass
        def setFixedSize(self, width, height): pass
        def setStyleSheet(self, style): pass
        def exec_(self): pass
        def accept(self): pass
    
    class QPushButton:
        def __init__(self, *args, **kwargs): pass
        def setFixedSize(self, width, height): pass
        def setStyleSheet(self, style): pass
        def setToolTip(self, tip): pass
        def clicked(self): return MockSignal()
    
    class QWidget:
        def __init__(self, *args, **kwargs): pass
        def width(self): return 100
    
    class MockSignal:
        def connect(self, callback): pass
        def emit(self, *args): pass
    
    def pyqtSignal(*args): return MockSignal()

try:
    from probe_basic.logging_config import get_ui_logger
    logger = get_ui_logger()
except ImportError:
    # Fallback logging when probe_basic not available
    import logging
    logger = logging.getLogger('help_system')

class HelpOverlay(QDialog):
    """Modal help overlay dialog with contextual information"""
    
    def __init__(self, widget_name: str, help_data: Dict[str, Any], parent=None):
        if not QT_AVAILABLE:
            raise ImportError("PyQt5 not available for HelpOverlay")
            
        super().__init__(parent)
        self.widget_name = widget_name
        self.help_data = help_data
        
        self.setWindowTitle(f"Help: {widget_name}")
        self.setModal(True)
        self.setFixedSize(600, 400)
        
        # Style for overlay
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 2px solid #0078d4;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the help overlay UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(self.help_data.get('title', self.widget_name))
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        if 'description' in self.help_data:
            desc_label = QLabel(self.help_data['description'])
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Content area with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Usage instructions
        if 'usage' in self.help_data:
            usage_label = QLabel("Usage:")
            usage_font = QFont()
            usage_font.setBold(True)
            usage_label.setFont(usage_font)
            content_layout.addWidget(usage_label)
            
            usage_text = QTextEdit()
            usage_text.setPlainText(self.help_data['usage'])
            usage_text.setMaximumHeight(120)
            content_layout.addWidget(usage_text)
        
        # Tips
        if 'tips' in self.help_data and self.help_data['tips']:
            tips_label = QLabel("Tips:")
            tips_font = QFont()
            tips_font.setBold(True)
            tips_label.setFont(tips_font)
            content_layout.addWidget(tips_label)
            
            for tip in self.help_data['tips']:
                tip_label = QLabel(f"• {tip}")
                tip_label.setWordWrap(True)
                content_layout.addWidget(tip_label)
        
        # Safety notes
        if 'safety' in self.help_data and self.help_data['safety']:
            safety_label = QLabel("⚠️ Safety Notes:")
            safety_font = QFont()
            safety_font.setBold(True)
            safety_label.setFont(safety_font)
            safety_label.setStyleSheet("color: #ff9500;")
            content_layout.addWidget(safety_label)
            
            for safety_note in self.help_data['safety']:
                safety_note_label = QLabel(f"• {safety_note}")
                safety_note_label.setWordWrap(True)
                safety_note_label.setStyleSheet("color: #ff9500;")
                content_layout.addWidget(safety_note_label)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if 'related_docs' in self.help_data:
            docs_button = QPushButton("View Documentation")
            docs_button.clicked.connect(self._open_documentation)
            button_layout.addWidget(docs_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _open_documentation(self):
        """Open related documentation"""
        import webbrowser
        docs_url = self.help_data.get('related_docs', '')
        if docs_url:
            webbrowser.open(docs_url)
            logger.info(f"Opened documentation for {self.widget_name}: {docs_url}")

class HelpButton(QPushButton):
    """Help button widget that shows contextual help"""
    
    help_requested = pyqtSignal(str)  # Signal emitted when help is requested
    
    def __init__(self, widget_name: str, parent=None):
        if not QT_AVAILABLE:
            raise ImportError("PyQt5 not available for HelpButton")
            
        super().__init__("?", parent)
        self.widget_name = widget_name
        
        # Style the help button
        self.setFixedSize(24, 24)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        self.setToolTip(f"Click for help with {widget_name}")
        self.clicked.connect(self._show_help)
        
    def _show_help(self):
        """Show help for this widget"""
        self.help_requested.emit(self.widget_name)

class HelpManager:
    """Manages contextual help for probe_basic widgets"""
    
    def __init__(self, help_data_dir: Optional[Path] = None):
        self.help_data_dir = help_data_dir or Path(__file__).parent / 'help_data'
        self.help_data: Dict[str, Dict[str, Any]] = {}
        self.load_help_data()
        
    def load_help_data(self):
        """Load help data from JSON files"""
        if not self.help_data_dir.exists():
            logger.warning(f"Help data directory not found: {self.help_data_dir}")
            return
            
        for help_file in self.help_data_dir.glob('*.json'):
            try:
                with open(help_file, 'r') as f:
                    data = json.load(f)
                    widget_name = help_file.stem
                    self.help_data[widget_name] = data
                    logger.debug(f"Loaded help data for {widget_name}")
            except Exception as e:
                logger.error(f"Error loading help data from {help_file}: {e}")
    
    def get_help_data(self, widget_name: str) -> Dict[str, Any]:
        """Get help data for a widget"""
        return self.help_data.get(widget_name, self._get_default_help_data(widget_name))
    
    def _get_default_help_data(self, widget_name: str) -> Dict[str, Any]:
        """Get default help data for unknown widgets"""
        return {
            'title': widget_name.replace('_', ' ').title(),
            'description': f'This is the {widget_name} component.',
            'usage': f'Use the {widget_name} to interact with the system.',
            'tips': ['Click on controls to activate them', 'Use keyboard shortcuts when available'],
            'safety': ['Always ensure machine is in a safe state before operation']
        }
    
    def show_help(self, widget_name: str, parent=None):
        """Show help overlay for a widget"""
        if not QT_AVAILABLE:
            logger.error("Cannot show help: PyQt5 not available")
            return
            
        help_data = self.get_help_data(widget_name)
        overlay = HelpOverlay(widget_name, help_data, parent)
        overlay.exec_()
        logger.info(f"Showed help for {widget_name}")
    
    def add_help_button(self, widget: QWidget, widget_name: str) -> HelpButton:
        """Add a help button to a widget"""
        if not QT_AVAILABLE:
            raise ImportError("PyQt5 not available for help button")
            
        help_button = HelpButton(widget_name, widget)
        help_button.help_requested.connect(lambda name: self.show_help(name, widget))
        
        # Position the help button in the top-right corner of the widget
        help_button.move(widget.width() - 30, 6)
        
        return help_button
    
    def add_help_data(self, widget_name: str, help_data: Dict[str, Any]):
        """Add help data for a widget programmatically"""
        self.help_data[widget_name] = help_data
        logger.debug(f"Added help data for {widget_name}")

# Global help manager instance
_help_manager: Optional[HelpManager] = None

def get_help_manager() -> HelpManager:
    """Get the global help manager instance"""
    global _help_manager
    if _help_manager is None:
        _help_manager = HelpManager()
    return _help_manager

def show_widget_help(widget_name: str, parent=None):
    """Convenience function to show help for a widget"""
    get_help_manager().show_help(widget_name, parent)

def add_help_button_to_widget(widget: QWidget, widget_name: str) -> Optional[HelpButton]:
    """Convenience function to add help button to a widget"""
    if not QT_AVAILABLE:
        return None
    return get_help_manager().add_help_button(widget, widget_name)