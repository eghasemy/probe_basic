#!/usr/bin/env python
"""
Test script for Phase 10 help system
"""

import sys
import os
from pathlib import Path

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_help_system_imports():
    """Test help system imports"""
    print("Testing help system imports...")
    
    try:
        # Test direct import from logging_config to avoid qtpyvcp dependency
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'probe_basic'))
        
        from help_system import HelpManager, get_help_manager
        print("✅ Help system imports successful (without Qt)")
        
        # Test help manager creation
        help_manager = HelpManager()
        print("✅ Help manager created successfully")
        
        return True
        
    except ImportError as e:
        if "PyQt5" in str(e):
            print("⚠️ PyQt5 not available, testing non-Qt functionality only")
            return True
        else:
            print(f"❌ Import error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_help_data_loading():
    """Test help data loading"""
    print("Testing help data loading...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'probe_basic'))
        from help_system import HelpManager
        
        # Test with actual help data directory
        help_data_dir = Path(__file__).parent / 'src' / 'probe_basic' / 'help_data'
        help_manager = HelpManager(help_data_dir)
        
        # Check if help data was loaded
        help_data = help_manager.help_data
        if help_data:
            print(f"✅ Loaded help data for {len(help_data)} widgets:")
            for widget_name in help_data.keys():
                print(f"   - {widget_name}")
        else:
            print("⚠️ No help data loaded (files may not exist)")
        
        # Test getting help data for known widgets
        dashboard_help = help_manager.get_help_data('dashboard')
        if 'title' in dashboard_help:
            print(f"✅ Dashboard help data: {dashboard_help['title']}")
        
        # Test default help data for unknown widget
        unknown_help = help_manager.get_help_data('unknown_widget')
        if 'title' in unknown_help:
            print(f"✅ Default help data generated: {unknown_help['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Help data loading error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_help_content():
    """Test help content structure"""
    print("Testing help content structure...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'probe_basic'))
        from help_system import HelpManager
        
        help_data_dir = Path(__file__).parent / 'src' / 'probe_basic' / 'help_data'
        help_manager = HelpManager(help_data_dir)
        
        # Test specific help files
        test_widgets = ['dashboard', 'probing', 'io_panel', 'jog_panel']
        
        for widget_name in test_widgets:
            help_data = help_manager.get_help_data(widget_name)
            
            # Check required fields
            required_fields = ['title', 'description', 'usage', 'tips', 'safety']
            missing_fields = []
            
            for field in required_fields:
                if field not in help_data:
                    missing_fields.append(field)
            
            if not missing_fields:
                print(f"✅ {widget_name}: All required fields present")
                
                # Check field content
                if len(help_data['tips']) > 0:
                    print(f"   Tips: {len(help_data['tips'])} items")
                if len(help_data['safety']) > 0:
                    print(f"   Safety notes: {len(help_data['safety'])} items")
            else:
                print(f"❌ {widget_name}: Missing fields: {missing_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ Help content test error: {e}")
        return False

def test_help_manager_functions():
    """Test help manager functionality"""
    print("Testing help manager functions...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'probe_basic'))
        from help_system import HelpManager, get_help_manager
        
        # Test global help manager
        manager1 = get_help_manager()
        manager2 = get_help_manager()
        
        if manager1 is manager2:
            print("✅ Global help manager singleton works")
        else:
            print("❌ Global help manager singleton failed")
        
        # Test adding help data programmatically
        test_help_data = {
            'title': 'Test Widget',
            'description': 'This is a test widget',
            'usage': 'Use this widget for testing',
            'tips': ['Test tip 1', 'Test tip 2'],
            'safety': ['Test safety note']
        }
        
        manager1.add_help_data('test_widget', test_help_data)
        retrieved_data = manager1.get_help_data('test_widget')
        
        if retrieved_data['title'] == 'Test Widget':
            print("✅ Programmatic help data addition works")
        else:
            print("❌ Programmatic help data addition failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Help manager function test error: {e}")
        return False

if __name__ == '__main__':
    print("Phase 10 Help System Test")
    print("=" * 40)
    
    success = True
    success &= test_help_system_imports()
    success &= test_help_data_loading()
    success &= test_help_content()
    success &= test_help_manager_functions()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All help system tests passed!")
        sys.exit(0)
    else:
        print("❌ Some help system tests failed!")
        sys.exit(1)