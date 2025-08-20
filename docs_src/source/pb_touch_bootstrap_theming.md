# PB-Touch Bootstrap & Theming Guide

## Phase 0 - Bootstrap & Theming

This document outlines the foundational bootstrap infrastructure and touch-friendly theming system implemented for the PB-Touch project.

## Overview

The PB-Touch system extends Probe Basic with a modern, touch-optimized interface designed for industrial environments. Phase 0 establishes the core infrastructure that subsequent phases will build upon.

## Features Implemented

### 1. Touch-Optimized Themes

#### Standard Touch Theme (`touch_theme.qss`)
- Minimum 44px touch targets (WCAG 2.1 AA compliant)
- High contrast colors for industrial visibility
- Responsive design elements
- Modern visual design with rounded corners and gradients

#### High Contrast Theme (`touch_theme_high_contrast.qss`)
- Maximum contrast ratios for bright environments
- Enhanced visibility for users wearing safety glasses
- 48px minimum touch targets for improved accessibility
- Bold borders and high-contrast color schemes

### 2. Touch Widget Framework

#### Base Classes
- `TouchButton`: Touch-optimized button with enhanced feedback
- `TouchLabel`: High-readability label with appropriate font sizing
- `TouchFrame`: Container optimized for touch layouts
- `TouchPanel`: Structured panel with consistent spacing
- `TouchButtonRow`: Horizontal button layout with proper spacing

#### Widget Features
- Minimum touch target sizes
- Enhanced visual feedback (hover, pressed states)
- Responsive sizing based on screen size
- Consistent spacing and margins
- Accessibility-compliant design

### 3. Responsive Design System

#### Screen Size Classes
- **Compact**: < 800px width (tablets in portrait)
- **Normal**: 800-1024px width (small desktop/large tablet)
- **Large**: 1024-1920px width (desktop)
- **Extra Large**: > 1920px width (high-res displays)

#### Adaptive Elements
- Button sizes scale with screen size
- Font sizes adjust for readability
- Spacing adapts to maintain proper touch targets
- Layout adjusts for different orientations

### 4. Theme Management System

#### TouchThemeManager
- Dynamic theme switching
- Automatic screen size detection
- Responsive design adjustments
- Settings persistence
- Theme file management

#### Available Themes
- **Default Touch**: Standard touch-optimized theme
- **High Contrast**: Enhanced contrast for bright environments
- **Classic**: Traditional Probe Basic styling (backward compatibility)

### 5. Configuration System

#### INI File Settings
```ini
[DISPLAY]
# Enable touch optimizations
TOUCH_OPTIMIZED = true

# Set touch theme
TOUCH_THEME = default

# Touch-specific settings
TOUCH_TARGET_SIZE = 44
TOUCH_SPACING = medium
```

#### Configuration Options
- Touch target sizes (44px, 48px, 56px)
- Spacing preferences (small, medium, large)
- Theme variants
- Accessibility options
- Industrial environment settings

## Usage Examples

### 1. Creating Touch-Friendly Widgets

```python
from probe_basic.touch_widgets import TouchButton, TouchPanel, TouchButtonRow

# Create a touch-optimized button
button = TouchButton("Emergency Stop")
button.set_button_type("emergency")

# Create a panel with touch-friendly layout
panel = TouchPanel("Control Panel")
button_row = TouchButtonRow()
button_row.add_button("Start", callback=start_machine, button_type="primary")
button_row.add_button("Stop", callback=stop_machine, button_type="emergency")
panel.add_widget(button_row)
```

### 2. Applying Touch Themes

```python
from probe_basic.touch_utils import create_touch_theme_manager

# Create theme manager
theme_manager = create_touch_theme_manager()

# Set high contrast theme
theme_manager.set_theme("high_contrast")

# Apply to application
app = QApplication.instance()
theme_manager.apply_theme(app)
```

### 3. Responsive Widget Implementation

```python
from probe_basic.touch_utils import ResponsiveWidget, TouchStyleHelper

class MyTouchWidget(ResponsiveWidget, QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _apply_size_class(self, size_class):
        """Override to handle size class changes"""
        TouchStyleHelper.apply_touch_properties(self, size_class)
        # Apply custom responsive behavior
```

## Design Guidelines

### Touch Target Sizes
- **Minimum**: 44px (WCAG 2.1 AA)
- **Preferred**: 48px (better usability)
- **Large**: 56px (critical actions)

### Spacing
- **Tight**: 6px (dense layouts)
- **Standard**: 8px (normal spacing)
- **Generous**: 12px (accessibility)
- **Maximum**: 16px (critical separations)

### Colors
- High contrast ratios (4.5:1 minimum)
- Industrial-appropriate color palette
- Clear visual hierarchy
- Accessible color combinations

### Typography
- Minimum 12pt font size
- Bold weights for important text
- High contrast text/background
- Readable fonts (Bebas Kai)

## Industrial Environment Considerations

### Bright Lighting
- High contrast themes available
- Maximum contrast ratios
- Anti-glare color schemes

### Gloved Operation
- Larger touch targets (48px+)
- Enhanced touch sensitivity
- Clear visual feedback

### Safety Glasses
- Enhanced contrast
- Larger text sizes
- Clear visual indicators

## Accessibility Features

### WCAG 2.1 AA Compliance
- Minimum 44px touch targets
- 4.5:1 contrast ratios
- Keyboard navigation support
- Focus indicators

### Additional Features
- Large text mode
- High contrast mode
- Reduced motion options
- Enhanced focus indicators

## Future Enhancements

### Planned Features
- Voice command integration
- Haptic feedback support
- Gesture navigation
- Dynamic font scaling
- Theme customization tools

### Integration Points
- Machine configuration wizards
- Diagnostic interfaces
- Safety systems
- Network configuration

## Testing and Validation

### Screen Sizes Tested
- 7" tablet (1024x600)
- 10" tablet (1280x800)
- 15" desktop (1920x1080)
- 22" desktop (1920x1080)

### Input Methods
- Finger touch
- Stylus input
- Gloved operation
- Mouse/trackpad

### Environmental Conditions
- Indoor lighting
- Bright workshop lighting
- Outdoor visibility
- Safety glasses usage

## Conclusion

Phase 0 establishes a solid foundation for the PB-Touch project with:
- Modern, accessible touch interface design
- Responsive layout system
- Industrial environment optimization
- Comprehensive theme management
- Backward compatibility with existing Probe Basic configurations

This infrastructure provides the necessary building blocks for subsequent phases to implement specific functionality while maintaining consistency and usability across the entire system.