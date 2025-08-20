#!/usr/bin/env python

"""
Phase 7 Standalone Demo - UI only
Shows Phase 7 widgets without QtPyVCP dependencies for demonstration
"""

import sys
import os
from qtpy.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QTabWidget, QLabel, QFrame, QPushButton,
                            QGridLayout, QProgressBar, QComboBox, QSpinBox,
                            QTextEdit, QCheckBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QScrollArea, QListWidget, QMessageBox)
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QFont

class MockHomingBadge(QFrame):
    """Mock homing badge for demo"""
    
    def __init__(self, axis_name, is_homed=False):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setMinimumSize(80, 60)
        self.setMaximumSize(120, 80)
        
        layout = QVBoxLayout()
        
        # Axis label
        axis_label = QLabel(f"{axis_name}")
        axis_label.setAlignment(Qt.AlignCenter)
        axis_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(axis_label)
        
        # Status label
        status_label = QLabel("HOMED" if is_homed else "NOT HOMED")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFont(QFont("Arial", 8))
        layout.addWidget(status_label)
        
        # Home button
        home_button = QPushButton("REHOME" if is_homed else "HOME")
        home_button.setFont(QFont("Arial", 8))
        home_button.clicked.connect(lambda: self.toggleHomed())
        layout.addWidget(home_button)
        
        self.setLayout(layout)
        self.updateStatus(is_homed)
        
        # Store references
        self.axis_label = axis_label
        self.status_label = status_label
        self.home_button = home_button
        self.is_homed = is_homed
        
    def updateStatus(self, is_homed):
        """Update badge status"""
        self.is_homed = is_homed
        
        if is_homed:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d5a2d;
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                }
                QLabel { color: #ffffff; }
                QPushButton {
                    background-color: #4CAF50;
                    border: 1px solid #45a049;
                    border-radius: 4px;
                    color: white;
                    padding: 2px;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            self.status_label.setText("HOMED")
            self.home_button.setText("REHOME")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #5a2d2d;
                    border: 2px solid #f44336;
                    border-radius: 8px;
                }
                QLabel { color: #ffffff; }
                QPushButton {
                    background-color: #f44336;
                    border: 1px solid #da190b;
                    border-radius: 4px;
                    color: white;
                    padding: 2px;
                }
                QPushButton:hover { background-color: #da190b; }
            """)
            self.status_label.setText("NOT HOMED")
            self.home_button.setText("HOME")
            
    def toggleHomed(self):
        """Toggle homed status for demo"""
        self.updateStatus(not self.is_homed)

class MockHomingManager(QWidget):
    """Mock homing manager for demo"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        
    def setupUI(self):
        """Set up the UI"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Homing Status")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Badges
        badges_layout = QHBoxLayout()
        
        self.x_badge = MockHomingBadge("X", True)  # X is homed
        self.y_badge = MockHomingBadge("Y", False)  # Y not homed
        self.z_badge = MockHomingBadge("Z", True)  # Z is homed
        
        badges_layout.addWidget(self.x_badge)
        badges_layout.addWidget(self.y_badge)
        badges_layout.addWidget(self.z_badge)
        badges_layout.addStretch()
        
        layout.addLayout(badges_layout)
        
        # Home all button
        home_all_button = QPushButton("Home All Axes")
        home_all_button.setFont(QFont("Arial", 10, QFont.Bold))
        home_all_button.clicked.connect(self.homeAll)
        home_all_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        control_layout.addWidget(home_all_button)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        self.setLayout(layout)
        
    def homeAll(self):
        """Home all axes for demo"""
        self.x_badge.updateStatus(True)
        self.y_badge.updateStatus(True)
        self.z_badge.updateStatus(True)
        QMessageBox.information(self, "Homing", "All axes homed successfully!")

class MockSpindleWarmup(QWidget):
    """Mock spindle warmup widget"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        
    def setupUI(self):
        """Set up the UI"""
        layout = QVBoxLayout()
        
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
        
        selection_layout.addWidget(QLabel("Select Warmup Program:"))
        
        self.warmup_combo = QComboBox()
        self.warmup_combo.addItems([
            "Quick Warmup (2 min)",
            "Standard Warmup (5 min)",
            "Thorough Warmup (10 min)"
        ])
        self.warmup_combo.setStyleSheet("padding: 5px;")
        selection_layout.addWidget(self.warmup_combo)
        
        # Description
        self.description_label = QLabel("Fast warmup for light operations")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; padding: 5px;")
        selection_layout.addWidget(self.description_label)
        
        selection_frame.setLayout(selection_layout)
        layout.addWidget(selection_frame)
        
        # Hours display
        hours_frame = QFrame()
        hours_frame.setFrameStyle(QFrame.Box)
        hours_layout = QVBoxLayout()
        
        hours_title = QLabel("📊 Spindle Hours")
        hours_title.setFont(QFont("Arial", 11, QFont.Bold))
        hours_layout.addWidget(hours_title)
        
        hours_layout.addWidget(QLabel("Total Hours: 247.3"))
        hours_layout.addWidget(QLabel("Session Hours: 2.1"))
        hours_layout.addWidget(QLabel("Last Warmup: 2024-01-15 09:30"))
        
        hours_frame.setLayout(hours_layout)
        layout.addWidget(hours_frame)
        
        # Warmup button
        warmup_button = QPushButton("Start Warmup")
        warmup_button.setFont(QFont("Arial", 11, QFont.Bold))
        warmup_button.clicked.connect(self.startWarmup)
        warmup_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(warmup_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)
        
    def startWarmup(self):
        """Start warmup demo"""
        QMessageBox.information(self, "Warmup", "Warmup sequence started!\n\nThis would normally run the selected RPM ladder sequence.")

class MockMaintenanceWidget(QWidget):
    """Mock maintenance widget"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        
    def setupUI(self):
        """Set up the UI"""
        layout = QVBoxLayout()
        
        # Title with status
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🔧 Maintenance")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(title_label)
        
        status_indicator = QLabel("●")
        status_indicator.setFont(QFont("Arial", 16))
        status_indicator.setStyleSheet("color: #ff9800;")  # Orange - some issues
        title_layout.addWidget(status_indicator)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Summary
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Box)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        
        summary_layout = QVBoxLayout()
        summary_label = QLabel("🔔 2 maintenance task(s) due soon")
        summary_label.setAlignment(Qt.AlignCenter)
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        summary_frame.setLayout(summary_layout)
        
        layout.addWidget(summary_frame)
        
        # Sample maintenance task
        task_frame = QFrame()
        task_frame.setFrameStyle(QFrame.Box)
        task_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        task_layout = QVBoxLayout()
        
        # Task header
        task_title = QLabel("Spindle Lubrication - HIGH")
        task_title.setFont(QFont("Arial", 11, QFont.Bold))
        task_layout.addWidget(task_title)
        
        task_desc = QLabel("Check and refill spindle lubrication system")
        task_desc.setStyleSheet("color: #666; margin: 3px;")
        task_layout.addWidget(task_desc)
        
        task_due = QLabel("Due in 8.3 hours")
        task_due.setStyleSheet("color: #666; margin: 3px;")
        task_layout.addWidget(task_due)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        snooze_combo = QComboBox()
        snooze_combo.addItems(["Snooze 1h", "Snooze 8h", "Snooze 24h"])
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
            QPushButton:hover { background-color: #f57c00; }
        """)
        
        complete_button = QPushButton("Mark Complete")
        complete_button.clicked.connect(self.completeTask)
        complete_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 3px;
                color: white;
                padding: 4px 8px;
                font-size: 9px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        button_layout.addWidget(snooze_combo)
        button_layout.addWidget(snooze_button)
        button_layout.addStretch()
        button_layout.addWidget(complete_button)
        
        task_layout.addLayout(button_layout)
        task_frame.setLayout(task_layout)
        
        layout.addWidget(task_frame)
        
        # View all button
        view_all_button = QPushButton("View All Tasks")
        view_all_button.clicked.connect(self.viewAllTasks)
        view_all_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(view_all_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def completeTask(self):
        """Complete task demo"""
        QMessageBox.information(self, "Task Complete", "Maintenance task marked as complete!\n\nCounter has been reset.")
        
    def viewAllTasks(self):
        """View all tasks demo"""
        QMessageBox.information(self, "All Tasks", "This would show the complete maintenance management dialog.")

class MockLimitOverride(QWidget):
    """Mock limit override widget"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        
    def setupUI(self):
        """Set up the UI"""
        layout = QVBoxLayout()
        
        # Normally hidden, but show for demo
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        status_layout = QVBoxLayout()
        
        status_title = QLabel("Soft Limit Override Active")
        status_title.setFont(QFont("Arial", 12, QFont.Bold))
        status_title.setAlignment(Qt.AlignCenter)
        status_title.setStyleSheet("color: #ff6b35; padding: 5px;")
        status_layout.addWidget(status_title)
        
        time_label = QLabel("Time remaining: 3:42")
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(time_label)
        
        reason_label = QLabel("Reason: Machine Recovery - Tool change required")
        reason_label.setAlignment(Qt.AlignCenter)
        reason_label.setWordWrap(True)
        reason_label.setFont(QFont("Arial", 9))
        reason_label.setStyleSheet("color: #666; padding: 5px;")
        status_layout.addWidget(reason_label)
        
        # Revert button
        revert_button = QPushButton("Revert to Normal Limits")
        revert_button.clicked.connect(self.revertOverride)
        revert_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        status_layout.addWidget(revert_button)
        
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
        # Trigger button for demo
        trigger_button = QPushButton("Simulate Limit Trigger")
        trigger_button.clicked.connect(self.triggerLimit)
        trigger_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        
        demo_layout = QHBoxLayout()
        demo_layout.addStretch()
        demo_layout.addWidget(trigger_button)
        layout.addLayout(demo_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def revertOverride(self):
        """Revert override demo"""
        QMessageBox.information(self, "Override Reverted", "Soft limit override has been reverted.\n\nNormal limits are now active.")
        
    def triggerLimit(self):
        """Trigger limit demo"""
        QMessageBox.warning(self, "Limit Triggered", "⚠️ SOFT LIMIT TRIGGERED ⚠️\n\nThis would normally show the override dialog with countdown.")

class Phase7DemoWindow(QMainWindow):
    """Main demo window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Phase 7 Demo - Safety, Homing, Limits, Overrides & Warmup")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Integrated Panel Tab
        integrated_panel = QWidget()
        integrated_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("🛡️ Phase 7 - Safety & Maintenance")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2196F3; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        integrated_layout.addWidget(title_label)
        
        # Top row: Homing and Limits
        top_row = QHBoxLayout()
        
        homing_frame = QFrame()
        homing_frame.setFrameStyle(QFrame.Box)
        homing_layout = QVBoxLayout()
        homing_layout.addWidget(MockHomingManager())
        homing_frame.setLayout(homing_layout)
        top_row.addWidget(homing_frame)
        
        limit_frame = QFrame()
        limit_frame.setFrameStyle(QFrame.Box)
        limit_layout = QVBoxLayout()
        limit_layout.addWidget(MockLimitOverride())
        limit_frame.setLayout(limit_layout)
        top_row.addWidget(limit_frame)
        
        integrated_layout.addLayout(top_row)
        
        # Bottom row: Warmup and Maintenance
        bottom_row = QHBoxLayout()
        
        warmup_frame = QFrame()
        warmup_frame.setFrameStyle(QFrame.Box)
        warmup_layout = QVBoxLayout()
        warmup_layout.addWidget(MockSpindleWarmup())
        warmup_frame.setLayout(warmup_layout)
        bottom_row.addWidget(warmup_frame)
        
        maintenance_frame = QFrame()
        maintenance_frame.setFrameStyle(QFrame.Box)
        maintenance_layout = QVBoxLayout()
        maintenance_layout.addWidget(MockMaintenanceWidget())
        maintenance_frame.setLayout(maintenance_layout)
        bottom_row.addWidget(maintenance_frame)
        
        integrated_layout.addLayout(bottom_row)
        integrated_panel.setLayout(integrated_layout)
        
        tab_widget.addTab(integrated_panel, "🛡️ Integrated Safety Panel")
        
        # Individual tabs
        tab_widget.addTab(MockHomingManager(), "🏠 Homing Manager")
        tab_widget.addTab(MockLimitOverride(), "⚠️ Limit Override")
        tab_widget.addTab(MockSpindleWarmup(), "🔄 Spindle Warmup")
        tab_widget.addTab(MockMaintenanceWidget(), "🔧 Maintenance")
        
        layout.addWidget(tab_widget)

def main():
    """Run the demo"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    demo_window = Phase7DemoWindow()
    demo_window.show()
    
    print("Phase 7 UI Demo")
    print("===============")
    print("This demonstrates the visual interface for Phase 7 features:")
    print("• Homing Manager with per-axis status badges")
    print("• Soft Limit Override with active status display")
    print("• Spindle Warmup with program selection")
    print("• Maintenance Reminders with task management")
    print()
    print("Interactive elements:")
    print("- Click homing badges to toggle status")
    print("- Try warmup and maintenance buttons")
    print("- Test limit override simulation")
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())