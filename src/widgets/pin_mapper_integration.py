#!/usr/bin/env python

"""
Pin Mapper Integration for Probe Basic
Demonstrates how to integrate pin mapping functionality into the main application
"""

import os
import sys
from qtpy.QtCore import QObject, Signal, Slot
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget

class PinMapperIntegration(QWidget):
    """
    Integration widget for Pin Mapper functionality
    This can be embedded in the main Probe Basic application
    """
    
    def __init__(self, parent=None):
        super(PinMapperIntegration, self).__init__(parent)
        
        self.setupUI()
        
    def setupUI(self):
        """Setup the integration UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different tools
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Pin Mapper tab
        try:
            from .pin_mapper.pin_map_tree import PinMapTree
            pin_mapper = PinMapTree(self)
            pin_mapper.mappingChanged.connect(self.onMappingsChanged)
            self.tab_widget.addTab(pin_mapper, "Pin Mapper")
        except ImportError as e:
            print(f"Pin Mapper not available: {e}")
            
        # Machine Config Wizard tab
        wizard_tab = QWidget()
        wizard_layout = QVBoxLayout(wizard_tab)
        
        wizard_button = QPushButton("Launch Machine Config Wizard")
        wizard_button.clicked.connect(self.launchWizard)
        wizard_layout.addWidget(wizard_button)
        wizard_layout.addStretch()
        
        self.tab_widget.addTab(wizard_tab, "Machine Wizard")
        
        # HAL Tools tab
        hal_tab = QWidget()
        hal_layout = QVBoxLayout(hal_tab)
        
        generate_button = QPushButton("Generate HAL Files")
        generate_button.clicked.connect(self.generateHAL)
        hal_layout.addWidget(generate_button)
        
        validate_button = QPushButton("Validate Configuration")
        validate_button.clicked.connect(self.validateConfig)
        hal_layout.addWidget(validate_button)
        
        hal_layout.addStretch()
        self.tab_widget.addTab(hal_tab, "HAL Tools")
        
    @Slot()
    def onMappingsChanged(self):
        """Handle mapping changes"""
        print("Pin mappings have been updated")
        # Here you could emit signals to update other parts of the application
        
    @Slot()  
    def launchWizard(self):
        """Launch the Machine Config Wizard"""
        try:
            from .machine_config_wizard.machine_config_wizard import MachineConfigWizard
            wizard = MachineConfigWizard(self)
            if wizard.exec_() == wizard.Accepted:
                config_data = wizard.getConfigData()
                print(f"Machine config completed: {config_data}")
                # Here you would generate the actual machine configuration files
        except ImportError as e:
            print(f"Machine Config Wizard not available: {e}")
            
    @Slot()
    def generateHAL(self):
        """Generate HAL files from current mappings"""
        try:
            from .pin_mapper.hal_generator import HALGenerator
            import yaml
            
            # Load current mappings
            config_dir = os.path.join(os.path.dirname(__file__), '../configs/probe_basic/config/pinmap.d')
            config_file = os.path.join(config_dir, 'default.yaml')
            
            mappings = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    mappings = data.get('mappings', {})
            
            generator = HALGenerator(mappings)
            hal_file = os.path.join(os.path.dirname(__file__), '../configs/probe_basic/hal/pb_touch_sim.hal')
            
            success = generator.generate(hal_file)
            print(f"HAL generation: {'Success' if success else 'Failed'}")
            
        except Exception as e:
            print(f"HAL generation error: {e}")
            
    @Slot()
    def validateConfig(self):
        """Validate current configuration"""
        try:
            from .pin_mapper.hal_generator import HALGenerator
            import yaml
            
            # Load current mappings
            config_dir = os.path.join(os.path.dirname(__file__), '../configs/probe_basic/config/pinmap.d')
            config_file = os.path.join(config_dir, 'default.yaml')
            
            mappings = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    mappings = data.get('mappings', {})
            
            generator = HALGenerator(mappings)
            errors = generator.validate_mappings()
            
            if errors:
                print("Validation errors found:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("Configuration validation: PASSED")
                
        except Exception as e:
            print(f"Validation error: {e}")


# Example of how to add this to the main Probe Basic application
def add_pin_mapper_to_probe_basic():
    """
    Example function showing how to integrate pin mapper into Probe Basic
    This would be called during application initialization
    """
    
    # This is pseudo-code showing the integration approach
    # In the actual ProbeBasic class (probe_basic.py), you would:
    
    # 1. Add a new tab or menu item for Pin Mapper
    # main_window.addTab(PinMapperIntegration(), "Pin Mapper")
    
    # 2. Connect signals for real-time updates
    # pin_mapper.mappingChanged.connect(main_window.onConfigChanged)
    
    # 3. Add menu items to File menu
    # file_menu.addAction("Generate HAL Files", pin_mapper.generateHAL)
    # file_menu.addAction("Machine Config Wizard", pin_mapper.launchWizard)
    
    # 4. Add to settings/preferences 
    # settings.addSection("Pin Mapping", pin_mapper.getSettingsWidget())
    
    pass


if __name__ == "__main__":
    # Standalone test
    from qtpy.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    integration = PinMapperIntegration()
    integration.show()
    
    sys.exit(app.exec_())