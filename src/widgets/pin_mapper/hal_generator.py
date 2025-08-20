#!/usr/bin/env python

import os
import re
from datetime import datetime
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class HALGenerator:
    """
    Generate HAL file from pin mappings using Jinja2-style templates
    """
    
    def __init__(self, mappings):
        self.mappings = mappings
        self.block_id = "pb_touch_generated"
        
    def generate(self, output_file):
        """Generate HAL file with gated blocks"""
        try:
            # Read existing file if it exists
            existing_content = ""
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    existing_content = f.read()
            
            # Remove existing generated block
            cleaned_content = self._remove_existing_block(existing_content)
            
            # Generate new block
            generated_block = self._generate_block()
            
            # Combine content
            if cleaned_content.strip():
                final_content = cleaned_content + "\n\n" + generated_block
            else:
                final_content = generated_block
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(final_content)
                
            LOG.info(f"Generated HAL file: {output_file}")
            return True
            
        except Exception as e:
            LOG.error(f"Failed to generate HAL file: {e}")
            return False
            
    def _remove_existing_block(self, content):
        """Remove existing generated block from content"""
        pattern = rf"# --- PB-TOUCH GENERATED \(do not edit\) ---\s*\n# begin: {self.block_id}.*?# end: {self.block_id}\s*\n?"
        return re.sub(pattern, "", content, flags=re.DOTALL)
        
    def _generate_block(self):
        """Generate the HAL block content"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = [
            "# --- PB-TOUCH GENERATED (do not edit) ---",
            f"# begin: {self.block_id}",
            f"# Generated at: {timestamp}",
            f"# Pin mappings: {len(self.mappings)} total",
            ""
        ]
        
        # Group mappings by subsystem
        subsystems = {}
        for function_name, mapping in self.mappings.items():
            subsystem = mapping.get('subsystem', 'misc')
            if subsystem not in subsystems:
                subsystems[subsystem] = []
            subsystems[subsystem].append((function_name, mapping))
        
        # Generate HAL for each subsystem
        for subsystem, mappings in sorted(subsystems.items()):
            lines.append(f"# --- {subsystem.upper()} MAPPINGS ---")
            
            for function_name, mapping in mappings:
                signal = mapping.get('signal', '')
                pin = mapping.get('pin', '')
                direction = mapping.get('direction', 'input')
                notes = mapping.get('notes', '')
                
                if signal and pin:
                    if notes:
                        lines.append(f"# {function_name}: {notes}")
                    
                    if direction == 'input':
                        lines.append(f"net {signal} <= {pin}")
                    elif direction == 'output':
                        lines.append(f"net {signal} => {pin}")
                    else:  # io
                        lines.append(f"net {signal} <=> {pin}")
                        
                    lines.append("")
            
            lines.append("")
        
        # Add default example mappings if none exist
        if not self.mappings:
            lines.extend([
                "# --- EXAMPLE MAPPINGS ---",
                "# No mappings configured yet.",
                "# Use the Pin Mapper to create mappings.",
                "",
                "# Example input mapping:",
                "# net cycle-start <= hm2_7i76e.0.7i76.0.0.input-00",
                "",
                "# Example output mapping:",
                "# net spindle-enable => hm2_7i76e.0.7i76.0.0.output-00",
                ""
            ])
        
        lines.extend([
            f"# end: {self.block_id}",
            ""
        ])
        
        return "\n".join(lines)
        
    def preview(self):
        """Generate preview of HAL content without writing to file"""
        return self._generate_block()
        
    def validate_mappings(self):
        """Validate mappings for conflicts and errors"""
        errors = []
        signals = {}
        pins = {}
        
        for function_name, mapping in self.mappings.items():
            signal = mapping.get('signal', '')
            pin = mapping.get('pin', '')
            
            # Check for duplicate signals
            if signal in signals:
                errors.append(f"Duplicate signal '{signal}' in functions: {signals[signal]}, {function_name}")
            else:
                signals[signal] = function_name
                
            # Check for duplicate pins
            if pin in pins:
                errors.append(f"Duplicate pin '{pin}' in functions: {pins[pin]}, {function_name}")
            else:
                pins[pin] = function_name
                
            # Check for empty required fields
            if not signal:
                errors.append(f"Function '{function_name}' missing signal name")
            if not pin:
                errors.append(f"Function '{function_name}' missing pin address")
                
        return errors