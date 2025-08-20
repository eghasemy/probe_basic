#!/usr/bin/env python
"""
Phase 8 Widget Testing Script

Tests the new Phase 8 widgets: OffsetsEditor, ToolTableEditor, and FixtureLibrary
"""

import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from qtpy.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
    from qtpy.QtCore import Qt
    
    # Import Phase 8 widgets
    from widgets.offsets_editor.offsets_editor import OffsetsEditor
    from widgets.tool_table_editor.tool_table_editor import ToolTableEditor
    from widgets.fixture_library.fixture_library import FixtureLibrary
    
    print("✅ Successfully imported all Phase 8 widgets")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class Phase8TestWindow(QMainWindow):
    """Test window for Phase 8 widgets"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 8 Widget Test - Offsets, Tool Table, Fixture Library")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget with tabs
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        tab_widget = QTabWidget()
        
        # Offsets Editor Tab
        try:
            self.offsets_editor = OffsetsEditor()
            tab_widget.addTab(self.offsets_editor, "Offsets Editor")
            print("✅ OffsetsEditor widget created successfully")
        except Exception as e:
            print(f"❌ Error creating OffsetsEditor: {e}")
        
        # Tool Table Editor Tab
        try:
            self.tool_table_editor = ToolTableEditor()
            tab_widget.addTab(self.tool_table_editor, "Tool Table Editor")
            print("✅ ToolTableEditor widget created successfully")
        except Exception as e:
            print(f"❌ Error creating ToolTableEditor: {e}")
        
        # Fixture Library Tab
        try:
            self.fixture_library = FixtureLibrary()
            tab_widget.addTab(self.fixture_library, "Fixture Library")
            print("✅ FixtureLibrary widget created successfully")
        except Exception as e:
            print(f"❌ Error creating FixtureLibrary: {e}")
        
        layout.addWidget(tab_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

def test_widget_creation():
    """Test that all widgets can be created"""
    print("Testing Phase 8 widget creation...")
    
    # Test OffsetsEditor
    try:
        offsets_editor = OffsetsEditor()
        print("✅ OffsetsEditor creation test passed")
        
        # Test basic functionality
        assert hasattr(offsets_editor, 'WCS_SYSTEMS'), "Missing WCS_SYSTEMS attribute"
        assert hasattr(offsets_editor, 'offsetChanged'), "Missing offsetChanged signal"
        assert len(offsets_editor.WCS_SYSTEMS) == 10, "Should have 10 WCS systems (G54-G59.3 + G92)"
        
    except Exception as e:
        print(f"❌ OffsetsEditor test failed: {e}")
        return False
    
    # Test ToolTableEditor
    try:
        tool_editor = ToolTableEditor()
        print("✅ ToolTableEditor creation test passed")
        
        # Test basic functionality
        assert hasattr(tool_editor, 'COLUMNS'), "Missing COLUMNS attribute"
        assert hasattr(tool_editor, 'toolChanged'), "Missing toolChanged signal"
        assert len(tool_editor.COLUMNS) == 9, "Should have 9 tool table columns"
        
    except Exception as e:
        print(f"❌ ToolTableEditor test failed: {e}")
        return False
    
    # Test FixtureLibrary
    try:
        fixture_lib = FixtureLibrary()
        print("✅ FixtureLibrary creation test passed")
        
        # Test basic functionality
        assert hasattr(fixture_lib, 'fixtureApplied'), "Missing fixtureApplied signal"
        assert hasattr(fixture_lib, 'fixtures'), "Missing fixtures attribute"
        
    except Exception as e:
        print(f"❌ FixtureLibrary test failed: {e}")
        return False
    
    return True

def test_widget_integration():
    """Test widget registration and integration"""
    print("Testing widget integration...")
    
    try:
        # Test widget imports from __init__.py
        from widgets.offsets_editor import OffsetsEditor as OE_Import
        from widgets.tool_table_editor import ToolTableEditor as TTE_Import
        from widgets.fixture_library import FixtureLibrary as FL_Import
        
        print("✅ Widget package imports successful")
        
        # Test that widgets are the same classes
        assert OE_Import == OffsetsEditor, "OffsetsEditor import mismatch"
        assert TTE_Import == ToolTableEditor, "ToolTableEditor import mismatch"
        assert FL_Import == FixtureLibrary, "FixtureLibrary import mismatch"
        
        print("✅ Widget integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Widget integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Phase 8 Widget Test Suite")
    print("=" * 40)
    
    # Run creation tests first
    if not test_widget_creation():
        print("❌ Widget creation tests failed")
        return 1
    
    # Run integration tests
    if not test_widget_integration():
        print("❌ Widget integration tests failed")
        return 1
    
    # Create and show test GUI if requested
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        print("\nStarting GUI test...")
        app = QApplication(sys.argv)
        
        window = Phase8TestWindow()
        window.show()
        
        print("✅ All Phase 8 widgets loaded successfully!")
        print("You can now test the widgets interactively.")
        
        return app.exec_()
    else:
        print("\nAll tests passed! ✅")
        print("Run with --gui flag to test the UI interactively.")
        return 0

if __name__ == "__main__":
    sys.exit(main())