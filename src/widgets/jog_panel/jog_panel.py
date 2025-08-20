#!/usr/bin/env python

import os
import math
from qtpy.QtCore import Qt, QTimer, Signal, QPointF
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QFrame, QPushButton, QComboBox, QSlider,
                            QGroupBox, QButtonGroup, QRadioButton, QSpinBox)
from qtpy.QtGui import QFont, QPalette, QPainter, QBrush, QPen, QColor
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger
from qtpyvcp import actions

LOG = logger.getLogger(__name__)

class MPGWheel(QWidget):
    """
    On-screen MPG (Manual Pulse Generator) wheel widget
    Provides visual feedback and mouse/touch interaction for manual jogging
    """
    
    position_changed = Signal(float)  # Emitted when wheel position changes
    
    def __init__(self, parent=None):
        super(MPGWheel, self).__init__(parent)
        
        self.setMinimumSize(150, 150)
        self.setMaximumSize(200, 200)
        
        # Wheel state
        self.wheel_position = 0.0  # Current position in degrees
        self.last_mouse_angle = 0.0
        self.is_dragging = False
        self.acceleration = 1.0
        self.counts_per_detent = 4  # Configurable
        
        # Visual properties
        self.wheel_radius = 60
        self.center_radius = 20
        
    def paintEvent(self, event):
        """Paint the MPG wheel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get center point
        center = QPointF(self.width() / 2, self.height() / 2)
        
        # Draw outer wheel
        painter.setBrush(QBrush(QColor(70, 70, 70)))
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawEllipse(center, self.wheel_radius, self.wheel_radius)
        
        # Draw detent marks
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        detent_count = 24  # Number of detent marks
        for i in range(detent_count):
            angle = (2 * math.pi * i / detent_count) + math.radians(self.wheel_position)
            outer_x = center.x() + (self.wheel_radius - 5) * math.cos(angle)
            outer_y = center.y() + (self.wheel_radius - 5) * math.sin(angle)
            inner_x = center.x() + (self.wheel_radius - 15) * math.cos(angle)
            inner_y = center.y() + (self.wheel_radius - 15) * math.sin(angle)
            painter.drawLine(outer_x, outer_y, inner_x, inner_y)
        
        # Draw center hub
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(QPen(QColor(180, 180, 180), 2))
        painter.drawEllipse(center, self.center_radius, self.center_radius)
        
        # Draw position indicator
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        angle = math.radians(self.wheel_position)
        indicator_x = center.x() + (self.wheel_radius - 25) * math.cos(angle)
        indicator_y = center.y() + (self.wheel_radius - 25) * math.sin(angle)
        painter.drawEllipse(QPointF(indicator_x, indicator_y), 5, 5)
        
    def mousePressEvent(self, event):
        """Handle mouse press for wheel interaction"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            center = QPointF(self.width() / 2, self.height() / 2)
            self.last_mouse_angle = math.atan2(event.y() - center.y(), event.x() - center.x())
            
    def mouseMoveEvent(self, event):
        """Handle mouse movement for wheel rotation"""
        if self.is_dragging:
            center = QPointF(self.width() / 2, self.height() / 2)
            current_angle = math.atan2(event.y() - center.y(), event.x() - center.x())
            
            # Calculate angle difference
            angle_diff = current_angle - self.last_mouse_angle
            
            # Handle wrap-around
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Update wheel position
            self.wheel_position += math.degrees(angle_diff) * self.acceleration
            self.last_mouse_angle = current_angle
            
            # Emit position change
            self.position_changed.emit(angle_diff)
            
            self.update()  # Repaint
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False


