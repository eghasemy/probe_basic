"""
Touch Theme and Responsive Design Utilities
Phase 0 - Bootstrap & Theming

This module provides utilities for managing themes, responsive design,
and touch interface adaptations in the PB-Touch system.
"""

import os
from qtpy.QtCore import QObject, Signal, QSettings, QSize
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QScreen

from .touch_config import (
    THEME_VARIANTS, BREAKPOINTS, SIZE_CLASSES, 
    DEFAULT_CONFIG, get_size_class_for_screen,
    get_responsive_spacing, get_responsive_font_sizes
)


class TouchThemeManager(QObject):
    """
    Manages touch themes and responsive design adaptations
    """
    
    # Signals
    theme_changed = Signal(str)  # theme_name
    size_class_changed = Signal(str)  # size_class
    
    def __init__(self, vcp_dir=None):
        super().__init__()
        self.vcp_dir = vcp_dir or os.path.dirname(__file__)
        self.settings = QSettings('ProbeBasic', 'TouchTheme')
        self.current_theme = self.settings.value('theme', 'default')
        self.current_size_class = self.settings.value('size_class', 'normal')
        self._screen_monitor = None
        
        # Monitor screen changes
        if QApplication.instance():
            self._setup_screen_monitoring()
    
    def _setup_screen_monitoring(self):
        """Setup monitoring for screen size changes"""
        app = QApplication.instance()
        if app:
            app.screenAdded.connect(self._on_screen_changed)
            app.screenRemoved.connect(self._on_screen_changed)
            primary_screen = app.primaryScreen()
            if primary_screen:
                primary_screen.geometryChanged.connect(self._on_screen_geometry_changed)
    
    def _on_screen_changed(self, screen):
        """Handle screen addition/removal"""
        self._update_size_class_from_screen()
    
    def _on_screen_geometry_changed(self, geometry):
        """Handle screen geometry changes"""
        self._update_size_class_from_screen()
    
    def _update_size_class_from_screen(self):
        """Update size class based on current screen geometry"""
        app = QApplication.instance()
        if not app:
            return
            
        primary_screen = app.primaryScreen()
        if primary_screen:
            geometry = primary_screen.geometry()
            new_size_class = get_size_class_for_screen(geometry.width(), geometry.height())
            if new_size_class != self.current_size_class:
                self.set_size_class(new_size_class)
    
    def get_available_themes(self):
        """Get list of available themes"""
        return list(THEME_VARIANTS.keys())
    
    def get_theme_info(self, theme_name):
        """Get information about a specific theme"""
        return THEME_VARIANTS.get(theme_name, {})
    
    def get_current_theme(self):
        """Get current theme name"""
        return self.current_theme
    
    def get_current_size_class(self):
        """Get current size class"""
        return self.current_size_class
    
    def set_theme(self, theme_name):
        """
        Set the current theme
        
        Args:
            theme_name: Name of theme to set
            
        Returns:
            bool: True if theme was set successfully
        """
        if theme_name not in THEME_VARIANTS:
            return False
        
        old_theme = self.current_theme
        self.current_theme = theme_name
        self.settings.setValue('theme', theme_name)
        
        if old_theme != theme_name:
            self.theme_changed.emit(theme_name)
        
        return True
    
    def set_size_class(self, size_class):
        """
        Set the current size class
        
        Args:
            size_class: Size class to set ('compact', 'normal', 'large', 'extra_large')
            
        Returns:
            bool: True if size class was set successfully
        """
        if size_class not in SIZE_CLASSES:
            return False
        
        old_size_class = self.current_size_class
        self.current_size_class = size_class
        self.settings.setValue('size_class', size_class)
        
        if old_size_class != size_class:
            self.size_class_changed.emit(size_class)
        
        return True
    
    def get_theme_file_path(self, theme_name=None):
        """
        Get the full path to a theme file
        
        Args:
            theme_name: Theme name (uses current theme if None)
            
        Returns:
            str: Full path to theme file
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        theme_info = THEME_VARIANTS.get(theme_name, THEME_VARIANTS['default'])
        theme_file = theme_info.get('file', 'probe_basic.qss')
        
        # If it's a relative path, make it relative to VCP directory
        if not os.path.isabs(theme_file):
            theme_file = os.path.join(self.vcp_dir, theme_file)
        
        return theme_file
    
    def load_theme_stylesheet(self, theme_name=None):
        """
        Load stylesheet content for a theme
        
        Args:
            theme_name: Theme name (uses current theme if None)
            
        Returns:
            str: Stylesheet content, or empty string if file not found
        """
        theme_file = self.get_theme_file_path(theme_name)
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError):
            print(f"Warning: Could not load theme file: {theme_file}")
            return ""
    
    def apply_theme(self, app=None, theme_name=None):
        """
        Apply a theme to the application
        
        Args:
            app: QApplication instance (uses QApplication.instance() if None)
            theme_name: Theme name (uses current theme if None)
            
        Returns:
            bool: True if theme was applied successfully
        """
        if app is None:
            app = QApplication.instance()
        
        if not app:
            return False
        
        stylesheet = self.load_theme_stylesheet(theme_name)
        if stylesheet:
            # Apply responsive adjustments based on current size class
            stylesheet = self._apply_responsive_adjustments(stylesheet)
            app.setStyleSheet(stylesheet)
            return True
        
        return False
    
    def _apply_responsive_adjustments(self, stylesheet):
        """
        Apply responsive design adjustments to stylesheet
        
        Args:
            stylesheet: Base stylesheet content
            
        Returns:
            str: Modified stylesheet with responsive adjustments
        """
        size_config = SIZE_CLASSES.get(self.current_size_class, SIZE_CLASSES['normal'])
        spacing = get_responsive_spacing(self.current_size_class)
        font_sizes = get_responsive_font_sizes(self.current_size_class)
        
        # Simple variable substitution for responsive values
        # In a more sophisticated implementation, this could use a CSS preprocessor
        responsive_vars = {
            'button_height': size_config['button_height'],
            'input_height': size_config['input_height'],
            'icon_size': size_config['icon_size'],
            'spacing_small': spacing['small'],
            'spacing_medium': spacing['medium'],
            'spacing_large': spacing['large'],
            'font_small': font_sizes['small'],
            'font_medium': font_sizes['medium'],
            'font_large': font_sizes['large'],
        }
        
        # Replace placeholder variables in stylesheet
        for var_name, value in responsive_vars.items():
            placeholder = f"var({var_name})"
            stylesheet = stylesheet.replace(placeholder, f"{value}px")
        
        return stylesheet
    
    def get_current_screen_info(self):
        """
        Get information about the current screen
        
        Returns:
            dict: Screen information including size, DPI, etc.
        """
        app = QApplication.instance()
        if not app:
            return {}
        
        primary_screen = app.primaryScreen()
        if not primary_screen:
            return {}
        
        geometry = primary_screen.geometry()
        return {
            'width': geometry.width(),
            'height': geometry.height(),
            'dpi': primary_screen.logicalDotsPerInch(),
            'device_pixel_ratio': primary_screen.devicePixelRatio(),
            'size_class': get_size_class_for_screen(geometry.width(), geometry.height()),
        }


class ResponsiveWidget:
    """
    Mixin class for widgets that need responsive behavior
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._theme_manager = None
        self._responsive_enabled = True
    
    def set_theme_manager(self, theme_manager):
        """Set the theme manager for this widget"""
        if self._theme_manager:
            # Disconnect old manager
            self._theme_manager.size_class_changed.disconnect(self._on_size_class_changed)
        
        self._theme_manager = theme_manager
        if self._theme_manager:
            # Connect to new manager
            self._theme_manager.size_class_changed.connect(self._on_size_class_changed)
            # Apply current size class
            self._on_size_class_changed(self._theme_manager.get_current_size_class())
    
    def set_responsive_enabled(self, enabled):
        """Enable or disable responsive behavior"""
        self._responsive_enabled = enabled
    
    def _on_size_class_changed(self, size_class):
        """Handle size class changes"""
        if not self._responsive_enabled:
            return
        
        self._apply_size_class(size_class)
    
    def _apply_size_class(self, size_class):
        """Apply size class specific styling (override in subclasses)"""
        pass


