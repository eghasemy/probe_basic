"""
Touch Interface Configuration for PB-Touch
Phase 0 - Bootstrap & Theming

This module provides configuration settings and constants for the
touch-optimized interface, including accessibility guidelines,
responsive design breakpoints, and touch interaction parameters.
"""

# Touch Target Sizes (following WCAG 2.1 AA guidelines)
TOUCH_TARGET_MINIMUM = 44  # pixels - minimum touch target size
TOUCH_TARGET_PREFERRED = 48  # pixels - preferred touch target size for better UX
TOUCH_TARGET_LARGE = 56  # pixels - large touch targets for critical actions

# Spacing and Layout
TOUCH_SPACING = {
    'small': 6,     # pixels - tight spacing for dense layouts
    'medium': 8,    # pixels - standard spacing
    'large': 12,    # pixels - generous spacing for accessibility
    'extra_large': 16  # pixels - maximum spacing for critical separations
}

# Font Sizes for Touch Interface
FONT_SIZES = {
    'small': 12,    # pt - minimum readable size
    'medium': 14,   # pt - standard text size
    'large': 16,    # pt - headers and important text
    'extra_large': 18,  # pt - critical information
    'title': 20     # pt - panel titles and main headers
}

# Screen Size Breakpoints
BREAKPOINTS = {
    'small': 800,    # pixels width - tablets in portrait
    'medium': 1024,  # pixels width - small desktop/large tablet
    'large': 1920,   # pixels width - full desktop
    'extra_large': 2560  # pixels width - high-res displays
}

# Touch Interaction Timing
INTERACTION_TIMING = {
    'tap_duration': 250,     # ms - maximum duration for tap vs hold
    'hold_duration': 500,    # ms - minimum duration to register as hold
    'double_tap_interval': 300,  # ms - maximum interval between taps
    'hover_delay': 100,      # ms - delay before hover effects
    'animation_duration': 200  # ms - standard animation duration
}

# Color Palette for Touch Theme
COLORS = {
    # Background colors
    'background_primary': '#1e1e1e',    # Main background
    'background_secondary': '#2a2a2a',  # Secondary panels
    'background_tertiary': '#3d3d3d',   # Input fields, buttons
    
    # Text colors
    'text_primary': '#ffffff',          # Main text
    'text_secondary': '#cccccc',        # Secondary text
    'text_disabled': '#666666',         # Disabled text
    
    # Accent colors
    'accent_primary': '#0077dd',        # Primary actions
    'accent_secondary': '#0099ff',      # Secondary actions
    'accent_success': '#22cc22',        # Success states
    'accent_warning': '#ffaa00',        # Warning states
    'accent_error': '#dd3333',          # Error states
    'accent_emergency': '#ff2222',      # Emergency/critical actions
    
    # Border colors
    'border_normal': '#666666',         # Standard borders
    'border_hover': '#888888',          # Hover state borders
    'border_focus': '#0099ff',          # Focus state borders
    'border_disabled': '#444444',       # Disabled borders
}

# Touch Gesture Configuration
GESTURES = {
    'pan_threshold': 10,        # pixels - minimum movement to register pan
    'pinch_threshold': 20,      # pixels - minimum scale change for pinch
    'swipe_threshold': 50,      # pixels - minimum distance for swipe
    'swipe_velocity': 500,      # pixels/second - minimum velocity for swipe
}

# Accessibility Settings
ACCESSIBILITY = {
    'high_contrast_mode': False,        # Enhanced contrast for visibility
    'large_text_mode': False,           # Larger text for readability
    'reduce_motion': False,             # Reduced animations for sensitivity
    'focus_indicators': True,           # Enhanced focus indicators
    'keyboard_navigation': True,        # Full keyboard navigation support
}

# Industrial Environment Settings
INDUSTRIAL = {
    'glove_mode': False,               # Enhanced touch sensitivity for gloves
    'bright_ambient_mode': False,      # High contrast for bright environments
    'vibration_feedback': False,       # Haptic feedback if supported
    'audio_feedback': False,           # Audio cues for actions
}