class JogPanel(QWidget):
    """
    Jog Panel Widget for Phase 3
    Comprehensive jogging interface with axis selector, increments, and MPG wheel
    """
    
    def __init__(self, parent=None):
        super(JogPanel, self).__init__(parent)
        
        self.status = getPlugin('status')
        if self.status is None:
            LOG.error("Could not get Status plugin")
            return
            
        self.setupUI()
        self.connectSignals()
        
        # Jog state
        self.selected_axis = 'X'
        self.jog_increment = 1.0  # Current jog increment
        self.continuous_mode = False
        self.jog_speed = 100.0  # mm/min or in/min
        self.is_jogging = False
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateStatus)
        self.update_timer.start(100)
        
    def setupUI(self):
        """Set up the user interface"""
        self.setObjectName("jogPanel")
        self.setMinimumSize(600, 400)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("Jog Panel - Manual Axis Control")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        main_layout.addWidget(header)
        
        # Top section: Axis selection and increment controls
        control_layout = QHBoxLayout()
        
        # Axis selection
        axis_group = self.createAxisSelectionGroup()
        control_layout.addWidget(axis_group)
        
        # Increment selection
        increment_group = self.createIncrementGroup()
        control_layout.addWidget(increment_group)
        
        # Speed control
        speed_group = self.createSpeedGroup()
        control_layout.addWidget(speed_group)
        
        main_layout.addLayout(control_layout)
        
        # Middle section: Jog buttons and MPG wheel
        jog_layout = QHBoxLayout()
        
        # Jog buttons
        buttons_group = self.createJogButtons()
        jog_layout.addWidget(buttons_group)
        
        # MPG wheel
        mpg_group = self.createMPGGroup()
        jog_layout.addWidget(mpg_group)
        
        main_layout.addLayout(jog_layout)
        
        # Status section
        status_group = self.createStatusGroup()
        main_layout.addWidget(status_group)
        
        self.setLayout(main_layout)
        
    def createAxisSelectionGroup(self):
        """Create axis selection controls"""
        group = QGroupBox("Axis Selection")
        layout = QVBoxLayout()
        
        # Axis radio buttons
        self.axis_button_group = QButtonGroup()
        
        axes = ['X', 'Y', 'Z']
        for i, axis in enumerate(axes):
            radio = QRadioButton(f"{axis} Axis")
            radio.setObjectName(f"axis_{axis.lower()}")
            if axis == 'X':
                radio.setChecked(True)  # Default to X axis
            radio.toggled.connect(lambda checked, a=axis: self.setSelectedAxis(a) if checked else None)
            self.axis_button_group.addButton(radio, i)
            layout.addWidget(radio)
            
        group.setLayout(layout)
        return group
        
    def createIncrementGroup(self):
        """Create increment selection controls"""
        group = QGroupBox("Jog Increment")
        layout = QVBoxLayout()
        
        # Increment radio buttons
        self.increment_button_group = QButtonGroup()
        
        increments = [
            ('continuous', 'Continuous'),
            (1.0, '1.0'),
            (0.1, '0.1'),
            (0.01, '0.01'),
            (0.001, '0.001')
        ]
        
        for i, (value, label) in enumerate(increments):
            radio = QRadioButton(label)
            if value == 1.0:
                radio.setChecked(True)  # Default to 1.0
            radio.toggled.connect(lambda checked, v=value: self.setJogIncrement(v) if checked else None)
            self.increment_button_group.addButton(radio, i)
            layout.addWidget(radio)
            
        group.setLayout(layout)
        return group
        
    def createSpeedGroup(self):
        """Create speed control"""
        group = QGroupBox("Jog Speed")
        layout = QVBoxLayout()
        
        # Speed slider
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(1000)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.setJogSpeed)
        layout.addWidget(self.speed_slider)
        
        # Speed label
        self.speed_label = QLabel("100 mm/min")
        self.speed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.speed_label)
        
        group.setLayout(layout)
        return group
        
    def createJogButtons(self):
        """Create jog button controls"""
        group = QGroupBox("Jog Controls")
        layout = QGridLayout()
        
        # Create jog buttons for each axis
        self.jog_buttons = {}
        
        # X axis buttons
        self.addJogButton(layout, 'X', '+', 1, 2)
        self.addJogButton(layout, 'X', '-', 1, 0)
        
        # Y axis buttons  
        self.addJogButton(layout, 'Y', '+', 0, 1)
        self.addJogButton(layout, 'Y', '-', 2, 1)
        
        # Z axis buttons
        self.addJogButton(layout, 'Z', '+', 3, 1)
        self.addJogButton(layout, 'Z', '-', 4, 1)
        
        # Center label
        center_label = QLabel("JOG")
        center_label.setAlignment(Qt.AlignCenter)
        center_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(center_label, 1, 1)
        
        group.setLayout(layout)
        return group
        
    def addJogButton(self, layout, axis, direction, row, col):
        """Add a jog button"""
        label = f"{axis}{direction}"
        btn = QPushButton(label)
        btn.setMinimumSize(60, 40)
        btn.setMaximumSize(80, 50)
        
        # Style the button
        if direction == '+':
            btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        else:
            btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
            
        # Connect button events
        btn.pressed.connect(lambda a=axis, d=direction: self.startJog(a, d))
        btn.released.connect(self.stopJog)
        
        self.jog_buttons[f"{axis}{direction}"] = btn
        layout.addWidget(btn, row, col)
        
    def createMPGGroup(self):
        """Create MPG wheel group"""
        group = QGroupBox("Manual Pulse Generator (MPG)")
        layout = QVBoxLayout()
        
        # MPG wheel
        self.mpg_wheel = MPGWheel()
        self.mpg_wheel.position_changed.connect(self.handleMPGRotation)
        layout.addWidget(self.mpg_wheel)
        
        # MPG controls
        mpg_controls = QHBoxLayout()
        
        # Counts per detent
        detent_label = QLabel("Counts/Detent:")
        self.detent_spinbox = QSpinBox()
        self.detent_spinbox.setMinimum(1)
        self.detent_spinbox.setMaximum(100)
        self.detent_spinbox.setValue(4)
        self.detent_spinbox.valueChanged.connect(self.setCountsPerDetent)
        
        mpg_controls.addWidget(detent_label)
        mpg_controls.addWidget(self.detent_spinbox)
        mpg_controls.addStretch()
        
        layout.addLayout(mpg_controls)
        
        group.setLayout(layout)
        return group
        
    def createStatusGroup(self):
        """Create status display"""
        group = QGroupBox("Status")
        layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.axis_label = QLabel("Axis: X")
        self.increment_label = QLabel("Increment: 1.0")
        self.speed_display = QLabel("Speed: 100 mm/min")
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.axis_label)
        layout.addWidget(self.increment_label)
        layout.addWidget(self.speed_display)
        
        group.setLayout(layout)
        return group
        
    def connectSignals(self):
        """Connect to status signals"""
        if self.status:
            self.status.enabled.notify(self.updateStatus)
            self.status.homed.notify(self.updateStatus)
            
    def setSelectedAxis(self, axis):
        """Set the selected axis for jogging"""
        self.selected_axis = axis
        self.axis_label.setText(f"Axis: {axis}")
        LOG.info(f"Selected axis: {axis}")
        
    def setJogIncrement(self, increment):
        """Set the jog increment"""
        self.jog_increment = increment
        self.continuous_mode = (increment == 'continuous')
        
        if self.continuous_mode:
            self.increment_label.setText("Increment: Continuous")
        else:
            self.increment_label.setText(f"Increment: {increment}")
            
        LOG.info(f"Jog increment set to: {increment}")
        
    def setJogSpeed(self, speed):
        """Set the jog speed"""
        self.jog_speed = speed
        self.speed_label.setText(f"{speed} mm/min")
        self.speed_display.setText(f"Speed: {speed} mm/min")
        
    def setCountsPerDetent(self, counts):
        """Set counts per detent for MPG"""
        self.mpg_wheel.counts_per_detent = counts
        LOG.info(f"MPG counts per detent: {counts}")
        
    def startJog(self, axis, direction):
        """Start jogging an axis"""
        if not self.status:
            return
            
        try:
            # Check if machine is ready for jogging
            if not self.status.enabled() or self.status.estop():
                LOG.warning("Cannot jog - machine not enabled or in ESTOP")
                return
                
            # Check if axis is homed (if required)
            homed_status = self.status.homed()
            axis_index = ord(axis) - ord('X')  # Convert to index (X=0, Y=1, Z=2)
            
            if axis_index < len(homed_status) and not homed_status[axis_index]:
                LOG.warning(f"Cannot jog {axis} axis - not homed")
                return
                
            self.is_jogging = True
            self.status_label.setText(f"Jogging {axis}{direction}")
            
            # Perform the jog operation
            if self.continuous_mode:
                # Start continuous jog
                jog_speed = self.jog_speed / 60.0  # Convert to mm/sec
                if direction == '-':
                    jog_speed = -jog_speed
                    
                # Use QtPyVCP actions for jogging
                if axis == 'X':
                    actions.machine.jog.axis.x(jog_speed)
                elif axis == 'Y':
                    actions.machine.jog.axis.y(jog_speed)
                elif axis == 'Z':
                    actions.machine.jog.axis.z(jog_speed)
            else:
                # Incremental jog
                jog_distance = self.jog_increment
                if direction == '-':
                    jog_distance = -jog_distance
                    
                # Use QtPyVCP actions for incremental jogging
                if axis == 'X':
                    actions.machine.jog.axis.x(jog_distance, self.jog_speed)
                elif axis == 'Y':
                    actions.machine.jog.axis.y(jog_distance, self.jog_speed)
                elif axis == 'Z':
                    actions.machine.jog.axis.z(jog_distance, self.jog_speed)
                    
        except Exception as e:
            LOG.error(f"Error starting jog: {e}")
            
    def stopJog(self):
        """Stop jogging"""
        if self.is_jogging and self.continuous_mode:
            try:
                # Stop continuous jog
                actions.machine.jog.stop()
                self.status_label.setText("Ready")
                self.is_jogging = False
            except Exception as e:
                LOG.error(f"Error stopping jog: {e}")
                
    def handleMPGRotation(self, angle_diff):
        """Handle MPG wheel rotation"""
        if not self.status or not self.status.enabled():
            return
            
        try:
            # Convert angle to incremental movement
            # Typical MPG: 100 counts per revolution, with configurable detents
            counts_per_revolution = 100
            movement_per_count = self.jog_increment / self.mpg_wheel.counts_per_detent
            
            # Calculate movement distance
            angle_fraction = angle_diff / (2 * math.pi)  # Fraction of full rotation
            distance = angle_fraction * counts_per_revolution * movement_per_count
            
            if abs(distance) > 0.001:  # Minimum movement threshold
                # Perform incremental jog on selected axis
                if self.selected_axis == 'X':
                    actions.machine.jog.axis.x(distance, self.jog_speed)
                elif self.selected_axis == 'Y':
                    actions.machine.jog.axis.y(distance, self.jog_speed)
                elif self.selected_axis == 'Z':
                    actions.machine.jog.axis.z(distance, self.jog_speed)
                    
                LOG.debug(f"MPG jog {self.selected_axis}: {distance:.4f}")
                
        except Exception as e:
            LOG.error(f"Error handling MPG rotation: {e}")
            
    def updateStatus(self):
        """Update status display"""
        if not self.status:
            return
            
        try:
            # Update button states based on machine status
            enabled = self.status.enabled() and not self.status.estop()
            
            for btn in self.jog_buttons.values():
                btn.setEnabled(enabled)
                
            # Update status text
            if not enabled:
                if self.status.estop():
                    self.status_label.setText("ESTOP Active - Jogging Disabled")
                else:
                    self.status_label.setText("Machine Disabled - Jogging Disabled")
            elif not self.is_jogging:
                self.status_label.setText("Ready")
                
        except Exception as e:
            LOG.error(f"Error updating jog panel status: {e}")