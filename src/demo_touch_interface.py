#!/usr/bin/env python3
"""
PB-Touch Interface Demo and Test Script
Phase 0 - Bootstrap & Theming

This script demonstrates the touch interface components and provides
a simple test environment for validating the touch theming system.
"""

import sys
import os

# Add the source path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from qtpy.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
        QWidget, QLabel, QComboBox, QPushButton, QScrollArea,
        QTabWidget, QGroupBox, QCheckBox
    )
    from qtpy.QtCore import Qt, QTimer
    from qtpy.QtGui import QFont
    
    # Import touch interface components
    from probe_basic.touch_widgets import (
        TouchButton, TouchPanel, TouchButtonRow, TouchLabel,
        TouchFrame, create_touch_button_panel
    )
    from probe_basic.touch_utils import (
        TouchThemeManager, TouchStyleHelper, apply_touch_optimizations
    )
    from probe_basic.touch_config import THEME_VARIANTS, SIZE_CLASSES
    
except ImportError as e:
    print(f"Import error: {e}")
    print("This demo requires QtPy and the PB-Touch modules.")
    print("Some dependencies may not be available in this environment.")
    sys.exit(1)


class TouchInterfaceDemo(QMainWindow):
    """Demo application for PB-Touch interface components"""
    
    def __init__(self):
        super().__init__()
        self.theme_manager = None
        self.init_ui()
        self.init_theme_system()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PB-Touch Interface Demo - Phase 0")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("PB-Touch Interface Demo")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        main_layout.addWidget(title)
        
        # Theme controls
        theme_controls = self.create_theme_controls()
        main_layout.addWidget(theme_controls)
        
        # Tab widget for demos
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Add demo tabs
        tab_widget.addTab(self.create_button_demo(), "Touch Buttons")
        tab_widget.addTab(self.create_panel_demo(), "Touch Panels")
        tab_widget.addTab(self.create_size_demo(), "Responsive Sizing")
        tab_widget.addTab(self.create_theme_preview(), "Theme Preview")
    
    def create_theme_controls(self):
        """Create theme selection controls"""
        group = QGroupBox("Theme Controls")
        layout = QHBoxLayout(group)
        
        # Theme selector
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEME_VARIANTS.keys()))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # Size class selector
        layout.addWidget(QLabel("Size Class:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(list(SIZE_CLASSES.keys()))
        self.size_combo.currentTextChanged.connect(self.on_size_class_changed)
        layout.addWidget(self.size_combo)
        
        # Apply button
        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self.apply_current_theme)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
        return group
    
    def create_button_demo(self):
        """Create button demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Standard buttons
        std_group = QGroupBox("Standard Touch Buttons")
        std_layout = QVBoxLayout(std_group)
        
        button_row1 = TouchButtonRow()
        button_row1.add_button("Primary", button_type="primary")
        button_row1.add_button("Secondary", button_type="secondary")
        button_row1.add_button("Emergency", button_type="emergency")
        std_layout.addWidget(button_row1)
        
        button_row2 = TouchButtonRow()
        button_row2.add_button("Start", callback=lambda: self.show_message("Start clicked"))
        button_row2.add_button("Stop", callback=lambda: self.show_message("Stop clicked"))
        button_row2.add_button("Reset", callback=lambda: self.show_message("Reset clicked"))
        std_layout.addWidget(button_row2)
        
        layout.addWidget(std_group)
        
        # Size variants
        size_group = QGroupBox("Button Size Variants")
        size_layout = QVBoxLayout(size_group)
        
        for size_name, size_config in SIZE_CLASSES.items():
            btn = TouchButton(f"{size_name.title()} ({size_config['button_height']}px)")
            TouchStyleHelper.apply_touch_properties(btn, size_name)
            size_layout.addWidget(btn)
        
        layout.addWidget(size_group)
        layout.addStretch()
        
        return widget
    
    def create_panel_demo(self):
        """Create panel demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create demo panels
        control_panel = TouchPanel("Machine Controls")
        button_row = TouchButtonRow()
        button_row.add_button("Home All", button_type="primary")
        button_row.add_button("Emergency Stop", button_type="emergency")
        control_panel.add_widget(button_row)
        layout.addWidget(control_panel)
        
        # Settings panel using convenience function
        settings_config = [
            {'text': 'Load Config', 'type': 'secondary'},
            {'text': 'Save Config', 'type': 'primary'},
            {'text': 'Reset to Default', 'type': 'secondary'}
        ]
        settings_panel = create_touch_button_panel("Settings", settings_config)
        layout.addWidget(settings_panel)
        
        layout.addStretch()
        
        return widget
    
    def create_size_demo(self):
        """Create responsive sizing demonstration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_label = TouchLabel(
            "This tab demonstrates responsive sizing. "
            "Change the size class above to see how elements adapt."
        )
        layout.addWidget(info_label)
        
        # Create elements that respond to size changes
        self.responsive_elements = []
        
        for i, (size_name, size_config) in enumerate(SIZE_CLASSES.items()):
            group = QGroupBox(f"{size_name.title()} Size Class")
            group_layout = QHBoxLayout(group)
            
            btn = TouchButton(f"Button ({size_config['button_height']}px)")
            TouchStyleHelper.apply_touch_properties(btn, size_name)
            group_layout.addWidget(btn)
            
            label = TouchLabel(f"Font scale: {size_config['font_scale']}")
            group_layout.addWidget(label)
            
            layout.addWidget(group)
            self.responsive_elements.append((btn, label, size_name))
        
        layout.addStretch()
        
        return widget
    
    def create_theme_preview(self):
        """Create theme preview tab"""
        scroll = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme information
        for theme_name, theme_info in THEME_VARIANTS.items():
            group = QGroupBox(theme_info.get('name', theme_name))
            group_layout = QVBoxLayout(group)
            
            desc = TouchLabel(theme_info.get('description', 'No description'))
            group_layout.addWidget(desc)
            
            file_label = TouchLabel(f"File: {theme_info.get('file', 'Unknown')}")
            group_layout.addWidget(file_label)
            
            # Preview button
            preview_btn = TouchButton(f"Preview {theme_name}")
            preview_btn.clicked.connect(lambda checked, t=theme_name: self.preview_theme(t))
            group_layout.addWidget(preview_btn)
            
            layout.addWidget(group)
        
        layout.addStretch()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        
        return scroll
    
    def init_theme_system(self):
        """Initialize the theme management system"""
        try:
            # Get the directory containing this script
            demo_dir = os.path.dirname(os.path.abspath(__file__))
            vcp_dir = os.path.join(demo_dir, '..', 'probe_basic')
            
            self.theme_manager = TouchThemeManager(vcp_dir)
            
            # Set initial values
            self.theme_combo.setCurrentText(self.theme_manager.get_current_theme())
            self.size_combo.setCurrentText(self.theme_manager.get_current_size_class())
            
            # Apply initial theme
            QTimer.singleShot(100, self.apply_current_theme)
            
        except Exception as e:
            print(f"Failed to initialize theme system: {e}")
            self.theme_manager = None
    
    def on_theme_changed(self, theme_name):
        """Handle theme selection change"""
        if self.theme_manager:
            self.theme_manager.set_theme(theme_name)
    
    def on_size_class_changed(self, size_class):
        """Handle size class change"""
        if self.theme_manager:
            self.theme_manager.set_size_class(size_class)
        
        # Update responsive elements
        if hasattr(self, 'responsive_elements'):
            for btn, label, element_size in self.responsive_elements:
                # Highlight the current size class
                if element_size == size_class:
                    btn.setProperty("highlighted", True)
                else:
                    btn.setProperty("highlighted", False)
                
                # Force style update
                btn.style().unpolish(btn)
                btn.style().polish(btn)
    
    def apply_current_theme(self):
        """Apply the current theme to the application"""
        if not self.theme_manager:
            return
        
        app = QApplication.instance()
        if app:
            success = self.theme_manager.apply_theme(app)
            if success:
                self.show_message(f"Applied theme: {self.theme_manager.get_current_theme()}")
            else:
                self.show_message("Failed to apply theme")
    
    def preview_theme(self, theme_name):
        """Preview a specific theme"""
        if self.theme_manager:
            old_theme = self.theme_manager.get_current_theme()
            self.theme_manager.set_theme(theme_name)
            self.apply_current_theme()
            self.theme_combo.setCurrentText(theme_name)
    
    def show_message(self, message):
        """Show a message in the status bar"""
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(message, 3000)
        else:
            print(f"Message: {message}")


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set up basic application properties
    app.setApplicationName("PB-Touch Demo")
    app.setApplicationVersion("Phase 0")
    app.setOrganizationName("Probe Basic")
    
    # Create and show the demo window
    demo = TouchInterfaceDemo()
    demo.show()
    
    # Center the window
    screen = app.primaryScreen().geometry()
    size = demo.geometry()
    demo.move(
        (screen.width() - size.width()) // 2,
        (screen.height() - size.height()) // 2
    )
    
    print("PB-Touch Interface Demo - Phase 0")
    print("This demo showcases the touch interface components and theming system.")
    print("Use the theme controls to test different themes and size classes.")
    
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())