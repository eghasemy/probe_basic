"""
Slot Conversational Widget
Phase 6: Enhanced conversational operations  
"""

from qtpyvcp.ops.slot_ops import SlotOps
from .base_widget import ConversationalBaseWidget

class SlotWidget(ConversationalBaseWidget):
    def __init__(self, parent=None):
        super(SlotWidget, self).__init__(parent, 'slot.ui')

        # Connect validators
        self.start_x_input.editingFinished.connect(self._validate_positions)
        self.start_y_input.editingFinished.connect(self._validate_positions)
        self.end_x_input.editingFinished.connect(self._validate_positions)
        self.end_y_input.editingFinished.connect(self._validate_positions)
        self.width_input.editingFinished.connect(self._validate_width)
        self.step_down_input.editingFinished.connect(self._validate_step_down)
        self.step_over_input.editingFinished.connect(self._validate_step_over)

        self._validators.extend([self._validate_positions,
                                 self._validate_width,
                                 self._validate_step_down,
                                 self._validate_step_over])

    def start_x(self):
        return self.start_x_input.value()

    def start_y(self):
        return self.start_y_input.value()

    def end_x(self):
        return self.end_x_input.value()

    def end_y(self):
        return self.end_y_input.value()

    def width(self):
        return self.width_input.value()

    def step_down(self):
        return self.step_down_input.value()

    def step_over(self):
        return self.step_over_input.value()

    def create_op(self):
        s = SlotOps()
        self._set_common_fields(s)

        s.tool_diameter = self.tool_diameter()
        s.start_x = self.start_x()
        s.start_y = self.start_y()
        s.end_x = self.end_x()
        s.end_y = self.end_y()
        s.width = self.width()

        if self.step_down() == 0:
            s.step_down = abs(self.z_end() - self.z_start())
            self.step_down_input.setText('{0:.3f}'.format(s.step_down))
        else:
            s.step_down = self.step_down()

        if self.step_over() == 0:
            s.step_over = self.tool_diameter() * 0.8
            self.step_over_input.setText('{0:.3f}'.format(s.step_over))
        else:
            s.step_over = self.step_over()

        return s.slot()

    def _validate_positions(self):
        # Check that start and end positions are different
        if (self.start_x() != self.end_x() or self.start_y() != self.end_y()):
            self.start_x_input.setStyleSheet('')
            self.start_y_input.setStyleSheet('')
            self.end_x_input.setStyleSheet('')
            self.end_y_input.setStyleSheet('')
            return True, None
        else:
            self.start_x_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            self.start_y_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            self.end_x_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            self.end_y_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Start and end positions must be different.'
            for widget in [self.start_x_input, self.start_y_input, self.end_x_input, self.end_y_input]:
                widget.setToolTip(error)
            return False, error

    def _validate_width(self):
        if self.width() > self.tool_diameter():
            self.width_input.setStyleSheet('')
            return True, None
        else:
            self.width_input.setStyleSheet('background-color: rgb(205, 141, 123)')
            error = 'Slot width must be greater than tool diameter.'
            self.width_input.setToolTip(error)
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