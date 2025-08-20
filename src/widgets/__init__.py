from qtpyvcp.widgets.qtdesigner import _DesignerPlugin

from widgets.lathe_tool_touch_off.lathe_tool_touch_off import LatheToolTouchOff
from widgets.atc_widget.atc import DynATC
from widgets.rack_atc_widget.rack_atc import RackATC

from widgets.conversational.facing import FacingWidget
from widgets.conversational.xy_coord import XYCoordWidget
from widgets.conversational.hole_circle import HoleCircleWidget
from widgets.conversational.int_line_edit import IntLineEdit
from widgets.conversational.float_line_edit import FloatLineEdit

# Import Phase 1 Dashboard widgets
from widgets.modal_group_hud.modal_group_hud import ModalGroupHUD
from widgets.status_tiles.status_tiles import StatusTiles
from widgets.cycle_control_panel.cycle_control_panel import CycleControlPanel
from widgets.alarms_panel.alarms_panel import AlarmsPanel
from widgets.tool_info_panel.tool_info_panel import ToolInfoPanel

# Import Phase 3 widgets
from widgets.io_panel.io_panel import IOPanel
from widgets.jog_panel.jog_panel import JogPanel
from widgets.diagnostics_panel.diagnostics_panel import DiagnosticsPanel



class LatheToolTouchOff_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return LatheToolTouchOff


class DynATC_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return DynATC
    
class RackATC_Plugin(_DesignerPlugin):
    def pluginClass(self):
        return RackATC


class FloatLineEditPlugin(_DesignerPlugin):
    def pluginClass(self):
        return FloatLineEdit


class IntLineEditPlugin(_DesignerPlugin):
    def pluginClass(self):
        return IntLineEdit


class HoleCircleWidgetPlugin(_DesignerPlugin):
    def pluginClass(self):
        return HoleCircleWidget


class XYCoordWidgetPlugin(_DesignerPlugin):
    def pluginClass(self):
        return XYCoordWidget


class FacingWidgetPlugin(_DesignerPlugin):
    def pluginClass(self):
        return FacingWidget


# Phase 1 Dashboard Widget Plugins
class ModalGroupHUDPlugin(_DesignerPlugin):
    def pluginClass(self):
        return ModalGroupHUD


class StatusTilesPlugin(_DesignerPlugin):
    def pluginClass(self):
        return StatusTiles


class CycleControlPanelPlugin(_DesignerPlugin):
    def pluginClass(self):
        return CycleControlPanel


class AlarmsPanelPlugin(_DesignerPlugin):
    def pluginClass(self):
        return AlarmsPanel


class ToolInfoPanelPlugin(_DesignerPlugin):
    def pluginClass(self):
        return ToolInfoPanel


# Phase 3 Widget Plugins
class IOPanelPlugin(_DesignerPlugin):
    def pluginClass(self):
        return IOPanel


class JogPanelPlugin(_DesignerPlugin):
    def pluginClass(self):
        return JogPanel


class DiagnosticsPanelPlugin(_DesignerPlugin):
    def pluginClass(self):
        return DiagnosticsPanel
