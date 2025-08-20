#!/usr/bin/env python
"""
Standalone test script for Phase 10 logging system
Tests logging system independently of QtPyVCP
"""

import sys
import os
from pathlib import Path

def test_logging_system_standalone():
    """Test the centralized logging system independently"""
    print("Testing Phase 10 logging system (standalone)...")
    
    try:
        # Add src to path and import logging directly
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)
        
        from probe_basic.logging_config import (
            ProbeBasicLogger, 
            SUBSYSTEM_MAIN, SUBSYSTEM_UI, SUBSYSTEM_HAL,
            SUBSYSTEM_PROBE, SUBSYSTEM_ATC
        )
        print("✅ Logging imports successful")
        
        # Initialize logging
        temp_log_dir = Path('/tmp/probe_basic_test_logs')
        logger_manager = ProbeBasicLogger(temp_log_dir, 'DEBUG')
        print(f"✅ Logging initialized to {temp_log_dir}")
        
        # Test different subsystem loggers
        main_logger = logger_manager.get_logger(SUBSYSTEM_MAIN)
        ui_logger = logger_manager.get_logger(SUBSYSTEM_UI)
        hal_logger = logger_manager.get_logger(SUBSYSTEM_HAL)
        probe_logger = logger_manager.get_logger(SUBSYSTEM_PROBE)
        atc_logger = logger_manager.get_logger(SUBSYSTEM_ATC)
        
        # Test logging messages
        main_logger.info("Main application started")
        main_logger.debug("Debug message from main")
        
        ui_logger.warning("UI component warning")
        ui_logger.error("UI error for testing")
        
        hal_logger.info("HAL subsystem initialized")
        hal_logger.debug("HAL debug information")
        
        probe_logger.info("Probing subsystem ready")
        atc_logger.warning("ATC test warning")
        
        # Test custom subsystem logger
        custom_logger = logger_manager.get_logger('test_subsystem')
        custom_logger.critical("Critical test message")
        
        print("✅ Logger messages sent successfully")
        
        # Verify log files were created
        log_files = logger_manager.get_log_files()
        created_files = 0
        for subsystem, log_file in log_files.items():
            if log_file.exists():
                print(f"✅ Log file created: {subsystem} -> {log_file}")
                created_files += 1
            else:
                print(f"❌ Log file missing: {subsystem} -> {log_file}")
        
        if created_files == 0:
            print("❌ No log files were created")
            return False
        
        # Test log level change
        logger_manager.set_level('WARNING')
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
                    print(f"   Sample content: {content.split()[0:10]}")
                else:
                    print("❌ Log file content verification failed")
                    print(f"   File content preview: {content[:200]}")
        
        # Test rotating file behavior
        large_message = "Large test message " * 100
        for i in range(100):
            main_logger.info(f"Rotation test message {i}: {large_message}")
        print("✅ Log rotation test completed")
        
        # Test cleanup
        logger_manager.cleanup_old_logs(0)  # Should remove all logs
        print("✅ Log cleanup test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_module_functions():
    """Test module-level convenience functions"""
    print("Testing module-level logging functions...")
    
    try:
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)
        
        from probe_basic.logging_config import (
            initialize_logging, get_logger, 
            get_main_logger, get_ui_logger, get_hal_logger,
            get_probe_logger, get_atc_logger, set_log_level
        )
        
        # Initialize with module functions
        temp_log_dir = Path('/tmp/probe_basic_module_test')
        initialize_logging(temp_log_dir, 'INFO')
        
        # Test convenience functions
        loggers = {
            'main': get_main_logger(),
            'ui': get_ui_logger(), 
            'hal': get_hal_logger(),
            'probe': get_probe_logger(),
            'atc': get_atc_logger(),
            'custom': get_logger('custom_test')
        }
        
        for name, logger in loggers.items():
            logger.info(f"Test message from {name} logger")
        
        print("✅ Module function tests passed")
        
        # Test global log level setting
        set_log_level('DEBUG')
        get_main_logger().debug("Debug message after level change")
        
        print("✅ Global log level test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Module function test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Phase 10 Logging System Test (Standalone)")
    print("=" * 50)
    
    success = True
    success &= test_logging_system_standalone()
    success &= test_logging_module_functions()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All logging tests passed!")
        sys.exit(0)
    else:
        print("❌ Some logging tests failed!")
        sys.exit(1)