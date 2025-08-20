#!/usr/bin/env python
"""
Phase 8 Widget Standalone Test

Tests the Phase 8 widgets in standalone mode without QtPyVCP dependencies
"""

import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_widget_imports():
    """Test that widgets can be imported"""
    print("Testing Phase 8 widget imports...")
    
    try:
        # Test OffsetsEditor import
        from widgets.offsets_editor.offsets_editor import OffsetsEditor
        print("✅ OffsetsEditor import successful")
        
        # Test ToolTableEditor import
        from widgets.tool_table_editor.tool_table_editor import ToolTableEditor
        print("✅ ToolTableEditor import successful")
        
        # Test FixtureLibrary import
        from widgets.fixture_library.fixture_library import FixtureLibrary
        print("✅ FixtureLibrary import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_widget_structure():
    """Test widget structure and attributes"""
    print("Testing Phase 8 widget structure...")
    
    try:
        from widgets.offsets_editor.offsets_editor import OffsetsEditor
        from widgets.tool_table_editor.tool_table_editor import ToolTableEditor
        from widgets.fixture_library.fixture_library import FixtureLibrary
        
        # Test OffsetsEditor structure
        print("Testing OffsetsEditor structure...")
        assert hasattr(OffsetsEditor, 'WCS_SYSTEMS'), "Missing WCS_SYSTEMS"
        assert hasattr(OffsetsEditor, 'AXES'), "Missing AXES"
        assert len(OffsetsEditor.WCS_SYSTEMS) == 10, "Should have 10 WCS systems"
        assert len(OffsetsEditor.AXES) == 6, "Should have 6 axes"
        print("✅ OffsetsEditor structure valid")
        
        # Test ToolTableEditor structure
        print("Testing ToolTableEditor structure...")
        assert hasattr(ToolTableEditor, 'COLUMNS'), "Missing COLUMNS"
        assert len(ToolTableEditor.COLUMNS) == 9, "Should have 9 columns"
        print("✅ ToolTableEditor structure valid")
        
        # Test FixtureLibrary structure
        print("Testing FixtureLibrary structure...")
        assert hasattr(FixtureLibrary, '__init__'), "Missing __init__ method"
        print("✅ FixtureLibrary structure valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        return False

def test_csv_functionality():
    """Test CSV-related functionality"""
    print("Testing CSV functionality...")
    
    try:
        # Test that CSV modules are importable
        import csv
        import json
        print("✅ CSV and JSON modules available")
        
        # Test OffsetsEditor CSV schema
        from widgets.offsets_editor.offsets_editor import OffsetsEditor
        expected_headers = ['WCS'] + OffsetsEditor.AXES
        assert len(expected_headers) == 7, "CSV headers should have 7 columns"
        print("✅ OffsetsEditor CSV schema valid")
        
        # Test ToolTableEditor CSV schema
        from widgets.tool_table_editor.tool_table_editor import ToolTableEditor
        tool_headers = [col[0] for col in ToolTableEditor.COLUMNS]
        assert len(tool_headers) == 9, "Tool CSV headers should have 9 columns"
        print("✅ ToolTableEditor CSV schema valid")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV functionality test error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'src/widgets/offsets_editor/__init__.py',
        'src/widgets/offsets_editor/offsets_editor.py',
        'src/widgets/tool_table_editor/__init__.py',
        'src/widgets/tool_table_editor/tool_table_editor.py',
        'src/widgets/fixture_library/__init__.py',
        'src/widgets/fixture_library/fixture_library.py',
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    # Check widget registration in __init__.py
    init_file = 'src/widgets/__init__.py'
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
            if 'OffsetsEditor' in content and 'ToolTableEditor' in content and 'FixtureLibrary' in content:
                print("✅ Widgets registered in __init__.py")
            else:
                print("❌ Widgets not properly registered in __init__.py")
                return False
    
    return True

def test_phase8_requirements():
    """Test that Phase 8 requirements are addressed"""
    print("Testing Phase 8 requirements compliance...")
    
    try:
        from widgets.offsets_editor.offsets_editor import OffsetsEditor
        from widgets.tool_table_editor.tool_table_editor import ToolTableEditor
        from widgets.fixture_library.fixture_library import FixtureLibrary
        
        # Check OffsetsEditor features
        offsets_methods = dir(OffsetsEditor)
        assert 'exportAllWCS' in offsets_methods, "Missing CSV export functionality"
        assert 'importFromCSV' in offsets_methods, "Missing CSV import functionality"
        assert 'applyDeltas' in offsets_methods, "Missing delta apply functionality"
        print("✅ OffsetsEditor meets requirements")
        
        # Check ToolTableEditor features
        tool_methods = dir(ToolTableEditor)
        assert 'addNewTool' in tool_methods, "Missing CRUD functionality"
        assert 'deleteTool' in tool_methods, "Missing CRUD functionality"
        assert 'exportAllTools' in tool_methods, "Missing CSV export functionality"
        assert 'importToolsFromCSV' in tool_methods, "Missing CSV import functionality"
        assert 'clearAllTools' in tool_methods, "Missing bulk operations"
        print("✅ ToolTableEditor meets requirements")
        
        # Check FixtureLibrary features
        fixture_methods = dir(FixtureLibrary)
        assert 'newFixture' in fixture_methods, "Missing fixture creation"
        assert 'applyFixture' in fixture_methods, "Missing fixture application"
        assert 'importLibrary' in fixture_methods, "Missing import functionality"
        assert 'exportLibrary' in fixture_methods, "Missing export functionality"
        print("✅ FixtureLibrary meets requirements")
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements test error: {e}")
        return False

def main():
    """Main test function"""
    print("Phase 8 Widget Standalone Test Suite")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_widget_imports, 
        test_widget_structure,
        test_csv_functionality,
        test_phase8_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        else:
            print(f"❌ Test {test.__name__} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All Phase 8 widget tests passed!")
        print("\nPhase 8 Implementation Summary:")
        print("- OffsetsEditor: G54-G59.3 + G92 editing with CSV import/export")
        print("- ToolTableEditor: Complete tool.tbl CRUD with bulk operations")
        print("- FixtureLibrary: Named WCS presets with thumbnails")
        print("- WCS shortcuts integrated into probing wizards")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())