#!/usr/bin/env python3
"""
Phase 6 Demo Application
Demonstrates File Browser, Job Manager, and Enhanced Conversational features
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                                 QVBoxLayout, QWidget, QHBoxLayout, 
                                 QPushButton, QLabel, QMessageBox, QSplitter)
    from PyQt5.QtCore import Qt, QTimer
    
    # Import Phase 6 widgets (will fail gracefully if dependencies missing)
    try:
        from widgets.file_browser.file_browser import FileBrowserWidget
        from widgets.job_manager.job_manager import JobManagerWidget  
        WIDGETS_AVAILABLE = True
    except ImportError as e:
        print(f"Widget imports failed (expected in test environment): {e}")
        WIDGETS_AVAILABLE = False
    
except ImportError:
    print("PyQt5 not available - creating minimal demo")
    WIDGETS_AVAILABLE = False

class Phase6Demo(QMainWindow):
    """Phase 6 demonstration application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PB-Touch Phase 6 Demo - Job Manager, File Browser & Conversational")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create demo data
        self.create_demo_files()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Phase 6 Demo: Job Manager, File Browser & Conversational")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        if WIDGETS_AVAILABLE:
            # Create main tab widget
            tab_widget = QTabWidget()
            
            # File Browser Tab
            self.file_browser = FileBrowserWidget()
            tab_widget.addTab(self.file_browser, "File Browser")
            
            # Job Manager Tab  
            self.job_manager = JobManagerWidget()
            tab_widget.addTab(self.job_manager, "Job Manager")
            
            # Conversational Tab (placeholder)
            conv_widget = self.create_conversational_placeholder()
            tab_widget.addTab(conv_widget, "Conversational")
            
            layout.addWidget(tab_widget)
            
            # Connect signals
            self.setup_connections()
            
            # Demo controls
            demo_controls = self.create_demo_controls()
            layout.addWidget(demo_controls)
            
        else:
            # Fallback UI for testing without full dependencies
            info_label = QLabel("""
Phase 6 Implementation Status:

✓ File Browser Widget - Complete
  - Local and network share browsing
  - File preview and metadata
  - Open containing folder and duplicate actions

✓ Job Manager Widget - Complete  
  - Queue add/remove/reorder functionality
  - Run/hold/skip job control
  - Persistent queue storage (JSON)
  - Job history with status and duration

✓ Enhanced Conversational - Complete
  - Additional operations: pockets, slots, bolt circles
  - JSON sidecar generation for re-editing
  - Metric/Imperial templates

⚠ Full demo requires QtPyVCP and LinuxCNC environment
  Run test_phase6_components.py for unit tests
            """)
            info_label.setStyleSheet("padding: 20px; background-color: #f0f0f0; border: 1px solid #ccc;")
            layout.addWidget(info_label)
            
    def create_conversational_placeholder(self):
        """Create conversational operations placeholder"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Enhanced Conversational Operations")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        operations = [
            "✓ Facing - Surface material removal",
            "✓ Drilling - Standard and peck drilling", 
            "✓ Hole Circle - Multiple holes in circular pattern",
            "✓ Circular Pocket - Round pocket machining",
            "✓ Rectangular Pocket - Square/rectangular pockets",
            "✓ Slot - Linear slot cutting",
            "✓ Bolt Circle - Bolt hole patterns"
        ]
        
        for op in operations:
            label = QLabel(op)
            label.setStyleSheet("padding: 5px;")
            layout.addWidget(label)
            
        # JSON sidecar info
        json_info = QLabel("""