class TouchStyleHelper:
    """
    Helper class for applying touch-friendly styling to widgets
    """
    
    @staticmethod
    def apply_touch_properties(widget, size_class='normal'):
        """
        Apply touch-friendly properties to a widget
        
        Args:
            widget: Widget to modify
            size_class: Size class to apply
        """
        size_config = SIZE_CLASSES.get(size_class, SIZE_CLASSES['normal'])
        
        # Set minimum size for touch targets
        if hasattr(widget, 'setMinimumSize'):
            min_size = QSize(size_config['button_height'], size_config['button_height'])
            widget.setMinimumSize(min_size)
        
        # Set properties for CSS styling
        widget.setProperty('touchOptimized', True)
        widget.setProperty('sizeClass', size_class)
        
        # Force style refresh
        if hasattr(widget, 'style'):
            style = widget.style()
            if style:
                style.unpolish(widget)
                style.polish(widget)
    
    @staticmethod
    def apply_size_class_to_layout(layout, size_class='normal'):
        """
        Apply size class spacing to a layout
        
        Args:
            layout: Layout to modify
            size_class: Size class to apply
        """
        spacing = get_responsive_spacing(size_class)
        
        if hasattr(layout, 'setSpacing'):
            layout.setSpacing(spacing['medium'])
        
        if hasattr(layout, 'setContentsMargins'):
            margin = spacing['large']
            layout.setContentsMargins(margin, margin, margin, margin)


def create_touch_theme_manager(vcp_dir=None):
    """
    Create and initialize a TouchThemeManager instance
    
    Args:
        vcp_dir: VCP directory path
        
    Returns:
        TouchThemeManager: Initialized theme manager
    """
    return TouchThemeManager(vcp_dir)


def apply_touch_optimizations(widget, theme_manager=None):
    """
    Apply touch optimizations to a widget
    
    Args:
        widget: Widget to optimize
        theme_manager: Theme manager instance (optional)
    """
    if isinstance(widget, ResponsiveWidget):
        if theme_manager:
            widget.set_theme_manager(theme_manager)
    
    if theme_manager:
        size_class = theme_manager.get_current_size_class()
    else:
        size_class = 'normal'
    
    TouchStyleHelper.apply_touch_properties(widget, size_class)