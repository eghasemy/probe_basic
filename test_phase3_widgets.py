#!/usr/bin/env python
"""
Simple test script for Phase 3 widgets
Tests that widgets can be imported and instantiated
"""

import sys
import os

# Add src directory to path for testing
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def test_imports():
    """Test that all Phase 3 widgets can be imported"""
    print("Testing Phase 3 widget imports...")
    print(f"Using src path: {src_path}")
    
    try:
        from widgets.io_panel.io_panel import IOPanel
        print("✓ IOPanel imported successfully")
    except Exception as e:
        print(f"✗ IOPanel import failed: {e}")
        return False
        
    try:
        from widgets.jog_panel.jog_panel import JogPanel, MPGWheel
        print("✓ JogPanel and MPGWheel imported successfully")
    except Exception as e:
        print(f"✗ JogPanel import failed: {e}")
        return False
        
    try:
        from widgets.diagnostics_panel.diagnostics_panel import DiagnosticsPanel
        print("✓ DiagnosticsPanel imported successfully")
    except Exception as e:
        print(f"✗ DiagnosticsPanel import failed: {e}")
        return False
        
    return True

def test_widget_registration():
    """Test that widgets are properly registered"""
    print("\nTesting widget registration...")
    
    try:
        from widgets import IOPanelPlugin, JogPanelPlugin, DiagnosticsPanelPlugin
        print("✓ Widget plugins imported successfully")
        
        # Test plugin classes
        io_plugin = IOPanelPlugin()
        jog_plugin = JogPanelPlugin()
        diag_plugin = DiagnosticsPanelPlugin()
        
        print("✓ Widget plugins instantiated successfully")
        return True
        
    except Exception as e:
        print(f"✗ Widget registration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Phase 3 Widget Test Suite")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        
    # Test registration
    if not test_widget_registration():
        all_passed = False
        
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())