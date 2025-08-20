"""
Touch-friendly base widgets for PB-Touch interface
Phase 0 - Bootstrap & Theming

This module provides base classes for creating touch-optimized widgets
that follow accessibility guidelines and best practices for industrial
touch screen interfaces.
"""

from qtpy.QtCore import Qt, QSize, Signal
from qtpy.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QSizePolicy
)
from qtpy.QtGui import QFont, QPalette


class TouchButton(QPushButton):
    """
    Touch-optimized button with minimum 44px touch target
    and enhanced visual feedback.
    """
    
    # Minimum touch target size for accessibility
    MIN_TOUCH_SIZE = 44
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_touch_properties()
    
    def _setup_touch_properties(self):
        """Configure touch-friendly properties"""
        # Set minimum size for touch accessibility
        self.setMinimumSize(self.MIN_TOUCH_SIZE, self.MIN_TOUCH_SIZE)
        
        # Enhanced size policy for responsive layout
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add properties for CSS styling
        self.setProperty("touchButton", True)
        
        # Enable mouse tracking for better hover feedback
        self.setMouseTracking(True)
    
    def sizeHint(self):
        """Provide size hint that respects touch target minimums"""
        hint = super().sizeHint()
        return QSize(
            max(hint.width(), self.MIN_TOUCH_SIZE),
            max(hint.height(), self.MIN_TOUCH_SIZE)
        )
    
    def set_button_type(self, button_type):
        """
        Set button type for styling purposes
        
        Args:
            button_type: 'primary', 'emergency', 'secondary'
        """
        # Clear existing type properties
        self.setProperty("primary", False)
        self.setProperty("emergency", False)
        self.setProperty("secondary", False)
        
        # Set new type
        if button_type in ['primary', 'emergency', 'secondary']:
            self.setProperty(button_type, True)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)


class TouchLabel(QLabel):
    """
    Touch-friendly label with enhanced readability
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_touch_properties()
    
    def _setup_touch_properties(self):
        """Configure touch-friendly properties"""
        # Set minimum font size for readability
        font = self.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
            self.setFont(font)
        
        # Add property for CSS styling
        self.setProperty("touchLabel", True)


class TouchFrame(QFrame):
    """
    Container frame optimized for touch layouts
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_touch_properties()
    
    def _setup_touch_properties(self):
        """Configure touch-friendly properties"""
        # Set appropriate margins and spacing
        self.setContentsMargins(8, 8, 8, 8)
        
        # Add property for CSS styling
        self.setProperty("touchFrame", True)


class TouchPanel(QWidget):
    """
    Base panel class for touch interface sections
    Provides consistent spacing and layout for touch interfaces
    """
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self._setup_layout()
        self._setup_touch_properties()
    
    def _setup_layout(self):
        """Setup the basic layout structure"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(12)  # Touch-friendly spacing
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Add title if provided
        if self.title:
            self.title_label = TouchLabel(self.title)
            self.title_label.setProperty("panelTitle", True)
            font = self.title_label.font()
            font.setPointSize(16)
            font.setBold(True)
            self.title_label.setFont(font)
            self.main_layout.addWidget(self.title_label)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_widget)
    
    def _setup_touch_properties(self):
        """Configure touch-friendly properties"""
        # Add property for CSS styling
        self.setProperty("touchPanel", True)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def add_widget(self, widget):
        """Add a widget to the content area"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the content area"""
        self.content_layout.addLayout(layout)


class TouchButtonRow(QWidget):
    """
    Horizontal row of touch buttons with consistent spacing
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_layout()
        self._setup_touch_properties()
        self.buttons = []
    
    def _setup_layout(self):
        """Setup horizontal layout for buttons"""
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(8)  # Touch-friendly spacing between buttons
        self.layout.setContentsMargins(0, 0, 0, 0)
    
    def _setup_touch_properties(self):
        """Configure touch-friendly properties"""
        self.setProperty("touchButtonRow", True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    def add_button(self, text, callback=None, button_type="secondary"):
        """
        Add a button to the row
        
        Args:
            text: Button text
            callback: Function to call when button is clicked
            button_type: 'primary', 'emergency', 'secondary'
        
        Returns:
            TouchButton: The created button
        """
        button = TouchButton(text)
        button.set_button_type(button_type)
        
        if callback:
            button.clicked.connect(callback)
        
        self.buttons.append(button)
        self.layout.addWidget(button)
        
        return button
    
    def add_stretch(self):
        """Add a stretch to push buttons to one side"""
        self.layout.addStretch()


class ResponsiveLayout:
    """
    Utility class for creating responsive layouts that adapt to screen size
    """
    
    @staticmethod
    def get_screen_size_class():
        """
        Determine screen size class for responsive design
        
        Returns:
            str: 'small', 'medium', 'large'
        """
        # This would typically get the actual screen size
        # For now, return 'medium' as default
        # In a real implementation, this would check screen dimensions
        return 'medium'
    
    @staticmethod
    def get_touch_spacing(size_class='medium'):
        """
        Get appropriate spacing for touch interface based on screen size
        
        Args:
            size_class: 'small', 'medium', 'large'
        
        Returns:
            dict: Spacing values for different elements
        """
        spacing_config = {
            'small': {
                'button_spacing': 6,
                'panel_margin': 12,
                'content_spacing': 6
            },
            'medium': {
                'button_spacing': 8,
                'panel_margin': 16,
                'content_spacing': 8
            },
            'large': {
                'button_spacing': 12,
                'panel_margin': 20,
                'content_spacing': 12
            }
        }
        
        return spacing_config.get(size_class, spacing_config['medium'])


class TouchThemeManager:
    """
    Manager for touch theme configuration and switching
    """
    
    def __init__(self):
        self.current_theme = 'default'
        self.available_themes = {
            'default': 'probe_basic.qss',
            'touch': 'themes/touch_theme.qss'
        }
    
    def get_theme_path(self, theme_name):
        """Get the path to a theme file"""
        return self.available_themes.get(theme_name, self.available_themes['default'])
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.available_themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_current_theme_path(self):
        """Get the path to the current theme"""
        return self.get_theme_path(self.current_theme)


# Convenience function for creating common touch widget combinations
def create_touch_button_panel(title, buttons_config):
    """
    Create a panel with a title and buttons
    
    Args:
        title: Panel title
        buttons_config: List of dicts with button configuration
                       [{'text': 'Button', 'callback': func, 'type': 'primary'}, ...]
    
    Returns:
        TouchPanel: Configured panel with buttons
    """
    panel = TouchPanel(title)
    button_row = TouchButtonRow()
    
    for config in buttons_config:
        button_row.add_button(
            config.get('text', ''),
            config.get('callback'),
            config.get('type', 'secondary')
        )
    
    panel.add_widget(button_row)
    return panel