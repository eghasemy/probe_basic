"""
Settings Manager Widget
Phase 9 - Settings, Profiles & Network

Manages application settings including units, UI scale, theme, touchscreen mode, and language.
Integrates with existing touch configuration system.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                                QLabel, QComboBox, QCheckBox, QSlider, QPushButton,
                                QSpinBox, QDoubleSpinBox, QMessageBox, QTabWidget,
                                QFormLayout, QButtonGroup, QRadioButton)
    from PyQt5.QtCore import pyqtSignal, Qt
    from PyQt5.QtGui import QFont
except ImportError:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QComboBox, QCheckBox, QSlider, QPushButton,
                            QSpinBox, QDoubleSpinBox, QMessageBox, QTabWidget,
                            QFormLayout, QButtonGroup, QRadioButton, QFont)
    from PyQt4.QtCore import pyqtSignal, Qt

# Import touch configuration if available
try:
    from probe_basic.touch_config import (TOUCH_TARGET_MINIMUM, TOUCH_TARGET_PREFERRED,
                                         TOUCH_TARGET_LARGE, FONT_SIZES, THEME_VARIANTS,
                                         SIZE_CLASSES, TOUCH_SPACING, BREAKPOINTS)
except ImportError:
    # Fallback values if touch_config not available
    TOUCH_TARGET_MINIMUM = 44
    TOUCH_TARGET_PREFERRED = 48
    TOUCH_TARGET_LARGE = 56
    FONT_SIZES = {'small': 12, 'medium': 14, 'large': 16, 'extra_large': 18, 'title': 20}
    THEME_VARIANTS = {
        'default': {'name': 'Default Touch', 'file': 'themes/touch_theme.qss'},
        'high_contrast': {'name': 'High Contrast', 'file': 'themes/touch_theme_high_contrast.qss'},
        'dark': {'name': 'Dark Mode', 'file': 'themes/touch_theme_dark.qss'},
        'classic': {'name': 'Classic', 'file': 'probe_basic.qss'}
    }
    SIZE_CLASSES = {
        'compact': {'button_height': 36, 'font_scale': 0.9},
        'normal': {'button_height': 44, 'font_scale': 1.0},
        'large': {'button_height': 52, 'font_scale': 1.1},
        'extra_large': {'button_height': 60, 'font_scale': 1.2}
    }
    TOUCH_SPACING = {'small': 6, 'medium': 8, 'large': 12, 'extra_large': 16}
    BREAKPOINTS = {'small': 800, 'medium': 1024, 'large': 1920, 'extra_large': 2560}


class SettingsManager(QWidget):
    """
    Settings Manager Widget
    
    Manages application settings including:
    - Units (metric/imperial)
    - UI scale and touch targets
    - Theme selection
    - Touchscreen optimizations
    - Language (placeholder)
    """
    
    # Signals
    settings_changed = pyqtSignal(str, object)  # setting_name, value
    theme_changed = pyqtSignal(str)             # theme_name
    units_changed = pyqtSignal(str)             # units (metric/imperial)
    scale_changed = pyqtSignal(float)           # scale_factor
    restart_required = pyqtSignal()             # restart needed
    
    def __init__(self, parent=None):
        super(SettingsManager, self).__init__(parent)
        
        # Settings file location
        self.settings_dir = Path.home() / ".pb-touch" / "settings"
        self.settings_file = self.settings_dir / "settings.json"
        
        # Ensure settings directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Current settings
        self.settings = self.load_settings()
        
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Application Settings")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(header)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        
        # Units & Measurement tab
        self.units_tab = self.create_units_tab()
        self.tab_widget.addTab(self.units_tab, "Units")
        
        # Interface tab
        self.interface_tab = self.create_interface_tab()
        self.tab_widget.addTab(self.interface_tab, "Interface")
        
        # Touch Settings tab
        self.touch_tab = self.create_touch_tab()
        self.tab_widget.addTab(self.touch_tab, "Touch")
        
        # Advanced tab
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 4px; color: #666;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def create_units_tab(self):
        """Create units and measurement settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Units group
        units_group = QGroupBox("Units")
        units_layout = QFormLayout()
        
        # Units selection
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Imperial (inches)", "Metric (mm)"])
        self.units_combo.currentTextChanged.connect(self.on_setting_changed)
        units_layout.addRow("Default Units:", self.units_combo)
        
        # Linear units
        self.linear_units_combo = QComboBox()
        self.linear_units_combo.addItems(["inch", "mm"])
        self.linear_units_combo.currentTextChanged.connect(self.on_setting_changed)
        units_layout.addRow("Linear Units:", self.linear_units_combo)
        
        # Angular units
        self.angular_units_combo = QComboBox()
        self.angular_units_combo.addItems(["degree", "radian"])
        self.angular_units_combo.currentTextChanged.connect(self.on_setting_changed)
        units_layout.addRow("Angular Units:", self.angular_units_combo)
        
        # Feed rate units
        self.feed_units_combo = QComboBox()
        self.feed_units_combo.addItems(["units/min", "units/sec"])
        self.feed_units_combo.currentTextChanged.connect(self.on_setting_changed)
        units_layout.addRow("Feed Rate Units:", self.feed_units_combo)
        
        units_group.setLayout(units_layout)
        layout.addWidget(units_group)
        
        # Display precision
        precision_group = QGroupBox("Display Precision")
        precision_layout = QFormLayout()
        
        self.position_precision = QSpinBox()
        self.position_precision.setRange(0, 6)
        self.position_precision.setValue(4)
        self.position_precision.valueChanged.connect(self.on_setting_changed)
        precision_layout.addRow("Position (decimal places):", self.position_precision)
        
        self.velocity_precision = QSpinBox()
        self.velocity_precision.setRange(0, 4)
        self.velocity_precision.setValue(2)
        self.velocity_precision.valueChanged.connect(self.on_setting_changed)
        precision_layout.addRow("Velocity (decimal places):", self.velocity_precision)
        
        precision_group.setLayout(precision_layout)
        layout.addWidget(precision_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_interface_tab(self):
        """Create interface settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        theme_names = [info['name'] for info in THEME_VARIANTS.values()]
        self.theme_combo.addItems(theme_names)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addRow("Theme:", self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # UI Scale
        scale_group = QGroupBox("UI Scale")
        scale_layout = QFormLayout()
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(50, 200)  # 50% to 200%
        self.scale_slider.setValue(100)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_slider.setTickInterval(25)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        
        self.scale_label = QLabel("100%")
        scale_h_layout = QHBoxLayout()
        scale_h_layout.addWidget(self.scale_slider)
        scale_h_layout.addWidget(self.scale_label)
        
        scale_layout.addRow("Scale Factor:", scale_h_layout)
        
        # Font scale
        self.font_scale_combo = QComboBox()
        self.font_scale_combo.addItems(["Small", "Normal", "Large", "Extra Large"])
        self.font_scale_combo.setCurrentText("Normal")
        self.font_scale_combo.currentTextChanged.connect(self.on_setting_changed)
        scale_layout.addRow("Font Size:", self.font_scale_combo)
        
        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        
        self.fullscreen_check = QCheckBox()
        self.fullscreen_check.stateChanged.connect(self.on_setting_changed)
        window_layout.addRow("Start Fullscreen:", self.fullscreen_check)
        
        self.maximize_check = QCheckBox()
        self.maximize_check.stateChanged.connect(self.on_setting_changed)
        window_layout.addRow("Start Maximized:", self.maximize_check)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_touch_tab(self):
        """Create touch-specific settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Touch optimization
        touch_group = QGroupBox("Touch Optimization")
        touch_layout = QFormLayout()
        
        self.touch_enabled_check = QCheckBox()
        self.touch_enabled_check.setChecked(True)
        self.touch_enabled_check.stateChanged.connect(self.on_setting_changed)
        touch_layout.addRow("Enable Touch Mode:", self.touch_enabled_check)
        
        # Touch target size
        self.touch_size_combo = QComboBox()
        self.touch_size_combo.addItems(["Small (44px)", "Medium (48px)", "Large (56px)"])
        self.touch_size_combo.setCurrentText("Medium (48px)")
        self.touch_size_combo.currentTextChanged.connect(self.on_setting_changed)
        touch_layout.addRow("Touch Target Size:", self.touch_size_combo)
        
        # Touch spacing
        self.touch_spacing_combo = QComboBox()
        self.touch_spacing_combo.addItems(["Small", "Medium", "Large", "Extra Large"])
        self.touch_spacing_combo.setCurrentText("Medium")
        self.touch_spacing_combo.currentTextChanged.connect(self.on_setting_changed)
        touch_layout.addRow("Touch Spacing:", self.touch_spacing_combo)
        
        touch_group.setLayout(touch_layout)
        layout.addWidget(touch_group)
        
        # Industrial settings
        industrial_group = QGroupBox("Industrial Environment")
        industrial_layout = QFormLayout()
        
        self.glove_mode_check = QCheckBox()
        self.glove_mode_check.stateChanged.connect(self.on_setting_changed)
        industrial_layout.addRow("Glove Mode:", self.glove_mode_check)
        
        self.high_contrast_check = QCheckBox()
        self.high_contrast_check.stateChanged.connect(self.on_setting_changed)
        industrial_layout.addRow("High Contrast Mode:", self.high_contrast_check)
        
        self.vibration_feedback_check = QCheckBox()
        self.vibration_feedback_check.stateChanged.connect(self.on_setting_changed)
        industrial_layout.addRow("Vibration Feedback:", self.vibration_feedback_check)
        
        industrial_group.setLayout(industrial_layout)
        layout.addWidget(industrial_group)
        
        # Gestures
        gesture_group = QGroupBox("Gestures")
        gesture_layout = QFormLayout()
        
        self.momentum_scroll_check = QCheckBox()
        self.momentum_scroll_check.setChecked(True)
        self.momentum_scroll_check.stateChanged.connect(self.on_setting_changed)
        gesture_layout.addRow("Momentum Scrolling:", self.momentum_scroll_check)
        
        self.gesture_nav_check = QCheckBox()
        self.gesture_nav_check.setChecked(True)
        self.gesture_nav_check.stateChanged.connect(self.on_setting_changed)
        gesture_layout.addRow("Gesture Navigation:", self.gesture_nav_check)
        
        gesture_group.setLayout(gesture_layout)
        layout.addWidget(gesture_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Language (placeholder)
        language_group = QGroupBox("Language")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish (Coming Soon)", "French (Coming Soon)"])
        self.language_combo.currentTextChanged.connect(self.on_setting_changed)
        language_layout.addRow("Interface Language:", self.language_combo)
        
        language_group.setLayout(language_layout)
        layout.addWidget(language_group)
        
        # Accessibility
        accessibility_group = QGroupBox("Accessibility")
        accessibility_layout = QFormLayout()
        
        self.large_text_check = QCheckBox()
        self.large_text_check.stateChanged.connect(self.on_setting_changed)
        accessibility_layout.addRow("Large Text Mode:", self.large_text_check)
        
        self.reduce_motion_check = QCheckBox()
        self.reduce_motion_check.stateChanged.connect(self.on_setting_changed)
        accessibility_layout.addRow("Reduce Motion:", self.reduce_motion_check)
        
        self.enhanced_focus_check = QCheckBox()
        self.enhanced_focus_check.setChecked(True)
        self.enhanced_focus_check.stateChanged.connect(self.on_setting_changed)
        accessibility_layout.addRow("Enhanced Focus Indicators:", self.enhanced_focus_check)
        
        accessibility_group.setLayout(accessibility_layout)
        layout.addWidget(accessibility_group)
        
        # Performance
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout()
        
        self.animation_check = QCheckBox()
        self.animation_check.setChecked(True)
        self.animation_check.stateChanged.connect(self.on_setting_changed)
        performance_layout.addRow("Enable Animations:", self.animation_check)
        
        self.hardware_accel_check = QCheckBox()
        self.hardware_accel_check.setChecked(True)
        self.hardware_accel_check.stateChanged.connect(self.on_setting_changed)
        performance_layout.addRow("Hardware Acceleration:", self.hardware_accel_check)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        default_settings = {
            # Units
            'units': 'Imperial (inches)',
            'linear_units': 'inch',
            'angular_units': 'degree',
            'feed_units': 'units/min',
            'position_precision': 4,
            'velocity_precision': 2,
            
            # Interface
            'theme': 'Default Touch',
            'scale_factor': 100,
            'font_size': 'Normal',
            'fullscreen': False,
            'maximized': False,
            
            # Touch
            'touch_enabled': True,
            'touch_target_size': 'Medium (48px)',
            'touch_spacing': 'Medium',
            'glove_mode': False,
            'high_contrast': False,
            'vibration_feedback': False,
            'momentum_scrolling': True,
            'gesture_navigation': True,
            
            # Advanced
            'language': 'English',
            'large_text': False,
            'reduce_motion': False,
            'enhanced_focus': True,
            'animations': True,
            'hardware_acceleration': True
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
                
        return default_settings
        
    def load_current_settings(self):
        """Load current settings into UI controls"""
        # Units tab
        self.units_combo.setCurrentText(self.settings['units'])
        self.linear_units_combo.setCurrentText(self.settings['linear_units'])
        self.angular_units_combo.setCurrentText(self.settings['angular_units'])
        self.feed_units_combo.setCurrentText(self.settings['feed_units'])
        self.position_precision.setValue(self.settings['position_precision'])
        self.velocity_precision.setValue(self.settings['velocity_precision'])
        
        # Interface tab
        self.theme_combo.setCurrentText(self.settings['theme'])
        self.scale_slider.setValue(self.settings['scale_factor'])
        self.scale_label.setText(f"{self.settings['scale_factor']}%")
        self.font_scale_combo.setCurrentText(self.settings['font_size'])
        self.fullscreen_check.setChecked(self.settings['fullscreen'])
        self.maximize_check.setChecked(self.settings['maximized'])
        
        # Touch tab
        self.touch_enabled_check.setChecked(self.settings['touch_enabled'])
        self.touch_size_combo.setCurrentText(self.settings['touch_target_size'])
        self.touch_spacing_combo.setCurrentText(self.settings['touch_spacing'])
        self.glove_mode_check.setChecked(self.settings['glove_mode'])
        self.high_contrast_check.setChecked(self.settings['high_contrast'])
        self.vibration_feedback_check.setChecked(self.settings['vibration_feedback'])
        self.momentum_scroll_check.setChecked(self.settings['momentum_scrolling'])
        self.gesture_nav_check.setChecked(self.settings['gesture_navigation'])
        
        # Advanced tab
        self.language_combo.setCurrentText(self.settings['language'])
        self.large_text_check.setChecked(self.settings['large_text'])
        self.reduce_motion_check.setChecked(self.settings['reduce_motion'])
        self.enhanced_focus_check.setChecked(self.settings['enhanced_focus'])
        self.animation_check.setChecked(self.settings['animations'])
        self.hardware_accel_check.setChecked(self.settings['hardware_acceleration'])
        
    def on_setting_changed(self):
        """Handle setting change"""
        # Update settings from UI
        self.update_settings_from_ui()
        
    def on_theme_changed(self):
        """Handle theme change"""
        theme_name = self.theme_combo.currentText()
        self.settings['theme'] = theme_name
        self.theme_changed.emit(theme_name)
        
    def on_scale_changed(self):
        """Handle scale change"""
        scale_value = self.scale_slider.value()
        self.scale_label.setText(f"{scale_value}%")
        self.settings['scale_factor'] = scale_value
        self.scale_changed.emit(scale_value / 100.0)
        
    def update_settings_from_ui(self):
        """Update settings dictionary from UI controls"""
        # Units
        self.settings['units'] = self.units_combo.currentText()
        self.settings['linear_units'] = self.linear_units_combo.currentText()
        self.settings['angular_units'] = self.angular_units_combo.currentText()
        self.settings['feed_units'] = self.feed_units_combo.currentText()
        self.settings['position_precision'] = self.position_precision.value()
        self.settings['velocity_precision'] = self.velocity_precision.value()
        
        # Interface
        self.settings['theme'] = self.theme_combo.currentText()
        self.settings['scale_factor'] = self.scale_slider.value()
        self.settings['font_size'] = self.font_scale_combo.currentText()
        self.settings['fullscreen'] = self.fullscreen_check.isChecked()
        self.settings['maximized'] = self.maximize_check.isChecked()
        
        # Touch
        self.settings['touch_enabled'] = self.touch_enabled_check.isChecked()
        self.settings['touch_target_size'] = self.touch_size_combo.currentText()
        self.settings['touch_spacing'] = self.touch_spacing_combo.currentText()
        self.settings['glove_mode'] = self.glove_mode_check.isChecked()
        self.settings['high_contrast'] = self.high_contrast_check.isChecked()
        self.settings['vibration_feedback'] = self.vibration_feedback_check.isChecked()
        self.settings['momentum_scrolling'] = self.momentum_scroll_check.isChecked()
        self.settings['gesture_navigation'] = self.gesture_nav_check.isChecked()
        
        # Advanced
        self.settings['language'] = self.language_combo.currentText()
        self.settings['large_text'] = self.large_text_check.isChecked()
        self.settings['reduce_motion'] = self.reduce_motion_check.isChecked()
        self.settings['enhanced_focus'] = self.enhanced_focus_check.isChecked()
        self.settings['animations'] = self.animation_check.isChecked()
        self.settings['hardware_acceleration'] = self.hardware_accel_check.isChecked()
        
    def apply_settings(self):
        """Apply settings without saving"""
        self.update_settings_from_ui()
        
        # Emit relevant signals
        for setting, value in self.settings.items():
            self.settings_changed.emit(setting, value)
            
        self.status_label.setText("Settings applied")
        
    def save_settings(self):
        """Save settings to file"""
        try:
            self.update_settings_from_ui()
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
                
            self.status_label.setText("Settings saved")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
            
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove settings file and reload
            if self.settings_file.exists():
                self.settings_file.unlink()
                
            self.settings = self.load_settings()
            self.load_current_settings()
            self.status_label.setText("Settings reset to defaults")
            
    def get_setting(self, key: str, default=None) -> Any:
        """Get setting value"""
        return self.settings.get(key, default)
        
    def set_setting(self, key: str, value: Any):
        """Set setting value"""
        self.settings[key] = value
        
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
        
    def export_settings(self, export_path: str) -> bool:
        """Export settings to file"""
        try:
            with open(export_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception:
            return False
            
    def import_settings(self, import_path: str) -> bool:
        """Import settings from file"""
        try:
            with open(import_path, 'r') as f:
                imported_settings = json.load(f)
                self.settings.update(imported_settings)
                self.load_current_settings()
            return True
        except Exception:
            return False