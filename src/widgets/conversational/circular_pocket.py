"""
Circular Pocket Conversational Widget
Phase 6: Enhanced conversational operations
"""

from qtpyvcp.ops.pocket_ops import CircularPocketOps
from .base_widget import ConversationalBaseWidget

class CircularPocketWidget(ConversationalBaseWidget):
    def __init__(self, parent=None):
        super(CircularPocketWidget, self).__init__(parent, 'circular_pocket.ui')

        # Connect validators
        self.diameter_input.editingFinished.connect(self._validate_diameter)
        self.step_down_input.editingFinished.connect(self._validate_step_down)
        self.step_over_input.editingFinished.connect(self._validate_step_over)
        self.center_x_input.editingFinished.connect(self._validate_center)
        self.center_y_input.editingFinished.connect(self._validate_center)

        self._validators.extend([self._validate_diameter,
                                 self._validate_step_down,
                                 self._validate_step_over,
                                 self._validate_center])

    def diameter(self):
        return self.diameter_input.value()

    def step_down(self):
        return self.step_down_input.value()

    def step_over(self):
        return self.step_over_input.value()

    def center_x(self):
        return self.center_x_input.value()

    def center_y(self):
        return self.center_y_input.value()

    def create_op(self):
        p = CircularPocketOps()
        self._set_common_fields(p)

        p.tool_diameter = self.tool_diameter()
        p.center_x = self.center_x()
        p.center_y = self.center_y()
        p.diameter = self.diameter()

        if self.step_down() == 0:
            p.step_down = abs(self.z_end() - self.z_start())
            self.step_down_input.setText('{0:.3f}'.format(p.step_down))
        else:
            p.step_down = self.step_down()

        if self.step_over() == 0:
            p.step_over = self.tool_diameter() * 0.8
            self.step_over_input.setText('{0:.3f}'.format(p.step_over))
        else:
            p.step_over = self.step_over()

        return p.circular_pocket()

    def _validate_diameter(self):
        if self.diameter() > self.tool_diameter():
            self.diameter_input.setStyleSheet('')
            return True, None
        else:
            self.diameter_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Pocket diameter must be greater than tool diameter.'
            self.diameter_input.setToolTip(error)
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

    def _validate_step_over(self):
        if self.step_over() >= 0:
            self.step_over_input.setStyleSheet('')
            return True, None
        else:
            self.step_over_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Step over cannot be negative.'
            self.step_over_input.setToolTip(error)
            return False, error

    def _validate_center(self):
        # Center validation could include workspace limits
        self.center_x_input.setStyleSheet('')
        self.center_y_input.setStyleSheet('')
        return True, None