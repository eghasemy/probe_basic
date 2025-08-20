#!/usr/bin/env python
"""
Test script for Phase 10 logging system
"""

import sys
import os
from pathlib import Path

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logging_system():
    """Test the centralized logging system"""
    print("Testing Phase 10 logging system...")
    
    try:
        # Import logging components
        from probe_basic.logging_config import (
            initialize_logging, get_logger, get_main_logger, 
            get_ui_logger, get_hal_logger, set_log_level
        )
        print("✅ Logging imports successful")
        
        # Initialize logging
        temp_log_dir = Path('/tmp/probe_basic_test_logs')
        logger_manager = initialize_logging(temp_log_dir, 'DEBUG')
        print(f"✅ Logging initialized to {temp_log_dir}")
        
        # Test different subsystem loggers
        main_logger = get_main_logger()
        ui_logger = get_ui_logger()
        hal_logger = get_hal_logger()
        
        # Test logging messages
        main_logger.info("Main application started")
        main_logger.debug("Debug message from main")
        
        ui_logger.warning("UI component warning")
        ui_logger.error("UI error for testing")
        
        hal_logger.info("HAL subsystem initialized")
        hal_logger.debug("HAL debug information")
        
        # Test custom subsystem logger
        custom_logger = get_logger('test_subsystem')
        custom_logger.critical("Critical test message")
        
        print("✅ Logger messages sent successfully")
        
        # Verify log files were created
        log_files = logger_manager.get_log_files()
        for subsystem, log_file in log_files.items():
            if log_file.exists():
                print(f"✅ Log file created: {subsystem} -> {log_file}")
            else:
                print(f"❌ Log file missing: {subsystem} -> {log_file}")
        
        # Test log level change
        set_log_level('WARNING')
        main_logger.debug("This debug message should be filtered out")
        main_logger.warning("This warning should appear")
        print("✅ Log level change tested")
        
        # Check log file contents
        main_log_file = temp_log_dir / 'probe_basic.log'
        if main_log_file.exists():
            with open(main_log_file, 'r') as f:
                content = f.read()
                if 'Main application started' in content:
                    print("✅ Log file content verification passed")
                else:
                    print("❌ Log file content verification failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_integration():
    """Test logging integration with probe_basic module"""
    print("Testing logging integration...")
    
    try:
        # Test that the main module initializes logging
        from probe_basic import logging_config
        from probe_basic.logging_config import get_main_logger
        
        logger = get_main_logger()
        logger.info("Integration test message")
        print("✅ Logging integration test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

if __name__ == '__main__':
    print("Phase 10 Logging System Test")
    print("=" * 40)
    
    success = True
    success &= test_logging_system()
    success &= test_logging_integration()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All logging tests passed!")
        sys.exit(0)
    else:
        print("❌ Some logging tests failed!")
        sys.exit(1)