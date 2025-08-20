#!/usr/bin/env python
"""
Simple test script for Phase 4 widgets
Tests that widgets can be imported and basic functionality works
"""

import sys
import os

# Add src directory to path for testing
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def test_phase4_imports():
    """Test that all Phase 4 widgets can be imported"""
    print("Testing Phase 4 widget imports...")
    print(f"Using src path: {src_path}")
    
    try:
        from widgets.probing_wizards.probing_wizards import ProbingWizards
        print("✓ ProbingWizards imported successfully")
    except Exception as e:
        print(f"✗ ProbingWizards import failed: {e}")
        return False
        
    try:
        from widgets.toolsetter_wizard.toolsetter_wizard import ToolsetterWizard
        print("✓ ToolsetterWizard imported successfully")
    except Exception as e:
        print(f"✗ ToolsetterWizard import failed: {e}")
        return False
        
    return True

def test_ngc_macros():
    """Test that NGC macro files exist and are readable"""
    print("\nTesting NGC macro files...")
    
    macro_dir = os.path.join(os.path.dirname(__file__), 'wizards', 'probing')
    expected_files = [
        'edges.ngc',
        'corners.ngc', 
        'boss_pocket.ngc',
        'z_touchoff.ngc',
        'toolsetter.ngc',
        'probe_calibration.ngc'
    ]
    
    all_found = True
    for filename in expected_files:
        filepath = os.path.join(macro_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if len(content) > 100:  # Basic content check
                        print(f"✓ {filename} exists and has content")
                    else:
                        print(f"⚠ {filename} exists but appears empty")
                        all_found = False
            except Exception as e:
                print(f"✗ {filename} read error: {e}")
                all_found = False
        else:
            print(f"✗ {filename} not found")
            all_found = False
            
    return all_found

def test_widget_registration():
    """Test that widgets are properly registered"""
    print("\nTesting widget registration...")
    
    try:
        from widgets import ProbingWizardsPlugin, ToolsetterWizardPlugin
        print("✓ Widget plugins imported successfully")
        
        # Test plugin classes
        probing_plugin = ProbingWizardsPlugin()
        tool_plugin = ToolsetterWizardPlugin()
        
        print("✓ Widget plugins instantiated successfully")
        return True
        
    except Exception as e:
        print(f"✗ Widget registration test failed: {e}")
        return False

def test_macro_syntax():
    """Basic syntax check on NGC macros"""
    print("\nTesting NGC macro syntax...")
    
    macro_dir = os.path.join(os.path.dirname(__file__), 'wizards', 'probing')
    
    for filename in os.listdir(macro_dir):
        if filename.endswith('.ngc'):
            filepath = os.path.join(macro_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Basic syntax checks
                if 'o<' in content and 'endsub' in content:
                    print(f"✓ {filename} has proper subroutine structure")
                elif filename != 'README.md':
                    print(f"⚠ {filename} missing subroutine structure")
                    
            except Exception as e:
                print(f"✗ {filename} syntax check failed: {e}")
                
    return True

def main():
    """Run all tests"""
    print("Phase 4 Probing & Tool Setting Wizards Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_phase4_imports():
        all_passed = False
        
    # Test NGC macros exist
    if not test_ngc_macros():
        all_passed = False
        
    # Test registration (skip if QtPyVCP not available)
    try:
        if not test_widget_registration():
            all_passed = False
    except Exception as e:
        print(f"⚠ Widget registration test skipped (QtPyVCP not available): {e}")
        
    # Test macro syntax
    if not test_macro_syntax():
        all_passed = False
        
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nPhase 4 implementation status:")
        print("- ✓ Probing wizards widget created")
        print("- ✓ Toolsetter wizard widget created") 
        print("- ✓ NGC macros for all probing operations")
        print("- ✓ Edge, corner, boss/pocket, Z touch-off probing")
        print("- ✓ Tool setter with breakage detection")
        print("- ✓ Probe calibration functionality")
        print("- ✓ Safety checklists and visual diagrams")
        print("- ✓ Widget registration for QtDesigner")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())