#!/usr/bin/env python
"""
Phase 10 UI Smoke Tests with pytest-qt
Tests basic UI functionality without full LinuxCNC dependencies
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import pytest
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtTest import QTest
    PYTEST_QT_AVAILABLE = True
    
    @pytest.fixture
    def help_manager():
        """Fixture providing a help manager instance"""
        help_data_dir = Path(__file__).parent / 'src' / 'probe_basic' / 'help_data'
        return HelpManager(help_data_dir)
        
except ImportError:
    PYTEST_QT_AVAILABLE = False
    
    # Define dummy decorator when pytest not available
    def pytest_fixture(func):
        return func
    
    def help_manager():
        help_data_dir = Path(__file__).parent / 'src' / 'probe_basic' / 'help_data'
        return HelpManager(help_data_dir)

# Import our help system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'probe_basic'))
from help_system import HelpManager, HelpButton, HelpOverlay

if PYTEST_QT_AVAILABLE:
    class TestHelpSystem:
        """Test suite for the help system UI components"""
        
        def test_help_button_creation(self, qtbot, help_manager):
            """Test that help buttons can be created"""
            widget = QWidget()
            qtbot.addWidget(widget)
            
            # Create help button
            help_button = HelpButton('test_widget', widget)
            
            # Verify button properties
            assert help_button.text() == "?"
            assert help_button.widget_name == 'test_widget'
            assert help_button.toolTip() == "Click for help with test_widget"
        
        def test_help_button_signal(self, qtbot, help_manager):
            """Test that help button emits signal when clicked"""
            widget = QWidget()
            qtbot.addWidget(widget)
            
            help_button = HelpButton('test_widget', widget)
            
            # Track signal emission
            signal_received = []
            help_button.help_requested.connect(lambda name: signal_received.append(name))
            
            # Simulate click
            qtbot.mouseClick(help_button, Qt.LeftButton)
            
            # Verify signal was emitted
            assert len(signal_received) == 1
            assert signal_received[0] == 'test_widget'
        
        def test_help_overlay_creation(self, qtbot, help_manager):
            """Test that help overlay can be created"""
            help_data = {
                'title': 'Test Widget',
                'description': 'This is a test widget',
                'usage': 'Use this for testing',
                'tips': ['Tip 1', 'Tip 2'],
                'safety': ['Safety note 1']
            }
            
            overlay = HelpOverlay('test_widget', help_data)
            qtbot.addWidget(overlay)
            
            # Verify overlay properties
            assert overlay.windowTitle() == "Help: test_widget"
            assert overlay.isModal()

    class TestBasicUI:
        """Basic UI smoke tests"""
        
        def test_basic_widget_creation(self, qtbot):
            """Test basic widget creation and display"""
            widget = QWidget()
            widget.setWindowTitle("Smoke Test Widget")
            
            layout = QVBoxLayout(widget)
            
            label = QLabel("This is a smoke test")
            layout.addWidget(label)
            
            button = QPushButton("Test Button")
            layout.addWidget(button)
            
            qtbot.addWidget(widget)
            widget.show()
            
            # Verify widget is shown
            assert widget.isVisible()
            assert widget.windowTitle() == "Smoke Test Widget"
        
        def test_button_click(self, qtbot):
            """Test button click interaction"""
            widget = QWidget()
            button = QPushButton("Click Me", widget)
            
            qtbot.addWidget(widget)
            
            # Track clicks
            clicks = []
            button.clicked.connect(lambda: clicks.append(1))
            
            # Simulate click
            qtbot.mouseClick(button, Qt.LeftButton)
            
            assert len(clicks) == 1
        
        def test_keyboard_interaction(self, qtbot):
            """Test keyboard interaction"""
            widget = QWidget()
            button = QPushButton("Press Space", widget)
            
            qtbot.addWidget(widget)
            button.setFocus()
            
            # Track activation
            activations = []
            button.clicked.connect(lambda: activations.append(1))
            
            # Simulate space key press
            qtbot.keyPress(button, Qt.Key_Space)
            
            assert len(activations) == 1

    class TestUIResponsiveness:
        """Test UI responsiveness and performance"""
        
        def test_ui_responsiveness(self, qtbot):
            """Test that UI remains responsive during operations"""
            widget = QWidget()
            button = QPushButton("Process", widget)
            
            qtbot.addWidget(widget)
            
            # Simulate some processing
            processed = []
            
            def process():
                # Simulate work
                import time
                time.sleep(0.01)  # Short delay
                processed.append(1)
            
            button.clicked.connect(process)
            
            # Click multiple times rapidly
            for _ in range(5):
                qtbot.mouseClick(button, Qt.LeftButton)
                qtbot.wait(10)  # Small wait between clicks
            
            # Wait for processing to complete
            qtbot.wait(100)
            
            assert len(processed) == 5

else:
    # Dummy classes when pytest not available
    class TestHelpSystem:
        pass
    class TestBasicUI:
        pass
    class TestUIResponsiveness:
        pass

def test_logging_system_basic():
    """Test logging system without Qt dependencies"""
    from logging_config import ProbeBasicLogger
    
    # Test basic logging functionality
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        logger_manager = ProbeBasicLogger(Path(temp_dir), 'DEBUG')
        
        # Test subsystem loggers
        main_logger = logger_manager.get_logger('main')
        ui_logger = logger_manager.get_logger('ui')
        
        main_logger.info("Test message from main")
        ui_logger.warning("Test warning from UI")
        
        # Verify log files exist
        log_files = logger_manager.get_log_files()
        assert len(log_files) >= 2
        
        # Check main log content
        main_log = Path(temp_dir) / 'probe_basic.log'
        assert main_log.exists()
        
        with open(main_log, 'r') as f:
            content = f.read()
            assert "Test message from main" in content
            assert "Test warning from UI" in content

# Standalone test runner for when pytest is not available
def run_manual_tests():
    """Run tests manually when pytest is not available"""
    print("Running manual UI smoke tests...")
    
    if not PYTEST_QT_AVAILABLE:
        print("❌ PyQt5 or pytest-qt not available")
        return False
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    success = True
    
    try:
        # Test 1: Basic widget
        print("Test 1: Basic widget creation...")
        widget = QWidget()
        widget.setWindowTitle("Manual Test")
        widget.show()
        
        # Process events
        app.processEvents()
        
        # Auto-close after short time
        timer = QTimer()
        timer.timeout.connect(widget.close)
        timer.start(1000)  # 1 second
        
        # Process until closed
        while widget.isVisible():
            app.processEvents()
        
        print("✅ Basic widget test passed")
        
        # Test 2: Help system
        print("Test 2: Help system...")
        help_manager = HelpManager()
        help_data = help_manager.get_help_data('dashboard')
        
        if 'title' in help_data:
            print("✅ Help system test passed")
        else:
            print("❌ Help system test failed")
            success = False
        
    except Exception as e:
        print(f"❌ Manual test error: {e}")
        success = False
    
    return success

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        # Run manual tests
        success = run_manual_tests()
        sys.exit(0 if success else 1)
    else:
        # Run with pytest if available
        if PYTEST_QT_AVAILABLE:
            print("Running pytest-qt smoke tests...")
            pytest.main([__file__, '-v'])
        else:
            print("pytest or PyQt5 not available, running manual tests...")
            success = run_manual_tests()
            sys.exit(0 if success else 1)