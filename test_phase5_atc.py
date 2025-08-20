#!/usr/bin/env python
"""
Test script for Phase 5 ATC Management widgets
Tests that widgets can be imported and basic functionality works
"""

import sys
import os

# Add src directory to path for testing
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def test_phase5_imports():
    """Test that all Phase 5 ATC widgets can be imported"""
    print("Testing Phase 5 ATC Management widget imports...")
    print(f"Using src path: {src_path}")
    
    # Set environment variables for testing
    os.environ['DESIGNER'] = 'True'  # Skip QtQuick initialization in designer mode
    os.environ['INI_FILE_NAME'] = '/dev/null'  # Avoid INI file errors
    
    try:
        from widgets.atc_widget.atc import DynATC
        print("✓ Enhanced DynATC widget imported successfully")
    except Exception as e:
        print(f"✗ Enhanced DynATC widget import failed: {e}")
        return False
        
    try:
        from widgets.atc_widget.atc_recovery import ATCRecovery
        print("✓ ATCRecovery widget imported successfully")
    except Exception as e:
        print(f"✗ ATCRecovery widget import failed: {e}")
        return False
        
    return True

def test_atc_state_management():
    """Test ATC state management functionality"""
    print("\nTesting ATC state management...")
    
    # Set environment for testing
    os.environ['DESIGNER'] = 'True'
    os.environ['INI_FILE_NAME'] = '/dev/null'
    
    try:
        from widgets.atc_widget.atc import DynATC
        
        # Test that new state management methods exist
        atc = DynATC()
        
        # Check that new attributes exist
        assert hasattr(atc, 'atc_state'), "atc_state attribute missing"
        assert hasattr(atc, 'pocket_states'), "pocket_states attribute missing"
        assert hasattr(atc, 'update_atc_state'), "update_atc_state method missing"
        assert hasattr(atc, 'update_pocket_state'), "update_pocket_state method missing"
        assert hasattr(atc, 'update_interlocks'), "update_interlocks method missing"
        assert hasattr(atc, 'update_progress'), "update_progress method missing"
        
        # Test initial state
        assert atc.atc_state == "Ready", f"Expected Ready state, got {atc.atc_state}"
        
        print("✓ ATC state management methods available")
        return True
        
    except Exception as e:
        print(f"✗ ATC state management test failed: {e}")
        return False

def test_ngc_files():
    """Test that NGC macro files exist and are readable"""
    print("\nTesting NGC macro files...")
    
    base_dir = os.path.dirname(__file__)
    expected_files = [
        'configs/atc_sim/macros_sim/atc_change.ngc',
        'configs/atc_sim/macros_sim/toolchange.ngc'
    ]
    
    all_found = True
    for filename in expected_files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            print(f"✓ Found {filename}")
            # Check if file has expected content
            with open(filepath, 'r') as f:
                content = f.read()
                if 'Phase 5' in content:
                    print(f"  ✓ {filename} contains Phase 5 enhancements")
                else:
                    print(f"  ! {filename} may not have Phase 5 enhancements")
        else:
            print(f"✗ Missing {filename}")
            all_found = False
    
    return all_found

def test_recovery_widget():
    """Test ATC recovery widget functionality"""
    print("\nTesting ATC recovery widget...")
    
    os.environ['DESIGNER'] = 'True'
    os.environ['INI_FILE_NAME'] = '/dev/null'
    
    try:
        from widgets.atc_widget.atc_recovery import ATCRecovery
        
        recovery = ATCRecovery()
        
        # Check that recovery methods exist
        assert hasattr(recovery, 'start_recovery'), "start_recovery method missing"
        assert hasattr(recovery, 'resume_mid_change'), "resume_mid_change method missing"
        assert hasattr(recovery, 'home_atc'), "home_atc method missing"
        assert hasattr(recovery, 'manual_jog_to_pocket'), "manual_jog_to_pocket method missing"
        assert hasattr(recovery, 'clear_fault'), "clear_fault method missing"
        
        # Test initial state
        assert not recovery.recovery_active, "Recovery should not be active initially"
        
        print("✓ ATC recovery widget functionality available")
        return True
        
    except Exception as e:
        print(f"✗ ATC recovery widget test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Phase 5 ATC Management Test Suite")
    print("=" * 50)
    
    tests = [
        test_phase5_imports,
        test_atc_state_management,
        test_ngc_files,
        test_recovery_widget
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All Phase 5 ATC Management tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())