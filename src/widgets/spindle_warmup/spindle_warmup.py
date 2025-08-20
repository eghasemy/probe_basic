#!/usr/bin/env python

import os
import json
from datetime import datetime, timedelta
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QFrame, QDialog, QMessageBox,
                            QProgressBar, QSpinBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QComboBox, QCheckBox, QTextEdit)
from qtpy.QtGui import QFont
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class SpindleWarmupDialog(QDialog):
    """Dialog for running spindle warmup sequence"""
    
    warmupStarted = Signal()
    warmupFinished = Signal(bool)  # bool: completed successfully
    
    def __init__(self, warmup_config, parent=None):
        super(SpindleWarmupDialog, self).__init__(parent)
        
        self.warmup_config = warmup_config
        self.current_step = 0
        self.total_steps = len(warmup_config.get('steps', []))
        self.is_running = False
        self.start_time = None
        
        self.setupUI()
        
    def setupUI(self):
        """Set up the warmup dialog UI"""
        self.setWindowTitle("Spindle Warmup Sequence")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("🔄 Spindle Warmup Program")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2196F3; padding: 10px;")
        layout.addWidget(title_label)
        
        # Description
        desc_text = self.warmup_config.get('description', 'Standard spindle warmup sequence')
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("padding: 5px; color: #666;")
        layout.addWidget(desc_label)
        
        # Progress section
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_layout = QVBoxLayout()
        
        # Overall progress
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, self.total_steps)
        self.overall_progress.setValue(0)
        self.overall_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(QLabel("Overall Progress:"))
        progress_layout.addWidget(self.overall_progress)
        
        # Step progress
        self.step_progress = QProgressBar()
        self.step_progress.setRange(0, 100)
        self.step_progress.setValue(0)
        progress_layout.addWidget(QLabel("Current Step:"))
        progress_layout.addWidget(self.step_progress)
        
        progress_frame.setLayout(progress_layout)
        layout.addWidget(progress_frame)
        
        # Current step info
        self.step_info_frame = QFrame()
        self.step_info_frame.setFrameStyle(QFrame.Box)
        self.step_info_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        step_info_layout = QVBoxLayout()
        
        self.current_step_label = QLabel("Ready to start warmup...")
        self.current_step_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.current_step_label.setAlignment(Qt.AlignCenter)
        step_info_layout.addWidget(self.current_step_label)
        
        self.step_details_label = QLabel("")
        self.step_details_label.setAlignment(Qt.AlignCenter)
        self.step_details_label.setWordWrap(True)
        step_info_layout.addWidget(self.step_details_label)
        
        self.step_info_frame.setLayout(step_info_layout)
        layout.addWidget(self.step_info_frame)
        
        # Warmup steps preview
        steps_frame = QFrame()
        steps_frame.setFrameStyle(QFrame.Box)
        steps_layout = QVBoxLayout()
        
        steps_title = QLabel("Warmup Steps:")
        steps_title.setFont(QFont("Arial", 11, QFont.Bold))
        steps_layout.addWidget(steps_title)
        
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(3)
        self.steps_table.setHorizontalHeaderLabels(["Step", "RPM", "Duration"])
        self.steps_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.steps_table.setMaximumHeight(120)
        
        # Populate table
        steps = self.warmup_config.get('steps', [])
        self.steps_table.setRowCount(len(steps))
        
        for i, step in enumerate(steps):
            self.steps_table.setItem(i, 0, QTableWidgetItem(f"Step {i+1}"))
            self.steps_table.setItem(i, 1, QTableWidgetItem(f"{step.get('rpm', 0)}"))
            duration = step.get('duration_seconds', 0)
            self.steps_table.setItem(i, 2, QTableWidgetItem(f"{duration}s"))
            
        steps_layout.addWidget(self.steps_table)
        steps_frame.setLayout(steps_layout)
        layout.addWidget(steps_frame)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Warmup")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover:enabled {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        button_layout.addWidget(self.close_button)
        button_layout.addStretch()
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.start_button)
        
        layout.addWidget(button_layout)
        self.setLayout(layout)
        
        # Connect signals
        self.start_button.clicked.connect(self.startWarmup)
        self.stop_button.clicked.connect(self.stopWarmup)
        self.close_button.clicked.connect(self.close)
        
        # Timer for warmup execution
        self.warmup_timer = QTimer()
        self.warmup_timer.timeout.connect(self.updateWarmup)
        
    def startWarmup(self):
        """Start the warmup sequence"""
        self.is_running = True
        self.current_step = 0
        self.start_time = datetime.now()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.warmupStarted.emit()
        
        # Start the first step
        self.executeCurrentStep()
        
        # Start update timer
        self.warmup_timer.start(100)  # Update every 100ms
        
    def stopWarmup(self):
        """Stop the warmup sequence"""
        self.is_running = False
        self.warmup_timer.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.current_step_label.setText("Warmup stopped by user")
        self.step_details_label.setText("Spindle stopped")
        
        # Stop spindle
        self.stopSpindle()
        
        LOG.info("Spindle warmup stopped by user")
        self.warmupFinished.emit(False)
        
    def executeCurrentStep(self):
        """Execute the current warmup step"""
        if self.current_step >= self.total_steps:
            self.completeWarmup()
            return
            
        steps = self.warmup_config.get('steps', [])
        if self.current_step < len(steps):
            step = steps[self.current_step]
            rpm = step.get('rpm', 0)
            duration = step.get('duration_seconds', 0)
            
            self.current_step_label.setText(f"Step {self.current_step + 1}: {rpm} RPM")
            self.step_details_label.setText(f"Running for {duration} seconds...")
            
            # Set spindle speed
            self.setSpindleSpeed(rpm)
            
            # Set step timer
            self.step_start_time = datetime.now()
            self.step_duration = duration
            
            LOG.info(f"Warmup step {self.current_step + 1}: {rpm} RPM for {duration}s")
            
    def updateWarmup(self):
        """Update warmup progress"""
        if not self.is_running:
            return
            
        # Update step progress
        elapsed = (datetime.now() - self.step_start_time).total_seconds()
        progress_percent = min(100, (elapsed / self.step_duration) * 100)
        self.step_progress.setValue(int(progress_percent))
        
        # Check if step is complete
        if elapsed >= self.step_duration:
            self.current_step += 1
            self.overall_progress.setValue(self.current_step)
            
            if self.current_step < self.total_steps:
                self.executeCurrentStep()
            else:
                self.completeWarmup()
                
    def completeWarmup(self):
        """Complete the warmup sequence"""
        self.is_running = False
        self.warmup_timer.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.current_step_label.setText("✅ Warmup Complete!")
        self.step_details_label.setText("Spindle is ready for operation")
        
        # Stop spindle
        self.stopSpindle()
        
        total_time = datetime.now() - self.start_time
        LOG.info(f"Spindle warmup completed in {total_time.total_seconds():.1f} seconds")
        
        self.warmupFinished.emit(True)
        
    def setSpindleSpeed(self, rpm):
        """Set spindle speed (would integrate with LinuxCNC)"""
        try:
            # Here you would send LinuxCNC commands to set spindle speed
            # This is a placeholder for the actual implementation
            LOG.info(f"Setting spindle speed to {rpm} RPM")
            
            # Example LinuxCNC command integration:
            # command = getPlugin('command')
            # if command:
            #     command.spindle(rpm)
            
        except Exception as e:
            LOG.error(f"Error setting spindle speed: {e}")
            
    def stopSpindle(self):
        """Stop the spindle"""
        try:
            LOG.info("Stopping spindle")
            
            # Example LinuxCNC command integration:
            # command = getPlugin('command')
            # if command:
            #     command.spindle(0)
            
        except Exception as e:
            LOG.error(f"Error stopping spindle: {e}")

