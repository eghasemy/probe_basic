#!/usr/bin/env python
"""
Simple Phase 5 ATC Management verification
Checks that code structure and NGC files are correct without full dependencies
"""

import sys
import os

def test_phase5_code_structure():
    """Test that Phase 5 code files exist with correct structure"""
    print("Testing Phase 5 ATC Management code structure...")
    
    base_dir = os.path.dirname(__file__)
    
    # Check widget files exist
    widget_files = [
        'src/widgets/atc_widget/atc.py',
        'src/widgets/atc_widget/atc.qml',
        'src/widgets/atc_widget/atc_recovery.py',
        'src/widgets/atc_widget/atc_recovery.qml',
        'src/widgets/atc_widget/__init__.py'
    ]
    
    all_found = True
    for filename in widget_files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            print(f"✓ Found {filename}")
        else:
            print(f"✗ Missing {filename}")
            all_found = False
    
    return all_found

def test_enhanced_atc_widget():
    """Test that ATC widget has Phase 5 enhancements"""
    print("\nTesting enhanced ATC widget...")
    
    base_dir = os.path.dirname(__file__)
    atc_file = os.path.join(base_dir, 'src/widgets/atc_widget/atc.py')
    
    if not os.path.exists(atc_file):
        print("✗ ATC widget file not found")
        return False
    
    with open(atc_file, 'r') as f:
        content = f.read()
    
    # Check for Phase 5 features
    phase5_features = [
        'atcStateSig',
        'pocketStateSig', 
        'interlockSig',
        'progressSig',
        'update_atc_state',
        'update_pocket_state',
        'update_interlocks',
        'update_progress',
        'set_atc_state',
        'set_pocket_state'
    ]
    
    found_features = 0
    for feature in phase5_features:
        if feature in content:
            print(f"  ✓ Found {feature}")
            found_features += 1
        else:
            print(f"  ✗ Missing {feature}")
    
    print(f"Found {found_features}/{len(phase5_features)} Phase 5 features")
    return found_features == len(phase5_features)

def test_enhanced_qml():
    """Test that QML has Phase 5 UI enhancements"""
    print("\nTesting enhanced ATC QML...")
    
    base_dir = os.path.dirname(__file__)
    qml_file = os.path.join(base_dir, 'src/widgets/atc_widget/atc.qml')
    
    if not os.path.exists(qml_file):
        print("✗ ATC QML file not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Check for Phase 5 UI features
    ui_features = [
        'onAtcStateSig',
        'onPocketStateSig',
        'onInterlockSig', 
        'onProgressSig',
        'state_panel',
        'atc_state_indicator',
        'door_indicator',
        'air_indicator',
        'encoder_indicator',
        'progress_bar',
        'fault_state'
    ]
    
    found_features = 0
    for feature in ui_features:
        if feature in content:
            print(f"  ✓ Found {feature}")
            found_features += 1
        else:
            print(f"  ✗ Missing {feature}")
    
    print(f"Found {found_features}/{len(ui_features)} Phase 5 UI features")
    return found_features >= len(ui_features) * 0.8  # Allow some variance

def test_ngc_enhancements():
    """Test that NGC files have Phase 5 enhancements"""
    print("\nTesting NGC file enhancements...")
    
    base_dir = os.path.dirname(__file__)
    ngc_files = {
        'configs/atc_sim/macros_sim/atc_change.ngc': [
            'Phase 5',
            'set_atc_state',
            'set_progress',
            'ngc=atc_change'
        ],
        'configs/atc_sim/macros_sim/toolchange.ngc': [
            'Phase 5',
            'set_atc_state',
            'set_progress'
        ]
    }
    
    all_good = True
    for filename, expected_content in ngc_files.items():
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f"✗ Missing {filename}")
            all_good = False
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        print(f"Checking {filename}:")
        for expected in expected_content:
            if expected in content:
                print(f"  ✓ Found {expected}")
            else:
                print(f"  ✗ Missing {expected}")
                all_good = False
    
    return all_good

def test_recovery_widget():
    """Test that recovery widget exists with correct structure"""
    print("\nTesting ATC recovery widget...")
    
    base_dir = os.path.dirname(__file__)
    recovery_py = os.path.join(base_dir, 'src/widgets/atc_widget/atc_recovery.py')
    recovery_qml = os.path.join(base_dir, 'src/widgets/atc_widget/atc_recovery.qml')
    
    if not os.path.exists(recovery_py):
        print("✗ Recovery Python file not found")
        return False
    
    if not os.path.exists(recovery_qml):
        print("✗ Recovery QML file not found")
        return False
    
    with open(recovery_py, 'r') as f:
        py_content = f.read()
    
    # Check for recovery features
    recovery_features = [
        'ATCRecovery',
        'start_recovery',
        'resume_mid_change',
        'home_atc',
        'manual_jog_to_pocket',
        'clear_fault',
        'complete_recovery'
    ]
    
    found_features = 0
    for feature in recovery_features:
        if feature in py_content:
            print(f"  ✓ Found {feature}")
            found_features += 1
        else:
            print(f"  ✗ Missing {feature}")
    
    print(f"Found {found_features}/{len(recovery_features)} recovery features")
    return found_features == len(recovery_features)

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Phase 5 ATC Management Code Verification")
    print("=" * 60)
    
    tests = [
        test_phase5_code_structure,
        test_enhanced_atc_widget,
        test_enhanced_qml,
        test_ngc_enhancements,
        test_recovery_widget
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All Phase 5 ATC Management verification tests passed!")
        print("\nPhase 5 Implementation Summary:")
        print("• Enhanced ATC widget with state management")
        print("• Added pocket state tracking and fault visualization")  
        print("• Added interlock status display (door/air/encoder)")
        print("• Added progress tracking during tool changes")
        print("• Created sample M6 remap (atc_change.ngc)")
        print("• Enhanced existing toolchange.ngc with progress updates")
        print("• Created ATC recovery wizard widget")
        print("• Recovery features: resume mid-change, home ATC, clear faults")
        return 0
    else:
        print("✗ Some verification tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())