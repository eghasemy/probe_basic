#!/usr/bin/env python
"""
Probe Basic Logging Configuration
Phase 10 - Centralized logging system with rotating files per subsystem
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict

# Subsystem identifiers
SUBSYSTEM_MAIN = 'main'
SUBSYSTEM_UI = 'ui'
SUBSYSTEM_HAL = 'hal'
SUBSYSTEM_PROBE = 'probe'
SUBSYSTEM_ATC = 'atc'
SUBSYSTEM_JOB = 'job'
SUBSYSTEM_SAFETY = 'safety'
SUBSYSTEM_NETWORK = 'network'
SUBSYSTEM_DIAGNOSTICS = 'diagnostics'

# Default log directory
DEFAULT_LOG_DIR = Path.home() / '.probe_basic' / 'logs'

class ProbeBasicLogger:
    """Centralized logging manager for Probe Basic subsystems"""
    
    def __init__(self, log_dir: Optional[Path] = None, log_level: str = 'INFO'):
        """
        Initialize the logging system
        
        Args:
            log_dir: Directory for log files (defaults to ~/.probe_basic/logs)
            log_level: Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = log_dir or DEFAULT_LOG_DIR
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.loggers: Dict[str, logging.Logger] = {}
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger with console handler"""
        root_logger = logging.getLogger('probe_basic')
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Format: [TIMESTAMP] [LEVEL] [SUBSYSTEM] MESSAGE
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)8s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Main log file handler (all messages)
        main_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'probe_basic.log',
            maxBytes=10 * 1024 * 1024,  # 10MB per file
            backupCount=5
        )
        main_file_handler.setLevel(logging.DEBUG)
        main_file_handler.setFormatter(formatter)
        root_logger.addHandler(main_file_handler)
    
    def get_logger(self, subsystem: str) -> logging.Logger:
        """
        Get or create a logger for the specified subsystem
        
        Args:
            subsystem: Subsystem identifier (e.g., 'ui', 'hal', 'probe')
            
        Returns:
            Logger instance for the subsystem
        """
        if subsystem in self.loggers:
            return self.loggers[subsystem]
        
        # Create logger with subsystem-specific name
        logger_name = f'probe_basic.{subsystem}'
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        
        # Subsystem-specific file handler
        log_file = self.log_dir / f'{subsystem}.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB per subsystem file
            backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Subsystem format includes function name for debugging
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)8s] [%(funcName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Store reference
        self.loggers[subsystem] = logger
        
        return logger
    
    def set_level(self, level: str, subsystem: Optional[str] = None):
        """
        Set logging level for all loggers or specific subsystem
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            subsystem: Specific subsystem to update (None for all)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        if subsystem:
            if subsystem in self.loggers:
                self.loggers[subsystem].setLevel(log_level)
        else:
            # Update all loggers
            logging.getLogger('probe_basic').setLevel(log_level)
            for logger in self.loggers.values():
                logger.setLevel(log_level)
    
    def get_log_files(self) -> Dict[str, Path]:
        """
        Get dict of subsystem -> log file path mappings
        
        Returns:
            Dictionary mapping subsystem names to log file paths
        """
        log_files = {'main': self.log_dir / 'probe_basic.log'}
        
        for subsystem in self.loggers:
            log_files[subsystem] = self.log_dir / f'{subsystem}.log'
        
        return log_files
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Remove log files older than specified days
        
        Args:
            days_to_keep: Number of days of logs to retain
        """
        import time
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob('*.log*'):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    print(f"Removed old log file: {log_file}")
            except Exception as e:
                print(f"Error removing log file {log_file}: {e}")


# Global logger instance
_logger_instance: Optional[ProbeBasicLogger] = None

def initialize_logging(log_dir: Optional[Path] = None, log_level: str = 'INFO') -> ProbeBasicLogger:
    """
    Initialize the global logging system
    
    Args:
        log_dir: Directory for log files
        log_level: Default logging level
        
    Returns:
        ProbeBasicLogger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = ProbeBasicLogger(log_dir, log_level)
    
    return _logger_instance

def get_logger(subsystem: str) -> logging.Logger:
    """
    Get logger for specified subsystem
    
    Args:
        subsystem: Subsystem identifier
        
    Returns:
        Logger instance
    """
    if _logger_instance is None:
        initialize_logging()
    
    return _logger_instance.get_logger(subsystem)

def set_log_level(level: str, subsystem: Optional[str] = None):
    """
    Set logging level
    
    Args:
        level: Log level string
        subsystem: Optional subsystem to target
    """
    if _logger_instance is not None:
        _logger_instance.set_level(level, subsystem)

# Convenience functions for common subsystems
def get_main_logger() -> logging.Logger:
    """Get main application logger"""
    return get_logger(SUBSYSTEM_MAIN)

def get_ui_logger() -> logging.Logger:
    """Get UI subsystem logger"""
    return get_logger(SUBSYSTEM_UI)

def get_hal_logger() -> logging.Logger:
    """Get HAL subsystem logger"""
    return get_logger(SUBSYSTEM_HAL)

def get_probe_logger() -> logging.Logger:
    """Get probing subsystem logger"""
    return get_logger(SUBSYSTEM_PROBE)

def get_atc_logger() -> logging.Logger:
    """Get ATC subsystem logger"""
    return get_logger(SUBSYSTEM_ATC)

def get_job_logger() -> logging.Logger:
    """Get job manager subsystem logger"""
    return get_logger(SUBSYSTEM_JOB)

def get_safety_logger() -> logging.Logger:
    """Get safety subsystem logger"""
    return get_logger(SUBSYSTEM_SAFETY)

def get_network_logger() -> logging.Logger:
    """Get network subsystem logger"""
    return get_logger(SUBSYSTEM_NETWORK)

def get_diagnostics_logger() -> logging.Logger:
    """Get diagnostics subsystem logger"""
    return get_logger(SUBSYSTEM_DIAGNOSTICS)