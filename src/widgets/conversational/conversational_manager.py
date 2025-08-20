"""
Enhanced Conversational Manager
Phase 6: Conversational operations with JSON sidecar generation
"""

import os
import json
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMessageBox

from .facing import FacingWidget
from .drill_widget import DrillWidget  
from .hole_circle import HoleCircleWidget
from .circular_pocket import CircularPocketWidget
from .rectangular_pocket import RectangularPocketWidget
from .slot import SlotWidget
from .bolt_circle import BoltCircleWidget

class ConversationalManager(QWidget):
    """Enhanced conversational manager with JSON sidecar support"""
    
    # Signals
    gcode_generated = pyqtSignal(str, str)  # gcode_path, json_path
    
    def __init__(self, parent=None):
        super(ConversationalManager, self).__init__(parent)
        
        self.output_directory = os.path.expanduser("~/linuxcnc/configs/generated")
        os.makedirs(self.output_directory, exist_ok=True)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different operations
        self.tab_widget = QTabWidget()
        
        # Add operation tabs
        self.facing_widget = FacingWidget()
        self.tab_widget.addTab(self.facing_widget, "Facing")
        
        self.drill_widget = DrillWidget()  
        self.tab_widget.addTab(self.drill_widget, "Drilling")
        
        self.hole_circle_widget = HoleCircleWidget()
        self.tab_widget.addTab(self.hole_circle_widget, "Hole Circle")
        
        self.circular_pocket_widget = CircularPocketWidget()
        self.tab_widget.addTab(self.circular_pocket_widget, "Circular Pocket")
        
        self.rectangular_pocket_widget = RectangularPocketWidget()
        self.tab_widget.addTab(self.rectangular_pocket_widget, "Rectangular Pocket")
        
        self.slot_widget = SlotWidget()
        self.tab_widget.addTab(self.slot_widget, "Slot")
        
        self.bolt_circle_widget = BoltCircleWidget()
        self.tab_widget.addTab(self.bolt_circle_widget, "Bolt Circle")
        
        layout.addWidget(self.tab_widget)
        
        # Connect post signals
        self.setup_post_connections()
        
    def setup_post_connections(self):
        """Setup connections for G-code generation"""
        widgets = [
            self.facing_widget,
            self.drill_widget,
            self.hole_circle_widget,
            self.circular_pocket_widget,
            self.rectangular_pocket_widget,
            self.slot_widget,
            self.bolt_circle_widget
        ]
        
        for widget in widgets:
            # Override the post_to_file method to include JSON generation
            original_post = widget.on_post_to_file
            widget.on_post_to_file = lambda w=widget, op=original_post: self.enhanced_post_to_file(w, op)
    
    def enhanced_post_to_file(self, widget, original_post_method):
        """Enhanced post to file with JSON sidecar generation"""
        # Check if widget is valid
        ok, errors = widget.is_valid()
        if not ok:
            widget._show_error_msg('GCode Error', '\n'.join(errors))
            return
            
        # Generate G-code using original method
        try:
            # Get the operation
            op = widget.create_op()
            
            # Generate G-code
            gcode_lines = op.split('\n') if isinstance(op, str) else []
            
            # Create filenames
            base_name = widget.name() or 'Untitled'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gcode_filename = f"{base_name}_{timestamp}.ngc"
            json_filename = f"{base_name}_{timestamp}.json"
            
            gcode_path = os.path.join(self.output_directory, gcode_filename)
            json_path = os.path.join(self.output_directory, json_filename)
            
            # Write G-code file
            with open(gcode_path, 'w') as f:
                if isinstance(op, str):
                    f.write(op)
                else:
                    f.write(str(op))
                    
            # Generate JSON sidecar
            json_data = self.generate_json_sidecar(widget, gcode_path)
            
            # Write JSON file
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
                
            # Emit signal
            self.gcode_generated.emit(gcode_path, json_path)
            
            # Show success message
            QMessageBox.information(widget, "Success", 
                                  f"Generated:\n{gcode_filename}\n{json_filename}")
                                  
            # Ask to load
            if widget._confirm_action('Load GCode', 'Would you like to open the file in the viewer?'):
                from qtpyvcp.actions.program_actions import load as loadProgram
                loadProgram(gcode_path)
                
        except Exception as e:
            QMessageBox.critical(widget, "Error", f"Failed to generate files:\n{e}")
            
    def generate_json_sidecar(self, widget, gcode_path):
        """Generate JSON sidecar with operation parameters"""
        # Get widget type
        widget_type = widget.__class__.__name__.replace('Widget', '').lower()
        
        # Base metadata
        json_data = {
            "format_version": "1.0",
            "created_time": datetime.now().isoformat(),
            "operation_type": widget_type,
            "gcode_file": os.path.basename(gcode_path),
            "pb_touch_phase": 6,
            "parameters": {}
        }
        
        # Common parameters
        common_params = {
            "name": widget.name(),
            "wcs": widget.wcs(),
            "units": widget.unit(),
            "tool_number": widget.tool_number(),
            "tool_diameter": widget.tool_diameter(),
            "spindle_rpm": widget.spindle_rpm(),
            "spindle_direction": widget.spindle_direction(),
            "coolant": widget.coolant(),
            "xy_feed_rate": widget.xy_feed_rate(),
            "z_feed_rate": widget.z_feed_rate(),
            "clearance_height": widget.clearance_height(),
            "retract_height": widget.retract_height(),
            "z_start": widget.z_start(),
            "z_end": widget.z_end()
        }
        
        json_data["parameters"]["common"] = common_params
        
        # Operation-specific parameters
        operation_params = {}
        
        if widget_type == "facing":
            operation_params = {
                "x_start": widget.x_start(),
                "x_end": widget.x_end(),
                "y_start": widget.y_start(),
                "y_end": widget.y_end(),
                "step_over": widget.step_over(),
                "step_down": widget.step_down()
            }
            
        elif widget_type == "circularpocket":
            operation_params = {
                "center_x": widget.center_x(),
                "center_y": widget.center_y(),
                "diameter": widget.diameter(),
                "step_over": widget.step_over(),
                "step_down": widget.step_down()
            }
            
        elif widget_type == "rectangularpocket":
            operation_params = {
                "center_x": widget.center_x(),
                "center_y": widget.center_y(),
                "length": widget.length(),
                "width": widget.width(),
                "step_over": widget.step_over(),
                "step_down": widget.step_down()
            }
            
        elif widget_type == "slot":
            operation_params = {
                "start_x": widget.start_x(),
                "start_y": widget.start_y(),
                "end_x": widget.end_x(),
                "end_y": widget.end_y(),
                "width": widget.width(),
                "step_over": widget.step_over(),
                "step_down": widget.step_down()
            }
            
        elif widget_type == "boltcircle":
            operation_params = {
                "center_x": widget.center_x(),
                "center_y": widget.center_y(),
                "circle_diameter": widget.circle_diameter(),
                "hole_diameter": widget.hole_diameter(),
                "hole_count": widget.hole_count(),
                "start_angle": widget.start_angle(),
                "step_down": widget.step_down()
            }
            
        # Add drilling parameters for drill and hole_circle widgets
        if hasattr(widget, 'peck_depth'):
            operation_params["peck_depth"] = widget.peck_depth()
            operation_params["drilling_mode"] = "peck"
        else:
            operation_params["drilling_mode"] = "standard"
            
        json_data["parameters"]["operation"] = operation_params
        
        # Template information
        json_data["template"] = {
            "metric": widget.unit() == "MM",
            "imperial": widget.unit() == "IN"
        }
        
        return json_data
        
    def load_from_json(self, json_path):
        """Load operation from JSON sidecar file"""
        try:
            with open(json_path, 'r') as f:
                json_data = json.load(f)
                
            operation_type = json_data.get("operation_type", "")
            parameters = json_data.get("parameters", {})
            
            # Find the appropriate widget
            widget_map = {
                "facing": self.facing_widget,
                "drilling": self.drill_widget,
                "hole_circle": self.hole_circle_widget,
                "circularpocket": self.circular_pocket_widget,
                "rectangularpocket": self.rectangular_pocket_widget,
                "slot": self.slot_widget,
                "boltcircle": self.bolt_circle_widget
            }
            
            widget = widget_map.get(operation_type)
            if not widget:
                raise ValueError(f"Unknown operation type: {operation_type}")
                
            # Load common parameters
            common = parameters.get("common", {})
            for param, value in common.items():
                if hasattr(widget, f"{param}_input"):
                    getattr(widget, f"{param}_input").setValue(value)
                elif hasattr(widget, f"{param}_input") and hasattr(getattr(widget, f"{param}_input"), "setText"):
                    getattr(widget, f"{param}_input").setText(str(value))
                    
            # Load operation-specific parameters
            operation = parameters.get("operation", {})
            for param, value in operation.items():
                if hasattr(widget, f"{param}_input"):
                    getattr(widget, f"{param}_input").setValue(value)
                    
            # Switch to the appropriate tab
            tab_index = list(widget_map.values()).index(widget)
            self.tab_widget.setCurrentIndex(tab_index)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file:\n{e}")
            return False