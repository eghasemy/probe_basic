#!/usr/bin/env python

"""
Phase 7 Demo - Safety, Homing, Limits, Overrides & Warmup
Demonstrates all Phase 7 features and acceptance criteria
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from qtpy.QtCore import Qt

from widgets.phase7_integration import Phase7IntegrationPanel
from widgets.homing_manager.homing_manager import HomingManager
from widgets.limit_override.limit_override import LimitOverrideManager
from widgets.spindle_warmup.spindle_warmup import SpindleWarmupWidget  
from widgets.maintenance_reminders.maintenance_reminders import MaintenanceRemindersWidget

class Phase7DemoWindow(QMainWindow):
    """Main demo window for Phase 7 features"""
    
    def __init__(self):
        super(Phase7DemoWindow, self).__init__()
        
        self.setWindowTitle("Phase 7 Demo - Safety, Homing, Limits, Overrides & Warmup")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Integrated Panel Tab
        self.integration_panel = Phase7IntegrationPanel()
        tab_widget.addTab(self.integration_panel, "🛡️ Integrated Safety Panel")
        
        # Individual Component Tabs
        self.homing_manager = HomingManager()
        tab_widget.addTab(self.homing_manager, "🏠 Homing Manager")
        
        self.limit_manager = LimitOverrideManager()
        tab_widget.addTab(self.limit_manager, "⚠️ Limit Override")
        
        self.warmup_widget = SpindleWarmupWidget()
        tab_widget.addTab(self.warmup_widget, "🔄 Spindle Warmup")
        
        self.maintenance_widget = MaintenanceRemindersWidget()
        tab_widget.addTab(self.maintenance_widget, "🔧 Maintenance")
        
        layout.addWidget(tab_widget)
        
        # Connect signals for demo
        self.connectDemoSignals()
        
    def connectDemoSignals(self):
        """Connect signals for demo purposes"""
        # Get safety manager from integration panel
        safety_manager = self.integration_panel.getSafetyManager()
        
        # Connect safety signals
        safety_manager.homingRequired.connect(self.onHomingRequired)
        safety_manager.limitOverrideActive.connect(self.onLimitOverrideActive)
        safety_manager.maintenanceOverdue.connect(self.onMaintenanceOverdue)
        
    def onHomingRequired(self, operation):
        """Handle homing required signal"""
        print(f"DEMO: Homing required for operation: {operation}")
        
    def onLimitOverrideActive(self, active):
        """Handle limit override state change"""
        print(f"DEMO: Limit override active: {active}")
        
    def onMaintenanceOverdue(self, tasks):
        """Handle maintenance overdue signal"""
        print(f"DEMO: Maintenance overdue - {len(tasks)} task(s)")

def main():
    """Run the Phase 7 demo"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show demo window
    demo_window = Phase7DemoWindow()
    demo_window.show()
    
    print("Phase 7 Demo Started")
    print("=" * 50)
    print("Features demonstrated:")
    print("• Homing Manager with per-axis status badges")
    print("• Soft Limit Override with countdown and confirmation")
    print("• Spindle Warmup with configurable RPM ladder")
    print("• Maintenance Reminders with snooze/reset capabilities")
    print("• Integrated safety management system")
    print("=" * 50)
    print()
    print("Acceptance Criteria Testing:")
    print("1. Check homing status and try homing operations")
    print("2. Trigger soft limit override dialog")
    print("3. Run warmup sequences and observe spindle hours")
    print("4. View maintenance tasks and test snooze/complete")
    print()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()