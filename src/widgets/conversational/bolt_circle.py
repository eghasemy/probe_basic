"""
Bolt Circle Conversational Widget
Phase 6: Enhanced conversational operations
"""

import math
from qtpyvcp.ops.bolt_circle_ops import BoltCircleOps
from .base_widget import ConversationalBaseWidget

class BoltCircleWidget(ConversationalBaseWidget):
    def __init__(self, parent=None):
        super(BoltCircleWidget, self).__init__(parent, 'bolt_circle.ui')

        # Connect validators
        self.center_x_input.editingFinished.connect(self._validate_center)
        self.center_y_input.editingFinished.connect(self._validate_center)
        self.circle_diameter_input.editingFinished.connect(self._validate_circle_diameter)
        self.hole_diameter_input.editingFinished.connect(self._validate_hole_diameter)
        self.hole_count_input.editingFinished.connect(self._validate_hole_count)
        self.start_angle_input.editingFinished.connect(self._validate_start_angle)
        self.step_down_input.editingFinished.connect(self._validate_step_down)

        self._validators.extend([self._validate_center,
                                 self._validate_circle_diameter,
                                 self._validate_hole_diameter,
                                 self._validate_hole_count,
                                 self._validate_start_angle,
                                 self._validate_step_down])

    def center_x(self):
        return self.center_x_input.value()

    def center_y(self):
        return self.center_y_input.value()

    def circle_diameter(self):
        return self.circle_diameter_input.value()

    def hole_diameter(self):
        return self.hole_diameter_input.value()

    def hole_count(self):
        return self.hole_count_input.value()

    def start_angle(self):
        return self.start_angle_input.value()

    def step_down(self):
        return self.step_down_input.value()

    def create_op(self):
        bc = BoltCircleOps()
        self._set_common_fields(bc)

        bc.tool_diameter = self.tool_diameter()
        bc.center_x = self.center_x()
        bc.center_y = self.center_y()
        bc.circle_diameter = self.circle_diameter()
        bc.hole_diameter = self.hole_diameter()
        bc.hole_count = self.hole_count()
        bc.start_angle = self.start_angle()

        if self.step_down() == 0:
            bc.step_down = abs(self.z_end() - self.z_start())
            self.step_down_input.setText('{0:.3f}'.format(bc.step_down))
        else:
            bc.step_down = self.step_down()

        return bc.bolt_circle()

    def _validate_center(self):
        # Center validation could include workspace limits
        self.center_x_input.setStyleSheet('')
        self.center_y_input.setStyleSheet('')
        return True, None

    def _validate_circle_diameter(self):
        if self.circle_diameter() > 0:
            self.circle_diameter_input.setStyleSheet('')
            return True, None
        else:
            self.circle_diameter_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Circle diameter must be greater than 0.'
            self.circle_diameter_input.setToolTip(error)
            return False, error

    def _validate_hole_diameter(self):
        if self.hole_diameter() > self.tool_diameter():
            self.hole_diameter_input.setStyleSheet('')
            return True, None
        else:
            self.hole_diameter_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Hole diameter must be greater than tool diameter.'
            self.hole_diameter_input.setToolTip(error)
            return False, error

    def _validate_hole_count(self):
        if self.hole_count() > 0:
            self.hole_count_input.setStyleSheet('')
            return True, None
        else:
            self.hole_count_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Hole count must be greater than 0.'
            self.hole_count_input.setToolTip(error)
            return False, error

    def _validate_start_angle(self):
        if 0 <= self.start_angle() < 360:
            self.start_angle_input.setStyleSheet('')
            return True, None
        else:
            self.start_angle_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Start angle must be between 0 and 360 degrees.'
            self.start_angle_input.setToolTip(error)
            return False, error

    def _validate_step_down(self):
        if self.step_down() >= 0:
            self.step_down_input.setStyleSheet('')
            return True, None
        else:
            self.step_down_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Step down cannot be negative.'
            self.step_down_input.setToolTip(error)
            return False, error