# Theme Variants
THEME_VARIANTS = {
    'default': {
        'name': 'Default Touch',
        'description': 'Standard touch-optimized theme',
        'file': 'themes/touch_theme.qss'
    },
    'high_contrast': {
        'name': 'High Contrast',
        'description': 'Enhanced contrast for bright environments',
        'file': 'themes/touch_theme_high_contrast.qss'
    },
    'dark': {
        'name': 'Dark Mode',
        'description': 'Dark theme for low-light environments',
        'file': 'themes/touch_theme_dark.qss'
    },
    'classic': {
        'name': 'Classic',
        'description': 'Traditional Probe Basic styling',
        'file': 'probe_basic.qss'
    }
}

# Widget Size Classes
SIZE_CLASSES = {
    'compact': {
        'button_height': 36,
        'input_height': 32,
        'icon_size': 16,
        'font_scale': 0.9
    },
    'normal': {
        'button_height': 44,
        'input_height': 40,
        'icon_size': 20,
        'font_scale': 1.0
    },
    'large': {
        'button_height': 52,
        'input_height': 48,
        'icon_size': 24,
        'font_scale': 1.1
    },
    'extra_large': {
        'button_height': 60,
        'input_height': 56,
        'icon_size': 28,
        'font_scale': 1.2
    }
}

# Layout Grid System
GRID = {
    'columns': 12,              # Number of grid columns
    'gutter': 16,              # Gutter width between columns
    'margin': 24,              # Page margins
    'max_width': 1200,         # Maximum content width
}

# Animation and Transition Settings
ANIMATIONS = {
    'enabled': True,
    'duration_fast': 150,      # ms - quick transitions
    'duration_normal': 250,    # ms - standard transitions
    'duration_slow': 400,      # ms - slow, noticeable transitions
    'easing': 'ease-out',      # CSS easing function
}

# Touch Optimization Flags
TOUCH_OPTIMIZATIONS = {
    'enable_touch_scrolling': True,    # Native touch scrolling
    'enable_momentum_scrolling': True, # Momentum/inertial scrolling
    'enable_gesture_navigation': True, # Gesture-based navigation
    'enable_haptic_feedback': False,   # Haptic feedback (if available)
    'enable_voice_commands': False,    # Voice command integration
}

def get_size_class_for_screen(width, height):
    """
    Determine appropriate size class based on screen dimensions
    
    Args:
        width: Screen width in pixels
        height: Screen height in pixels
    
    Returns:
        str: Size class ('compact', 'normal', 'large', 'extra_large')
    """
    if width < BREAKPOINTS['small']:
        return 'compact'
    elif width < BREAKPOINTS['medium']:
        return 'normal'
    elif width < BREAKPOINTS['large']:
        return 'large'
    else:
        return 'extra_large'

def get_responsive_spacing(size_class):
    """
    Get spacing values based on size class
    
    Args:
        size_class: Size class string
    
    Returns:
        dict: Spacing configuration
    """
    spacing_multipliers = {
        'compact': 0.75,
        'normal': 1.0,
        'large': 1.25,
        'extra_large': 1.5
    }
    
    multiplier = spacing_multipliers.get(size_class, 1.0)
    
    return {
        key: int(value * multiplier)
        for key, value in TOUCH_SPACING.items()
    }

def get_responsive_font_sizes(size_class):
    """
    Get font sizes based on size class
    
    Args:
        size_class: Size class string
    
    Returns:
        dict: Font size configuration
    """
    scale = SIZE_CLASSES.get(size_class, SIZE_CLASSES['normal'])['font_scale']
    
    return {
        key: int(value * scale)
        for key, value in FONT_SIZES.items()
    }

# Default configuration that can be imported and modified
DEFAULT_CONFIG = {
    'theme_variant': 'default',
    'size_class': 'normal',
    'accessibility': ACCESSIBILITY.copy(),
    'industrial': INDUSTRIAL.copy(),
    'touch_optimizations': TOUCH_OPTIMIZATIONS.copy(),
    'animations': ANIMATIONS.copy(),
}