"""
Rectangular Pocket Conversational Widget  
Phase 6: Enhanced conversational operations
"""

from qtpyvcp.ops.pocket_ops import RectangularPocketOps
from .base_widget import ConversationalBaseWidget

class RectangularPocketWidget(ConversationalBaseWidget):
    def __init__(self, parent=None):
        super(RectangularPocketWidget, self).__init__(parent, 'rectangular_pocket.ui')

        # Connect validators
        self.length_input.editingFinished.connect(self._validate_dimensions)
        self.width_input.editingFinished.connect(self._validate_dimensions)
        self.step_down_input.editingFinished.connect(self._validate_step_down)
        self.step_over_input.editingFinished.connect(self._validate_step_over)
        self.center_x_input.editingFinished.connect(self._validate_center)
        self.center_y_input.editingFinished.connect(self._validate_center)

        self._validators.extend([self._validate_dimensions,
                                 self._validate_step_down,
                                 self._validate_step_over,
                                 self._validate_center])

    def length(self):
        return self.length_input.value()

    def width(self):
        return self.width_input.value()

    def step_down(self):
        return self.step_down_input.value()

    def step_over(self):
        return self.step_over_input.value()

    def center_x(self):
        return self.center_x_input.value()

    def center_y(self):
        return self.center_y_input.value()

    def create_op(self):
        p = RectangularPocketOps()
        self._set_common_fields(p)

        p.tool_diameter = self.tool_diameter()
        p.center_x = self.center_x()
        p.center_y = self.center_y()
        p.length = self.length()
        p.width = self.width()

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

        return p.rectangular_pocket()

    def _validate_dimensions(self):
        tool_dia = self.tool_diameter()
        length_ok = self.length() > tool_dia
        width_ok = self.width() > tool_dia
        
        if length_ok and width_ok:
            self.length_input.setStyleSheet('')
            self.width_input.setStyleSheet('')
            return True, None
        else:
            if not length_ok:
                self.length_input.setStyleSheet('background-color: rgb(205, 141, 123)')
                error = 'Pocket length must be greater than tool diameter.'
                self.length_input.setToolTip(error)
            if not width_ok:
                self.width_input.setStyleSheet('background-color: rgb(205, 141, 123)')
                error = 'Pocket width must be greater than tool diameter.'
                self.width_input.setToolTip(error)
            return False, 'Pocket dimensions must be greater than tool diameter.'

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