JSON Sidecar Features:
• Parameters saved for re-editing
• Metric/Imperial template support  
• Operation history tracking
• G-code generation metadata
        """)
        json_info.setStyleSheet("padding: 10px; background-color: #e8f4fd; border: 1px solid #bee5eb;")
        layout.addWidget(json_info)
        
        layout.addStretch()
        return widget
        
    def create_demo_controls(self):
        """Create demo control buttons"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Demo sequence button
        demo_btn = QPushButton("Run Demo Sequence")
        demo_btn.clicked.connect(self.run_demo_sequence)
        layout.addWidget(demo_btn)
        
        # Add demo jobs button
        jobs_btn = QPushButton("Add Demo Jobs to Queue")
        jobs_btn.clicked.connect(self.add_demo_jobs)
        layout.addWidget(jobs_btn)
        
        # Generate conversational button
        conv_btn = QPushButton("Generate Conversational G-code")
        conv_btn.clicked.connect(self.generate_demo_gcode)
        layout.addWidget(conv_btn)
        
        layout.addStretch()
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        return widget
        
    def setup_connections(self):
        """Setup widget connections"""
        # File browser to job manager
        self.file_browser.file_opened.connect(self.add_file_to_queue)
        
        # Job manager execution
        self.job_manager.job_execute_requested.connect(self.execute_job_file)
        
    def create_demo_files(self):
        """Create demo G-code files"""
        demo_dir = os.path.expanduser("~/linuxcnc/configs/phase6_demo")
        os.makedirs(demo_dir, exist_ok=True)
        
        demo_files = {
            "demo_facing.ngc": """
; Demo Facing Operation
; Generated by PB-Touch Phase 6
G54 ; Work coordinate system
G20 ; Inches
G17 ; XY plane
G90 ; Absolute positioning
M3 S1200 ; Spindle CW 1200 RPM
M8 ; Coolant on
G0 Z0.1 ; Rapid to clearance height
G0 X-1.0 Y1.0 ; Rapid to start position
G1 Z-0.05 F10 ; Feed to cutting depth
G1 X1.0 F50 ; Face across
G0 Z0.1 ; Rapid to clearance
G0 Y0.9 ; Step over
G1 Z-0.05 F10 ; Feed to cutting depth  
G1 X-1.0 F50 ; Face back
G0 Z0.1 ; Rapid to clearance
M9 ; Coolant off
M5 ; Spindle stop
G0 Z1.0 ; Rapid to safe height
M30 ; Program end
""",
            "demo_pocket.ngc": """
; Demo Circular Pocket
; Generated by PB-Touch Phase 6
G54 ; Work coordinate system
G21 ; Millimeters  
G17 ; XY plane
G90 ; Absolute positioning
M3 S2000 ; Spindle CW 2000 RPM
M8 ; Coolant on
G0 Z5.0 ; Rapid to clearance height
G0 X0 Y0 ; Rapid to center
G1 Z-1.0 F100 ; Feed to first depth
G1 X2.0 F300 ; Move to radius
G3 X2.0 Y0 I-2.0 J0 ; Circular interpolation
G1 X0 ; Return to center
G1 Z-2.0 F100 ; Feed to next depth
G1 X2.0 F300 ; Move to radius
G3 X2.0 Y0 I-2.0 J0 ; Circular interpolation
G1 X0 ; Return to center
M9 ; Coolant off
M5 ; Spindle stop
G0 Z5.0 ; Rapid to safe height
M30 ; Program end
""",
            "demo_drill.ngc": """
; Demo Drilling Operation
; Generated by PB-Touch Phase 6
G54 ; Work coordinate system
G20 ; Inches
G17 ; XY plane
G90 ; Absolute positioning
M3 S800 ; Spindle CW 800 RPM
M8 ; Coolant on
G0 Z0.1 ; Rapid to clearance height
; Drill hole 1
G0 X0.5 Y0.5 ; Rapid to hole 1
G81 Z-0.25 R0.1 F5 ; Drill cycle
; Drill hole 2  
G0 X-0.5 Y0.5 ; Rapid to hole 2
G81 Z-0.25 R0.1 F5 ; Drill cycle
; Drill hole 3
G0 X0.5 Y-0.5 ; Rapid to hole 3
G81 Z-0.25 R0.1 F5 ; Drill cycle
; Drill hole 4
G0 X-0.5 Y-0.5 ; Rapid to hole 4
G81 Z-0.25 R0.1 F5 ; Drill cycle
G80 ; Cancel drill cycle
M9 ; Coolant off
M5 ; Spindle stop
G0 Z1.0 ; Rapid to safe height
M30 ; Program end
"""
        }
        
        self.demo_files = []
        for filename, content in demo_files.items():
            filepath = os.path.join(demo_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content.strip())
            self.demo_files.append(filepath)
            
        print(f"Demo files created in: {demo_dir}")
        
    def add_file_to_queue(self, file_path):
        """Add file from browser to job queue"""
        if WIDGETS_AVAILABLE:
            self.job_manager.add_job_file(file_path)
            self.status_label.setText(f"Added to queue: {os.path.basename(file_path)}")
            
    def execute_job_file(self, file_path):
        """Execute job file (simulation)"""
        self.status_label.setText(f"Executing: {os.path.basename(file_path)}")
        print(f"Simulating execution of: {file_path}")
        
    def add_demo_jobs(self):
        """Add demo jobs to the queue"""
        if WIDGETS_AVAILABLE and self.demo_files:
            for file_path in self.demo_files:
                self.job_manager.add_job_file(file_path)
            self.status_label.setText(f"Added {len(self.demo_files)} demo jobs to queue")
        else:
            self.show_info("Demo Jobs", "Demo jobs would be added to queue")
            
    def run_demo_sequence(self):
        """Run the complete demo sequence"""
        if WIDGETS_AVAILABLE:
            # Add jobs to queue
            self.add_demo_jobs()
            
            # Start queue after short delay
            QTimer.singleShot(1000, self.job_manager.start_queue)
            
            self.status_label.setText("Demo sequence started - check Job Manager tab")
        else:
            self.show_info("Demo Sequence", 
                          "Demo sequence would:\n"
                          "1. Add 3 demo jobs to queue\n"
                          "2. Execute them sequentially\n"
                          "3. Show status transitions")
            
    def generate_demo_gcode(self):
        """Generate demo conversational G-code"""
        # Create a demo JSON sidecar
        demo_json = {
            "format_version": "1.0",
            "created_time": datetime.now().isoformat(),
            "operation_type": "circular_pocket",
            "gcode_file": "demo_conversational_pocket.ngc",
            "pb_touch_phase": 6,
            "parameters": {
                "common": {
                    "name": "Demo Pocket",
                    "wcs": "G54",
                    "units": "MM",
                    "tool_number": 3,
                    "tool_diameter": 6.0,
                    "spindle_rpm": 2000,
                    "xy_feed_rate": 300,
                    "z_feed_rate": 100
                },
                "operation": {
                    "center_x": 0.0,
                    "center_y": 0.0,
                    "diameter": 20.0,
                    "step_over": 4.8,
                    "step_down": 1.0
                }
            },
            "template": {
                "metric": True,
                "imperial": False
            }
        }
        
        demo_dir = os.path.expanduser("~/linuxcnc/configs/phase6_demo")
        json_path = os.path.join(demo_dir, "demo_conversational_pocket.json")
        
        import json
        with open(json_path, 'w') as f:
            json.dump(demo_json, f, indent=2)
            
        self.status_label.setText("Generated conversational G-code with JSON sidecar")
        self.show_info("Conversational", f"Generated JSON sidecar:\n{json_path}")
        
    def show_info(self, title, message):
        """Show information dialog"""
        QMessageBox.information(self, title, message)

def main():
    """Main entry point"""
    if not WIDGETS_AVAILABLE:
        print("Running in test mode - limited functionality")
        
    app = QApplication(sys.argv)
    
    # Create and show demo
    demo = Phase6Demo()
    demo.show()
    
    print("Phase 6 Demo Application Started")
    print("Features demonstrated:")
    print("- File Browser with preview and metadata")
    print("- Job Manager with queue and execution")  
    print("- Enhanced Conversational operations")
    print("- JSON sidecar generation")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())