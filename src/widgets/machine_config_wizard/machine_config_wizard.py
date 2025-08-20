#!/usr/bin/env python

import os
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
                           QFormLayout, QLabel, QLineEdit, QComboBox, QSpinBox,
                           QCheckBox, QGroupBox, QTextEdit, QButtonGroup, QRadioButton)
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)

class MachineConfigWizard(QWizard):
    """
    Machine Configuration Wizard
    Steps: Machine Type → Axes → Switches → Spindle → Coolant → ATC → Summary
    """
    
    # Page IDs
    PAGE_MACHINE_TYPE = 0
    PAGE_AXES = 1
    PAGE_SWITCHES = 2
    PAGE_SPINDLE = 3
    PAGE_COOLANT = 4
    PAGE_ATC = 5
    PAGE_SUMMARY = 6
    
    def __init__(self, parent=None):
        super(MachineConfigWizard, self).__init__(parent)
        
        self.setWindowTitle("Machine Configuration Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.HaveHelpButton, False)
        self.resize(600, 500)
        
        # Configuration data
        self.config_data = {}
        
        self.setupPages()
        
    def setupPages(self):
        """Setup wizard pages"""
        self.addPage(MachineTypePage())
        self.addPage(AxesPage())
        self.addPage(SwitchesPage())
        self.addPage(SpindlePage())
        self.addPage(CoolantPage())
        self.addPage(ATCPage())
        self.addPage(SummaryPage())
        
    def getConfigData(self):
        """Get collected configuration data"""
        return self.config_data


class MachineTypePage(QWizardPage):
    """Machine Type selection page"""
    
    def __init__(self):
        super(MachineTypePage, self).__init__()
        
        self.setTitle("Machine Type")
        self.setSubTitle("Select your machine configuration type")
        
        layout = QVBoxLayout(self)
        
        # Machine type selection
        self.machine_group = QButtonGroup()
        
        self.mill_radio = QRadioButton("Mill/Router")
        self.mill_radio.setChecked(True)
        self.mill_radio.toggled.connect(self.onMachineTypeChanged)
        self.machine_group.addButton(self.mill_radio)
        layout.addWidget(self.mill_radio)
        
        self.lathe_radio = QRadioButton("Lathe")
        self.lathe_radio.toggled.connect(self.onMachineTypeChanged)
        self.machine_group.addButton(self.lathe_radio)
        layout.addWidget(self.lathe_radio)
        
        layout.addWidget(QLabel())
        
        # Basic info
        form = QFormLayout()
        
        self.machine_name_edit = QLineEdit("PB-Touch Machine")
        form.addRow("Machine Name:", self.machine_name_edit)
        
        self.units_combo = QComboBox()
        self.units_combo.addItems(["inch", "mm"])
        form.addRow("Units:", self.units_combo)
        
        layout.addLayout(form)
        layout.addStretch()
        
    def onMachineTypeChanged(self):
        """Handle machine type change"""
        self.completeChanged.emit()
        
    def isComplete(self):
        """Check if page is complete"""
        return self.machine_name_edit.text().strip() != ""
        
    def validatePage(self):
        """Validate page before proceeding"""
        wizard = self.wizard()
        wizard.config_data['machine_type'] = 'mill' if self.mill_radio.isChecked() else 'lathe'
        wizard.config_data['machine_name'] = self.machine_name_edit.text().strip()
        wizard.config_data['units'] = self.units_combo.currentText()
        return True


class AxesPage(QWizardPage):
    """Axes configuration page"""
    
    def __init__(self):
        super(AxesPage, self).__init__()
        
        self.setTitle("Axes Configuration")
        self.setSubTitle("Configure your machine axes")
        
        layout = QVBoxLayout(self)
        
        # Axes selection
        axes_group = QGroupBox("Available Axes")
        axes_layout = QVBoxLayout(axes_group)
        
        self.x_axis_check = QCheckBox("X Axis")
        self.x_axis_check.setChecked(True)
        self.x_axis_check.setEnabled(False)  # X is required
        axes_layout.addWidget(self.x_axis_check)
        
        self.y_axis_check = QCheckBox("Y Axis")
        self.y_axis_check.setChecked(True)
        axes_layout.addWidget(self.y_axis_check)
        
        self.z_axis_check = QCheckBox("Z Axis")
        self.z_axis_check.setChecked(True)
        axes_layout.addWidget(self.z_axis_check)
        
        self.a_axis_check = QCheckBox("A Axis (Rotary)")
        axes_layout.addWidget(self.a_axis_check)
        
        self.b_axis_check = QCheckBox("B Axis (Rotary)")
        axes_layout.addWidget(self.b_axis_check)
        
        self.c_axis_check = QCheckBox("C Axis (Rotary)")
        axes_layout.addWidget(self.c_axis_check)
        
        layout.addWidget(axes_group)
        
        # Travel limits
        limits_group = QGroupBox("Travel Limits")
        limits_layout = QFormLayout(limits_group)
        
        self.x_travel_edit = QLineEdit("24.0")
        limits_layout.addRow("X Travel:", self.x_travel_edit)
        
        self.y_travel_edit = QLineEdit("16.0")
        limits_layout.addRow("Y Travel:", self.y_travel_edit)
        
        self.z_travel_edit = QLineEdit("8.0")
        limits_layout.addRow("Z Travel:", self.z_travel_edit)
        
        layout.addWidget(limits_group)
        layout.addStretch()
        
    def validatePage(self):
        """Validate page before proceeding"""
        wizard = self.wizard()
        wizard.config_data['axes'] = {
            'x': True,  # Always enabled
            'y': self.y_axis_check.isChecked(),
            'z': self.z_axis_check.isChecked(),
            'a': self.a_axis_check.isChecked(),
            'b': self.b_axis_check.isChecked(),
            'c': self.c_axis_check.isChecked()
        }
        wizard.config_data['travel_limits'] = {
            'x': float(self.x_travel_edit.text() or "0"),
            'y': float(self.y_travel_edit.text() or "0"),
            'z': float(self.z_travel_edit.text() or "0")
        }
        return True


class SwitchesPage(QWizardPage):
    """Limit switches and probe configuration"""
    
    def __init__(self):
        super(SwitchesPage, self).__init__()
        
        self.setTitle("Switches & Probe")
        self.setSubTitle("Configure limit switches and probe settings")
        
        layout = QVBoxLayout(self)
        
        # Limit switches
        limits_group = QGroupBox("Limit Switches")
        limits_layout = QVBoxLayout(limits_group)
        
        self.home_switches_check = QCheckBox("Home switches enabled")
        self.home_switches_check.setChecked(True)
        limits_layout.addWidget(self.home_switches_check)
        
        self.limit_switches_check = QCheckBox("Limit switches enabled")
        self.limit_switches_check.setChecked(True)
        limits_layout.addWidget(self.limit_switches_check)
        
        layout.addWidget(limits_group)
        
        # Probe
        probe_group = QGroupBox("Touch Probe")
        probe_layout = QVBoxLayout(probe_group)
        
        self.probe_enabled_check = QCheckBox("Touch probe enabled")
        self.probe_enabled_check.setChecked(True)
        probe_layout.addWidget(self.probe_enabled_check)
        
        probe_form = QFormLayout()
        self.probe_tip_diameter_edit = QLineEdit("0.125")
        probe_form.addRow("Tip Diameter:", self.probe_tip_diameter_edit)
        
        self.probe_feed_rate_edit = QLineEdit("10.0")
        probe_form.addRow("Feed Rate:", self.probe_feed_rate_edit)
        
        probe_layout.addLayout(probe_form)
        layout.addWidget(probe_group)
        
        layout.addStretch()
        
    def validatePage(self):
        """Validate page before proceeding"""
        wizard = self.wizard()
        wizard.config_data['switches'] = {
            'home_switches': self.home_switches_check.isChecked(),
            'limit_switches': self.limit_switches_check.isChecked()
        }
        wizard.config_data['probe'] = {
            'enabled': self.probe_enabled_check.isChecked(),
            'tip_diameter': float(self.probe_tip_diameter_edit.text() or "0.125"),
            'feed_rate': float(self.probe_feed_rate_edit.text() or "10.0")
        }
        return True


class SpindlePage(QWizardPage):
    """Spindle configuration"""
    
    def __init__(self):
        super(SpindlePage, self).__init__()
        
        self.setTitle("Spindle Configuration")
        self.setSubTitle("Configure spindle settings")
        
        layout = QVBoxLayout(self)
        
        # Spindle type
        type_group = QGroupBox("Spindle Type")
        type_layout = QVBoxLayout(type_group)
        
        self.spindle_group = QButtonGroup()
        
        self.vfd_radio = QRadioButton("VFD Controlled")
        self.vfd_radio.setChecked(True)
        self.spindle_group.addButton(self.vfd_radio)
        type_layout.addWidget(self.vfd_radio)
        
        self.manual_radio = QRadioButton("Manual Control")
        self.spindle_group.addButton(self.manual_radio)
        type_layout.addWidget(self.manual_radio)
        
        layout.addWidget(type_group)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.max_rpm_edit = QLineEdit("3000")
        settings_layout.addRow("Max RPM:", self.max_rpm_edit)
        
        self.min_rpm_edit = QLineEdit("100")
        settings_layout.addRow("Min RPM:", self.min_rpm_edit)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
    def validatePage(self):
        """Validate page before proceeding"""
        wizard = self.wizard()
        wizard.config_data['spindle'] = {
            'type': 'vfd' if self.vfd_radio.isChecked() else 'manual',
            'max_rpm': int(self.max_rpm_edit.text() or "3000"),
            'min_rpm': int(self.min_rpm_edit.text() or "100")
        }
        return True


class CoolantPage(QWizardPage):
    """Coolant configuration"""
    
    def __init__(self):
        super(CoolantPage, self).__init__()
        
        self.setTitle("Coolant Configuration")
        self.setSubTitle("Configure coolant options")
        
        layout = QVBoxLayout(self)
        
        coolant_group = QGroupBox("Coolant Options")
        coolant_layout = QVBoxLayout(coolant_group)
        
        self.mist_check = QCheckBox("Mist coolant")
        coolant_layout.addWidget(self.mist_check)
        
        self.flood_check = QCheckBox("Flood coolant")
        coolant_layout.addWidget(self.flood_check)
        
        layout.addWidget(coolant_group)
        layout.addStretch()
        
    def validatePage(self):
        """Validate page before proceeding"""
        wizard = self.wizard()
        wizard.config_data['coolant'] = {
            'mist': self.mist_check.isChecked(),
            'flood': self.flood_check.isChecked()
        }
        return True


class ATCPage(QWizardPage):
    """ATC configuration"""
    
    def __init__(self):
        super(ATCPage, self).__init__()
        
        self.setTitle("ATC Configuration")
        self.setSubTitle("Configure Automatic Tool Changer")
        
        layout = QVBoxLayout(self)
        
        # ATC Type
        atc_group = QGroupBox("ATC Type")
        atc_layout = QVBoxLayout(atc_group)
        
        self.atc_group = QButtonGroup()
        
        self.no_atc_radio = QRadioButton("No ATC (Manual tool changes)")
        self.no_atc_radio.setChecked(True)
        self.atc_group.addButton(self.no_atc_radio)
        atc_layout.addWidget(self.no_atc_radio)
        
        self.carousel_radio = QRadioButton("Carousel ATC")
        self.atc_group.addButton(self.carousel_radio)
        atc_layout.addWidget(self.carousel_radio)
        
        self.rack_radio = QRadioButton("Rack ATC")
        self.atc_group.addButton(self.rack_radio)
        atc_layout.addWidget(self.rack_radio)
        
        layout.addWidget(atc_group)
        
        # Settings
        settings_group = QGroupBox("ATC Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.tool_pockets_spin = QSpinBox()
        self.tool_pockets_spin.setRange(1, 99)
        self.tool_pockets_spin.setValue(12)
        settings_layout.addRow("Tool Pockets:", self.tool_pockets_spin)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
    def validatePage(self):
        """Validate page before proceeding"""
        wizard = self.wizard()
        atc_type = 'none'
        if self.carousel_radio.isChecked():
            atc_type = 'carousel'
        elif self.rack_radio.isChecked():
            atc_type = 'rack'
            
        wizard.config_data['atc'] = {
            'type': atc_type,
            'tool_pockets': self.tool_pockets_spin.value()
        }
        return True


class SummaryPage(QWizardPage):
    """Summary and generation page"""
    
    def __init__(self):
        super(SummaryPage, self).__init__()
        
        self.setTitle("Summary")
        self.setSubTitle("Review configuration and generate files")
        
        layout = QVBoxLayout(self)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
    def initializePage(self):
        """Initialize page with summary"""
        wizard = self.wizard()
        config = wizard.config_data
        
        summary = []
        summary.append("Configuration Summary:")
        summary.append("=" * 50)
        summary.append(f"Machine Name: {config.get('machine_name', 'Unknown')}")
        summary.append(f"Machine Type: {config.get('machine_type', 'mill')}")
        summary.append(f"Units: {config.get('units', 'inch')}")
        summary.append("")
        
        # Axes
        axes = config.get('axes', {})
        enabled_axes = [axis for axis, enabled in axes.items() if enabled]
        summary.append(f"Axes: {', '.join(enabled_axes).upper()}")
        
        # Travel limits
        limits = config.get('travel_limits', {})
        summary.append(f"Travel: X={limits.get('x', 0)}, Y={limits.get('y', 0)}, Z={limits.get('z', 0)}")
        summary.append("")
        
        # Spindle
        spindle = config.get('spindle', {})
        summary.append(f"Spindle: {spindle.get('type', 'manual')} ({spindle.get('min_rpm', 100)}-{spindle.get('max_rpm', 3000)} RPM)")
        summary.append("")
        
        # Features
        features = []
        if config.get('switches', {}).get('home_switches'):
            features.append("Home switches")
        if config.get('switches', {}).get('limit_switches'):
            features.append("Limit switches")
        if config.get('probe', {}).get('enabled'):
            features.append("Touch probe")
        if config.get('coolant', {}).get('mist'):
            features.append("Mist coolant")
        if config.get('coolant', {}).get('flood'):
            features.append("Flood coolant")
            
        atc_type = config.get('atc', {}).get('type', 'none')
        if atc_type != 'none':
            features.append(f"{atc_type.title()} ATC")
            
        if features:
            summary.append(f"Features: {', '.join(features)}")
        
        self.summary_text.setPlainText("\n".join(summary))
        
    def validatePage(self):
        """Generate configuration files"""
        wizard = self.wizard()
        # TODO: Implement file generation
        LOG.info("Would generate configuration files here")
        return True