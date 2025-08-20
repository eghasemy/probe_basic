#!/usr/bin/env python

import os
import json
from datetime import datetime, timedelta
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QFrame, QDialog, QMessageBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QComboBox, QSpinBox, QTextEdit, QCheckBox, QListWidget,
                            QListWidgetItem, QScrollArea)
from qtpy.QtGui import QFont, QIcon
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class MaintenanceTaskItem(QFrame):
    """Individual maintenance task item widget"""
    
    taskCompleted = Signal(str)  # Signal: task_id
    taskSnoozed = Signal(str, int)  # Signal: task_id, snooze_hours
    
    def __init__(self, task_data, parent=None):
        super(MaintenanceTaskItem, self).__init__(parent)
        
        self.task_data = task_data
        self.task_id = task_data.get('id', '')
        
        self.setupUI()
        
    def setupUI(self):
        """Set up the task item UI"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        # Determine urgency color
        urgency = self.task_data.get('urgency', 'normal')
        urgency_colors = {
            'critical': '#ffebee',
            'high': '#fff3e0', 
            'normal': '#f5f5f5',
            'low': '#e8f5e8'
        }
        
        border_colors = {
            'critical': '#f44336',
            'high': '#ff9800',
            'normal': '#757575',
            'low': '#4CAF50'
        }
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {urgency_colors.get(urgency, '#f5f5f5')};
                border: 2px solid {border_colors.get(urgency, '#757575')};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Header with title and urgency
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.task_data.get('title', 'Maintenance Task'))
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(title_label)
        
        urgency_label = QLabel(urgency.upper())
        urgency_label.setFont(QFont("Arial", 9, QFont.Bold))
        urgency_label.setStyleSheet(f"color: {border_colors.get(urgency, '#757575')};")
        header_layout.addWidget(urgency_label)
        
        layout.addLayout(header_layout)
        
        # Description
        description = self.task_data.get('description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; margin: 3px;")
            layout.addWidget(desc_label)
            
        # Due info
        due_hours = self.task_data.get('due_hours', 0)
        current_hours = self.task_data.get('current_hours', 0)
        overdue_hours = max(0, current_hours - due_hours)
        
        if overdue_hours > 0:
            due_text = f"⚠️ Overdue by {overdue_hours:.1f} hours"
            due_color = "#d32f2f"
        else:
            remaining_hours = due_hours - current_hours
            due_text = f"Due in {remaining_hours:.1f} hours"
            due_color = "#666"
            
        due_label = QLabel(due_text)
        due_label.setFont(QFont("Arial", 9))
        due_label.setStyleSheet(f"color: {due_color}; margin: 3px;")
        layout.addWidget(due_label)
        
        # Checklist items
        checklist = self.task_data.get('checklist', [])
        if checklist:
            checklist_label = QLabel("Checklist:")
            checklist_label.setFont(QFont("Arial", 9, QFont.Bold))
            layout.addWidget(checklist_label)
            
            for item in checklist[:3]:  # Show first 3 items
                item_label = QLabel(f"• {item}")
                item_label.setStyleSheet("color: #666; margin-left: 10px; font-size: 8px;")
                layout.addWidget(item_label)
                
            if len(checklist) > 3:
                more_label = QLabel(f"... and {len(checklist) - 3} more items")
                more_label.setStyleSheet("color: #888; margin-left: 10px; font-size: 8px; font-style: italic;")
                layout.addWidget(more_label)
                
        # Control buttons
        button_layout = QHBoxLayout()
        
        # Snooze options
        snooze_combo = QComboBox()
        snooze_combo.addItem("Snooze 1h", 1)
        snooze_combo.addItem("Snooze 8h", 8)
        snooze_combo.addItem("Snooze 24h", 24)
        snooze_combo.addItem("Snooze 1 week", 168)
        snooze_combo.setStyleSheet("padding: 2px; font-size: 8px;")
        
        snooze_button = QPushButton("Snooze")
        snooze_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                border: none;
                border-radius: 3px;
                color: white;
                padding: 4px 8px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        
        complete_button = QPushButton("Mark Complete")
        complete_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 3px;
                color: white;
                padding: 4px 8px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(snooze_combo)
        button_layout.addWidget(snooze_button)
        button_layout.addStretch()
        button_layout.addWidget(complete_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connect signals
        snooze_button.clicked.connect(lambda: self.snoozeTask(snooze_combo.currentData()))
        complete_button.clicked.connect(self.completeTask)
        
    def snoozeTask(self, hours):
        """Snooze the task for specified hours"""
        self.taskSnoozed.emit(self.task_id, hours)
        
    def completeTask(self):
        """Mark task as complete"""
        self.taskCompleted.emit(self.task_id)

class MaintenanceDialog(QDialog):
    """Dialog for detailed maintenance task management"""
    
    def __init__(self, maintenance_data, parent=None):
        super(MaintenanceDialog, self).__init__(parent)
        
        self.maintenance_data = maintenance_data
        
        self.setupUI()
        
    def setupUI(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Maintenance Management")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("🔧 Maintenance Management")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ff6b35; padding: 10px;")
        layout.addWidget(title_label)
        
        # Summary stats
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Box)
        stats_layout = QHBoxLayout()
        
        tasks = self.maintenance_data.get('tasks', [])
        overdue_tasks = [t for t in tasks if t.get('current_hours', 0) > t.get('due_hours', 0)]
        due_soon_tasks = [t for t in tasks if 0 <= (t.get('due_hours', 0) - t.get('current_hours', 0)) <= 10]
        
        overdue_label = QLabel(f"Overdue: {len(overdue_tasks)}")
        overdue_label.setStyleSheet("color: #f44336; font-weight: bold; padding: 5px;")
        
        due_soon_label = QLabel(f"Due Soon: {len(due_soon_tasks)}")
        due_soon_label.setStyleSheet("color: #ff9800; font-weight: bold; padding: 5px;")
        
        total_label = QLabel(f"Total Tasks: {len(tasks)}")
        total_label.setStyleSheet("color: #666; font-weight: bold; padding: 5px;")
        
        stats_layout.addWidget(overdue_label)
        stats_layout.addWidget(due_soon_label)
        stats_layout.addStretch()
        stats_layout.addWidget(total_label)
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Task table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["Task", "Description", "Due Hours", "Current Hours", "Status"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate table
        self.task_table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.task_table.setItem(i, 0, QTableWidgetItem(task.get('title', '')))
            self.task_table.setItem(i, 1, QTableWidgetItem(task.get('description', '')))
            self.task_table.setItem(i, 2, QTableWidgetItem(f"{task.get('due_hours', 0):.1f}"))
            self.task_table.setItem(i, 3, QTableWidgetItem(f"{task.get('current_hours', 0):.1f}"))
            
            # Status
            current_hours = task.get('current_hours', 0)
            due_hours = task.get('due_hours', 0)
            
            if current_hours > due_hours:
                status = f"OVERDUE ({current_hours - due_hours:.1f}h)"
                color = "#f44336"
            elif due_hours - current_hours <= 10:
                status = f"DUE SOON ({due_hours - current_hours:.1f}h)"
                color = "#ff9800"
            else:
                status = f"OK ({due_hours - current_hours:.1f}h remaining)"
                color = "#4CAF50"
                
            status_item = QTableWidgetItem(status)
            status_item.setForeground(color)
            self.task_table.setItem(i, 4, status_item)
            
        layout.addWidget(self.task_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addWidget(button_layout)
        self.setLayout(layout)

class MaintenanceRemindersWidget(QWidget):
    """
    Maintenance Reminders Widget
    Provides alerts based on hours/elapsed time with snooze/reschedule capabilities
    Based on Phase 7 requirements
    """
    
    maintenanceRequired = Signal(list)  # Signal: list of overdue tasks
    
    def __init__(self, parent=None):
        super(MaintenanceRemindersWidget, self).__init__(parent)
        
        self.maintenance_file = 'maintenance_data.json'
        self.maintenance_data = self.loadMaintenanceData()
        
        self.setupUI()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateMaintenanceTasks)
        self.update_timer.start(3600000)  # Update every hour
        
        # Initial update
        self.updateMaintenanceTasks()
        
    def setupUI(self):
        """Set up the widget UI"""
        self.setObjectName("maintenanceRemindersWidget")
        self.setMinimumSize(300, 150)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title with status indicator
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🔧 Maintenance")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(title_label)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 16))
        self.status_indicator.setStyleSheet("color: #4CAF50;")  # Green by default
        title_layout.addWidget(self.status_indicator)
        
        title_layout.addStretch()
        
        # Settings button
        settings_button = QPushButton("⚙️")
        settings_button.setMaximumSize(30, 30)
        settings_button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 15px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        settings_button.clicked.connect(self.showMaintenanceDialog)
        title_layout.addWidget(settings_button)
        
        layout.addLayout(title_layout)
        
        # Summary display
        self.summary_frame = QFrame()
        self.summary_frame.setFrameStyle(QFrame.Box)
        summary_layout = QVBoxLayout()
        
        self.summary_label = QLabel("All maintenance up to date")
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        
        self.summary_frame.setLayout(summary_layout)
        layout.addWidget(self.summary_frame)
        
        # Active alerts scroll area
        self.alerts_scroll = QScrollArea()
        self.alerts_scroll.setWidgetResizable(True)
        self.alerts_scroll.setMaximumHeight(200)
        self.alerts_scroll.setVisible(False)  # Hidden when no alerts
        
        self.alerts_widget = QWidget()
        self.alerts_layout = QVBoxLayout()
        self.alerts_widget.setLayout(self.alerts_layout)
        self.alerts_scroll.setWidget(self.alerts_widget)
        
        layout.addWidget(self.alerts_scroll)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.view_all_button = QPushButton("View All Tasks")
        self.view_all_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.view_all_button)
        
        layout.addWidget(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Connect signals
        self.view_all_button.clicked.connect(self.showMaintenanceDialog)
        
    def loadMaintenanceData(self):
        """Load maintenance data from file"""
        try:
            if os.path.exists(self.maintenance_file):
                with open(self.maintenance_file, 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            LOG.error(f"Error loading maintenance data: {e}")
            
        # Return default maintenance schedule
        return {
            'tasks': [
                {
                    'id': 'spindle_lubrication',
                    'title': 'Spindle Lubrication',
                    'description': 'Check and refill spindle lubrication system',
                    'due_hours': 100,
                    'current_hours': 0,
                    'urgency': 'normal',
                    'checklist': [
                        'Check oil level in spindle reservoir',
                        'Top up with recommended spindle oil',
                        'Check for oil leaks around spindle',
                        'Test spindle rotation smoothness'
                    ]
                },
                {
                    'id': 'way_lubrication',
                    'title': 'Way Lubrication',
                    'description': 'Lubricate machine ways and linear guides',
                    'due_hours': 50,
                    'current_hours': 0,
                    'urgency': 'normal',
                    'checklist': [
                        'Clean ways with appropriate solvent',
                        'Apply way oil to all sliding surfaces',
                        'Exercise all axes through full travel',
                        'Check for binding or rough movement'
                    ]
                },
                {
                    'id': 'coolant_change',
                    'title': 'Coolant System Service',
                    'description': 'Change coolant and clean system',
                    'due_hours': 200,
                    'current_hours': 0,
                    'urgency': 'normal',
                    'checklist': [
                        'Drain old coolant completely',
                        'Clean coolant tank and filters',
                        'Replace coolant pump filter',
                        'Fill with fresh coolant mixture',
                        'Test coolant flow and pressure'
                    ]
                },
                {
                    'id': 'spindle_inspection',
                    'title': 'Spindle Inspection',
                    'description': 'Detailed spindle condition inspection',
                    'due_hours': 500,
                    'current_hours': 0,
                    'urgency': 'high',
                    'checklist': [
                        'Check spindle runout with dial indicator',
                        'Inspect spindle taper for damage',
                        'Test drawbar operation',
                        'Check spindle bearing condition',
                        'Verify spindle speed accuracy'
                    ]
                },
                {
                    'id': 'belt_inspection',
                    'title': 'Drive Belt Inspection',
                    'description': 'Inspect and adjust drive belts',
                    'due_hours': 150,
                    'current_hours': 0,
                    'urgency': 'low',
                    'checklist': [
                        'Inspect belts for cracking or fraying',
                        'Check belt tension',
                        'Adjust belt tension if needed',
                        'Check pulley alignment',
                        'Test for belt slippage'
                    ]
                }
            ],
            'settings': {
                'reminder_threshold_hours': 10,  # Show reminders when within 10 hours
                'auto_snooze_enabled': False,
                'notification_enabled': True
            }
        }
        
    def saveMaintenanceData(self):
        """Save maintenance data to file"""
        try:
            with open(self.maintenance_file, 'w') as f:
                json.dump(self.maintenance_data, f, indent=2)
                
        except Exception as e:
            LOG.error(f"Error saving maintenance data: {e}")
            
    def updateMaintenanceTasks(self):
        """Update maintenance task status based on current spindle hours"""
        # Get current spindle hours from spindle warmup widget or other source
        # For now, use a simple counter that increments over time
        current_time = datetime.now()
        
        # Update current hours for all tasks (placeholder logic)
        for task in self.maintenance_data.get('tasks', []):
            # In a real implementation, this would come from actual machine hours
            # For demo purposes, increment slightly each update
            task['current_hours'] = task.get('current_hours', 0) + 0.1
            
        # Find overdue and due soon tasks
        tasks = self.maintenance_data.get('tasks', [])
        threshold = self.maintenance_data.get('settings', {}).get('reminder_threshold_hours', 10)
        
        overdue_tasks = []
        due_soon_tasks = []
        
        for task in tasks:
            current_hours = task.get('current_hours', 0)
            due_hours = task.get('due_hours', 0)
            
            if current_hours > due_hours:
                overdue_tasks.append(task)
            elif due_hours - current_hours <= threshold:
                due_soon_tasks.append(task)
                
        # Update UI
        self.updateMaintenanceDisplay(overdue_tasks, due_soon_tasks)
        
        # Save updated data
        self.saveMaintenanceData()
        
        # Emit signal if there are maintenance requirements
        if overdue_tasks or due_soon_tasks:
            self.maintenanceRequired.emit(overdue_tasks + due_soon_tasks)
            
    def updateMaintenanceDisplay(self, overdue_tasks, due_soon_tasks):
        """Update the maintenance display"""
        # Clear existing alerts
        for i in reversed(range(self.alerts_layout.count())):
            child = self.alerts_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # Update status indicator and summary
        if overdue_tasks:
            self.status_indicator.setStyleSheet("color: #f44336;")  # Red
            self.summary_label.setText(f"⚠️ {len(overdue_tasks)} overdue maintenance task(s)")
            self.summary_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffebee;
                    border: 2px solid #f44336;
                    border-radius: 6px;
                    padding: 5px;
                }
            """)
        elif due_soon_tasks:
            self.status_indicator.setStyleSheet("color: #ff9800;")  # Orange
            self.summary_label.setText(f"🔔 {len(due_soon_tasks)} maintenance task(s) due soon")
            self.summary_frame.setStyleSheet("""
                QFrame {
                    background-color: #fff3e0;
                    border: 2px solid #ff9800;
                    border-radius: 6px;
                    padding: 5px;
                }
            """)
        else:
            self.status_indicator.setStyleSheet("color: #4CAF50;")  # Green
            self.summary_label.setText("✅ All maintenance up to date")
            self.summary_frame.setStyleSheet("""
                QFrame {
                    background-color: #e8f5e8;
                    border: 2px solid #4CAF50;
                    border-radius: 6px;
                    padding: 5px;
                }
            """)
            
        # Show alerts for overdue and due soon tasks
        alert_tasks = overdue_tasks + due_soon_tasks
        
        if alert_tasks:
            self.alerts_scroll.setVisible(True)
            
            for task in alert_tasks[:3]:  # Show up to 3 alerts
                task_item = MaintenanceTaskItem(task)
                task_item.taskCompleted.connect(self.onTaskCompleted)
                task_item.taskSnoozed.connect(self.onTaskSnoozed)
                self.alerts_layout.addWidget(task_item)
                
            if len(alert_tasks) > 3:
                more_label = QLabel(f"... and {len(alert_tasks) - 3} more tasks")
                more_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
                more_label.setAlignment(Qt.AlignCenter)
                self.alerts_layout.addWidget(more_label)
                
        else:
            self.alerts_scroll.setVisible(False)
            
    def onTaskCompleted(self, task_id):
        """Handle task completion"""
        # Find and update the task
        for task in self.maintenance_data.get('tasks', []):
            if task.get('id') == task_id:
                # Reset the task hours and set completion date
                task['current_hours'] = 0
                task['last_completed'] = datetime.now().isoformat()
                
                LOG.info(f"Maintenance task completed: {task.get('title', task_id)}")
                break
                
        # Refresh display
        self.updateMaintenanceTasks()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Task Completed",
            f"Maintenance task '{task_id}' has been marked as completed.\n\nThe counter has been reset."
        )
        
    def onTaskSnoozed(self, task_id, snooze_hours):
        """Handle task snooze"""
        # Find and update the task
        for task in self.maintenance_data.get('tasks', []):
            if task.get('id') == task_id:
                # Add snooze hours to due hours
                task['due_hours'] = task.get('due_hours', 0) + snooze_hours
                task['last_snoozed'] = datetime.now().isoformat()
                
                LOG.info(f"Maintenance task snoozed: {task.get('title', task_id)} for {snooze_hours} hours")
                break
                
        # Refresh display
        self.updateMaintenanceTasks()
        
    def showMaintenanceDialog(self):
        """Show the detailed maintenance dialog"""
        dialog = MaintenanceDialog(self.maintenance_data, self)
        dialog.exec_()
        
    def getOverdueTasks(self):
        """Get list of overdue maintenance tasks"""
        overdue = []
        for task in self.maintenance_data.get('tasks', []):
            if task.get('current_hours', 0) > task.get('due_hours', 0):
                overdue.append(task)
        return overdue
        
    def getDueSoonTasks(self, threshold_hours=10):
        """Get list of tasks due soon"""
        due_soon = []
        for task in self.maintenance_data.get('tasks', []):
            remaining = task.get('due_hours', 0) - task.get('current_hours', 0)
            if 0 <= remaining <= threshold_hours:
                due_soon.append(task)
        return due_soon