class SpindleWarmupWidget(QWidget):
    """
    Spindle Warmup Widget
    Provides configurable RPM ladder warmup with progress tracking and spindle hours logging
    Based on Phase 7 requirements
    """
    
    warmupCompleted = Signal(float)  # Signal: spindle hours logged
    
    def __init__(self, parent=None):
        super(SpindleWarmupWidget, self).__init__(parent)
        
        self.status = getPlugin('status')
        self.command = getPlugin('command')
        
        # Default warmup configuration
        self.warmup_configs = {
            'quick': {
                'name': 'Quick Warmup (2 min)',
                'description': 'Fast warmup for light operations',
                'steps': [
                    {'rpm': 500, 'duration_seconds': 30},
                    {'rpm': 1000, 'duration_seconds': 30},
                    {'rpm': 2000, 'duration_seconds': 60}
                ]
            },
            'standard': {
                'name': 'Standard Warmup (5 min)',
                'description': 'Recommended warmup for normal operations',
                'steps': [
                    {'rpm': 300, 'duration_seconds': 60},
                    {'rpm': 600, 'duration_seconds': 60},
                    {'rpm': 1000, 'duration_seconds': 60},
                    {'rpm': 1500, 'duration_seconds': 60},
                    {'rpm': 2000, 'duration_seconds': 60}
                ]
            },
            'thorough': {
                'name': 'Thorough Warmup (10 min)',
                'description': 'Complete warmup for precision work',
                'steps': [
                    {'rpm': 200, 'duration_seconds': 120},
                    {'rpm': 500, 'duration_seconds': 120},
                    {'rpm': 800, 'duration_seconds': 120},
                    {'rpm': 1200, 'duration_seconds': 120},
                    {'rpm': 1800, 'duration_seconds': 120}
                ]
            }
        }
        
        self.spindle_hours_file = 'spindle_hours.json'
        self.spindle_hours_data = self.loadSpindleHours()
        
        self.setupUI()
        
        # Timer for spindle hours tracking
        self.hours_timer = QTimer()
        self.hours_timer.timeout.connect(self.updateSpindleHours)
        self.hours_timer.start(60000)  # Update every minute
        
    def setupUI(self):
        """Set up the widget UI"""
        self.setObjectName("spindleWarmupWidget")
        self.setMinimumSize(300, 200)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("🔄 Spindle Warmup")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2196F3; padding: 5px;")
        layout.addWidget(title_label)
        
        # Warmup selection
        selection_frame = QFrame()
        selection_frame.setFrameStyle(QFrame.Box)
        selection_layout = QVBoxLayout()
        
        selection_layout.addWidget(QLabel("Select Warmup Program:"))\n        
        self.warmup_combo = QComboBox()
        for key, config in self.warmup_configs.items():
            self.warmup_combo.addItem(config['name'], key)
        self.warmup_combo.setStyleSheet("padding: 5px;")
        selection_layout.addWidget(self.warmup_combo)
        
        # Description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; padding: 5px;")
        selection_layout.addWidget(self.description_label)
        
        selection_frame.setLayout(selection_layout)
        layout.addWidget(selection_frame)
        
        # Spindle hours display
        hours_frame = QFrame()
        hours_frame.setFrameStyle(QFrame.Box)
        hours_layout = QVBoxLayout()
        
        hours_title = QLabel("📊 Spindle Hours")
        hours_title.setFont(QFont("Arial", 11, QFont.Bold))
        hours_layout.addWidget(hours_title)
        
        self.total_hours_label = QLabel()
        self.session_hours_label = QLabel()
        self.last_warmup_label = QLabel()
        
        hours_layout.addWidget(self.total_hours_label)
        hours_layout.addWidget(self.session_hours_label)
        hours_layout.addWidget(self.last_warmup_label)
        
        hours_frame.setLayout(hours_layout)
        layout.addWidget(hours_frame)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.warmup_button = QPushButton("Start Warmup")
        self.warmup_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.warmup_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.reset_hours_button = QPushButton("Reset Hours")
        self.reset_hours_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        
        button_layout.addWidget(self.reset_hours_button)
        button_layout.addStretch()
        button_layout.addWidget(self.warmup_button)
        
        layout.addWidget(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Connect signals
        self.warmup_combo.currentTextChanged.connect(self.updateDescription)
        self.warmup_button.clicked.connect(self.startWarmup)
        self.reset_hours_button.clicked.connect(self.resetSpindleHours)
        
        # Initial update
        self.updateDescription()
        self.updateHoursDisplay()
        
    def updateDescription(self):
        """Update warmup description"""
        current_key = self.warmup_combo.currentData()
        if current_key and current_key in self.warmup_configs:
            config = self.warmup_configs[current_key]
            self.description_label.setText(config['description'])
            
    def startWarmup(self):
        """Start the selected warmup program"""
        current_key = self.warmup_combo.currentData()
        if not current_key or current_key not in self.warmup_configs:
            return
            
        config = self.warmup_configs[current_key]
        
        # Show warmup dialog
        dialog = SpindleWarmupDialog(config, self)
        dialog.warmupStarted.connect(self.onWarmupStarted)
        dialog.warmupFinished.connect(self.onWarmupFinished)
        
        dialog.exec_()
        
    def onWarmupStarted(self):
        """Handle warmup start"""
        LOG.info("Spindle warmup started")
        self.warmup_button.setEnabled(False)
        
    def onWarmupFinished(self, completed):
        """Handle warmup completion"""
        self.warmup_button.setEnabled(True)
        
        if completed:
            # Log the warmup
            self.spindle_hours_data['last_warmup'] = datetime.now().isoformat()
            self.spindle_hours_data['warmup_count'] = self.spindle_hours_data.get('warmup_count', 0) + 1
            
            # Add warmup time to spindle hours (estimate based on warmup duration)
            current_key = self.warmup_combo.currentData()
            if current_key and current_key in self.warmup_configs:
                config = self.warmup_configs[current_key]
                total_duration = sum(step.get('duration_seconds', 0) for step in config.get('steps', []))
                warmup_hours = total_duration / 3600.0  # Convert to hours
                
                self.spindle_hours_data['total_hours'] = self.spindle_hours_data.get('total_hours', 0) + warmup_hours
                self.spindle_hours_data['session_hours'] = self.spindle_hours_data.get('session_hours', 0) + warmup_hours
                
            self.saveSpindleHours()
            self.updateHoursDisplay()
            
            LOG.info("Spindle warmup completed successfully")
            self.warmupCompleted.emit(self.spindle_hours_data.get('total_hours', 0))
        else:
            LOG.info("Spindle warmup was interrupted")
            
    def updateSpindleHours(self):
        """Update spindle hours based on current spindle state"""
        if not self.status:
            return
            
        try:
            # Check if spindle is running
            spindle_data = self.status.spindle()
            if spindle_data and spindle_data.get('enabled', False):
                # Add one minute to session and total hours
                minute_hours = 1.0 / 60.0  # One minute in hours
                
                self.spindle_hours_data['total_hours'] = self.spindle_hours_data.get('total_hours', 0) + minute_hours
                self.spindle_hours_data['session_hours'] = self.spindle_hours_data.get('session_hours', 0) + minute_hours
                
                # Save every 10 minutes to avoid excessive disk writes
                if int(self.spindle_hours_data.get('total_hours', 0) * 60) % 10 == 0:
                    self.saveSpindleHours()
                    
                self.updateHoursDisplay()
                
        except Exception as e:
            LOG.error(f"Error updating spindle hours: {e}")
            
    def updateHoursDisplay(self):
        """Update the spindle hours display"""
        total_hours = self.spindle_hours_data.get('total_hours', 0)
        session_hours = self.spindle_hours_data.get('session_hours', 0)
        last_warmup = self.spindle_hours_data.get('last_warmup', 'Never')
        
        if last_warmup != 'Never':
            try:
                last_warmup_dt = datetime.fromisoformat(last_warmup)
                last_warmup = last_warmup_dt.strftime("%Y-%m-%d %H:%M")
            except:
                last_warmup = 'Unknown'
                
        self.total_hours_label.setText(f"Total Hours: {total_hours:.1f}")
        self.session_hours_label.setText(f"Session Hours: {session_hours:.1f}")
        self.last_warmup_label.setText(f"Last Warmup: {last_warmup}")
        
    def resetSpindleHours(self):
        """Reset spindle hours counter"""
        reply = QMessageBox.question(
            self,
            "Reset Spindle Hours",
            "Are you sure you want to reset the spindle hours counter?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.spindle_hours_data = {
                'total_hours': 0,
                'session_hours': 0,
                'last_warmup': 'Never',
                'warmup_count': 0,
                'reset_date': datetime.now().isoformat()
            }
            
            self.saveSpindleHours()
            self.updateHoursDisplay()
            
            LOG.info("Spindle hours counter reset")
            
    def loadSpindleHours(self):
        """Load spindle hours data from file"""
        try:
            if os.path.exists(self.spindle_hours_file):
                with open(self.spindle_hours_file, 'r') as f:
                    data = json.load(f)
                    
                # Reset session hours on startup
                data['session_hours'] = 0
                return data
                
        except Exception as e:
            LOG.error(f"Error loading spindle hours: {e}")
            
        # Return default data
        return {
            'total_hours': 0,
            'session_hours': 0,
            'last_warmup': 'Never',
            'warmup_count': 0
        }
        
    def saveSpindleHours(self):
        """Save spindle hours data to file"""
        try:
            with open(self.spindle_hours_file, 'w') as f:
                json.dump(self.spindle_hours_data, f, indent=2)
                
        except Exception as e:
            LOG.error(f"Error saving spindle hours: {e}")
            
    def getTotalSpindleHours(self):
        """Get total spindle hours"""
        return self.spindle_hours_data.get('total_hours', 0)
        
    def getSessionSpindleHours(self):
        """Get session spindle hours"""
        return self.spindle_hours_data.get('session_hours', 0)