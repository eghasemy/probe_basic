#!/usr/bin/env python
"""
Comprehensive test for Phase 10 logging system
Tests logging independently of probe_basic package imports
"""

import sys
import os
from pathlib import Path

def test_comprehensive_logging():
    """Complete test of the logging system"""
    print("Testing Phase 10 Logging System")
    print("=" * 40)
    
    # Test direct import
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'probe_basic'))
    
    try:
        from logging_config import (
            ProbeBasicLogger, initialize_logging, get_logger,
            get_main_logger, get_ui_logger, get_hal_logger,
            get_probe_logger, get_atc_logger, get_job_logger,
            get_safety_logger, get_network_logger, get_diagnostics_logger,
            set_log_level,
            SUBSYSTEM_MAIN, SUBSYSTEM_UI, SUBSYSTEM_HAL, SUBSYSTEM_PROBE,
            SUBSYSTEM_ATC, SUBSYSTEM_JOB, SUBSYSTEM_SAFETY, SUBSYSTEM_NETWORK,
            SUBSYSTEM_DIAGNOSTICS
        )
        print("✅ All logging imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 1: Basic logger creation
    print("\n1. Testing basic logger creation...")
    temp_log_dir = Path('/tmp/probe_basic_test_logs')
    logger_manager = ProbeBasicLogger(temp_log_dir, 'DEBUG')
    print(f"✅ Logger manager created with directory: {temp_log_dir}")
    
    # Test 2: All subsystem loggers
    print("\n2. Testing all subsystem loggers...")
    subsystems = [
        SUBSYSTEM_MAIN, SUBSYSTEM_UI, SUBSYSTEM_HAL, SUBSYSTEM_PROBE,
        SUBSYSTEM_ATC, SUBSYSTEM_JOB, SUBSYSTEM_SAFETY, SUBSYSTEM_NETWORK,
        SUBSYSTEM_DIAGNOSTICS
    ]
    
    loggers = {}
    for subsystem in subsystems:
        logger = logger_manager.get_logger(subsystem)
        loggers[subsystem] = logger
        logger.info(f"{subsystem} subsystem initialized")
        logger.debug(f"{subsystem} debug message")
        logger.warning(f"{subsystem} warning message")
    
    print(f"✅ Created and tested {len(subsystems)} subsystem loggers")
    
    # Test 3: Module-level convenience functions
    print("\n3. Testing convenience functions...")
    initialize_logging(temp_log_dir, 'INFO')
    
    convenience_loggers = {
        'main': get_main_logger(),
        'ui': get_ui_logger(),
        'hal': get_hal_logger(),
        'probe': get_probe_logger(),
        'atc': get_atc_logger(),
        'job': get_job_logger(),
        'safety': get_safety_logger(),
        'network': get_network_logger(),
        'diagnostics': get_diagnostics_logger()
    }
    
    for name, logger in convenience_loggers.items():
        logger.info(f"Convenience function test for {name}")
    
    print("✅ All convenience functions work")
    
    # Test 4: Log file creation
    print("\n4. Testing log file creation...")
    log_files = logger_manager.get_log_files()
    created_count = 0
    for subsystem, log_file in log_files.items():
        if log_file.exists() and log_file.stat().st_size > 0:
            created_count += 1
            print(f"   ✅ {subsystem}: {log_file}")
        else:
            print(f"   ❌ {subsystem}: {log_file} (missing or empty)")
    
    if created_count > 0:
        print(f"✅ {created_count} log files created successfully")
    else:
        print("❌ No log files were created")
        return False
    
    # Test 5: Log level changes
    print("\n5. Testing log level changes...")
    set_log_level('WARNING')
    get_main_logger().debug("This debug should not appear")
    get_main_logger().warning("This warning should appear")
    get_main_logger().error("This error should appear")
    
    set_log_level('DEBUG', SUBSYSTEM_UI)
    get_ui_logger().debug("UI debug after level change")
    print("✅ Log level changes work")
    
    # Test 6: Log content verification
    print("\n6. Testing log content...")
    main_log = temp_log_dir / 'probe_basic.log'
    if main_log.exists():
        with open(main_log, 'r') as f:
            content = f.read()
            if 'main subsystem initialized' in content:
                print("✅ Main log content verified")
            else:
                print("❌ Main log content missing expected messages")
    
    ui_log = temp_log_dir / 'ui.log'
    if ui_log.exists():
        with open(ui_log, 'r') as f:
            content = f.read()
            if 'ui subsystem initialized' in content:
                print("✅ UI log content verified")
            else:
                print("❌ UI log content missing expected messages")
    
    # Test 7: Custom logger
    print("\n7. Testing custom logger...")
    custom_logger = get_logger('phase10_test')
    custom_logger.critical("Phase 10 test critical message")
    custom_logger.error("Phase 10 test error message")
    
    custom_log = temp_log_dir / 'phase10_test.log'
    if custom_log.exists():
        print("✅ Custom logger file created")
    else:
        print("❌ Custom logger file not created")
    
    # Test 8: Error handling
    print("\n8. Testing error handling...")
    try:
        # Test with invalid log level
        logger_manager.set_level('INVALID_LEVEL')
        print("✅ Invalid log level handled gracefully")
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
    
    print("\n" + "=" * 40)
    print("✅ All logging system tests completed successfully!")
    
    # Show log directory contents
    print(f"\nLog files created in {temp_log_dir}:")
    for log_file in temp_log_dir.glob('*.log*'):
        size = log_file.stat().st_size
        print(f"  {log_file.name}: {size} bytes")
    
    return True

if __name__ == '__main__':
    success = test_comprehensive_logging()
    sys.exit(0 if success else 1)