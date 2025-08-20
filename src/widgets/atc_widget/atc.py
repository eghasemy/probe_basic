import os

import linuxcnc

# Workarround for nvidia propietary drivers

import ctypes
import ctypes.util

ctypes.CDLL(ctypes.util.find_library("GL"), mode=ctypes.RTLD_GLOBAL)

# end of Workarround

from qtpy.QtCore import Property, Slot
from qtpy.QtGui import QColor

from qtpy.QtCore import Signal, Slot, QUrl, QTimer
from qtpy.QtQuickWidgets import QQuickWidget

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)
STATUS = getPlugin('status')
TOOLTABLE = getPlugin('tooltable')
IN_DESIGNER = os.getenv('DESIGNER', False)
WIDGET_PATH = os.path.dirname(os.path.abspath(__file__))
INIFILE = linuxcnc.ini(os.getenv("INI_FILE_NAME"))

class DynATC(QQuickWidget):
    atcInitSig = Signal(int, int, arguments=['pockets', 'step_duration'])
    
    resizeSig = Signal(int, int, arguments=["width", "height"])
    
    rotateSig = Signal(int, int, arguments=['steps', 'direction'])

    showToolSig = Signal(float, float, arguments=['pocket', 'tool_num'])
    hideToolSig = Signal(float, arguments=['pocket'])

    bgColorSig = Signal(QColor, arguments=["color"])
    homeMsgSig = Signal(str, arguments=["message"])
    
    # Phase 5 - ATC State Management signals
    atcStateSig = Signal(str, arguments=["state"])  # Ready/Busy/Fault
    pocketStateSig = Signal(int, str, arguments=['pocket', 'state'])  # pocket, empty/tool#/fault
    interlockSig = Signal(bool, bool, bool, arguments=['door_closed', 'air_pressure', 'encoder_ready'])
    progressSig = Signal(str, int, arguments=['step_description', 'progress_percent'])

    def __init__(self, parent=None):
        super(DynATC, self).__init__(parent)

        # properties
        self._background_color = QColor(0, 0, 0)
        
        self.atc_position = 0
        self.pocket = 1
        self.home = 0
        self.homing = 0
        self.pocket_slots = int(INIFILE.find("ATC", "POCKETS") or 12)
        self.rotaion_duration = int(INIFILE.find("ATC", "STEP_TIME") or 1000)
        
        # Phase 5 - ATC State Management
        self.atc_state = "Ready"  # Ready, Busy, Fault
        self.pocket_states = {}  # Track individual pocket states
        self.door_closed = True
        self.air_pressure = True
        self.encoder_ready = True
        self.current_step = ""
        self.progress_percent = 0
        
        self.engine().rootContext().setContextProperty("atc_spiner", self)
        qml_path = os.path.join(WIDGET_PATH, "atc.qml")
        url = QUrl.fromLocalFile(qml_path)

        self.setSource(url)  # Fixme fails on qtdesigner

        self.tool_table = None
        self.status_tool_table = None
        self.pockets = dict()
        self.tools = None

        self.atcInitSig.emit(self.pocket_slots, self.rotaion_duration)
        
        # Initialize pocket states
        for pocket in range(1, self.pocket_slots+1):
            self.pocket_states[pocket] = "empty"
        
        if not IN_DESIGNER:
            for pocket in range(1, self.pocket_slots+1):
                self.hideToolSig.emit(pocket)
                
        # Emit initial state
        self.update_atc_state("Ready")
        self.update_interlocks(True, True, True)
     
    def resizeEvent(self, event):
        self.resizeSig.emit(self.maximumWidth(), self.maximumHeight())
        super().resizeEvent(event)

    @Property(QColor)
    def backgroundColor(self):
        return self._background_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self.bgColorSig.emit(color)
        self._background_color = color

    def load_tools(self):
        # print("load_tools")
        for i in range(1, self.pocket_slots+1):
            self.hideToolSig.emit(i)

        for pocket, tool in list(self.pockets.items()):
            if tool != 0:
                self.showToolSig.emit(pocket, tool)
            else:
                self.hideToolSig.emit(pocket)

    def store_tool(self, pocket, tool_num):
        self.pockets[pocket] = tool_num
        #
        # print(type(pocket), pocket)
        # print(type(tool_num), tool_num)
        if tool_num != 0:
            # print("show tool {} at pocket {}".format(tool_num, pocket))
            self.showToolSig.emit(pocket, tool_num)
            # Phase 5 - Update pocket state
            self.pocket_states[pocket] = f"tool{int(tool_num)}"
            self.pocketStateSig.emit(pocket, f"tool{int(tool_num)}")
        else:
            # print("Hide tool at pocket {}".format(pocket))
            self.hideToolSig.emit(pocket)
            # Phase 5 - Update pocket state
            self.pocket_states[pocket] = "empty"
            self.pocketStateSig.emit(pocket, "empty")

    def atc_message(self, msg=""):
        self.homeMsgSig.emit(msg)

    def rotate(self, steps, direction):
        if direction == "cw":
            self.rotateSig.emit(int(steps), 1)
        elif direction == "ccw":
            self.rotateSig.emit(int(steps), -1)
            
    # Phase 5 - ATC State Management methods
    def update_atc_state(self, state):
        """Update ATC state: Ready, Busy, Fault"""
        self.atc_state = state
        self.atcStateSig.emit(state)
        
    def update_pocket_state(self, pocket, state):
        """Update individual pocket state: empty, tool#, fault"""
        self.pocket_states[pocket] = state
        self.pocketStateSig.emit(pocket, state)
        
    def update_interlocks(self, door_closed, air_pressure, encoder_ready):
        """Update interlock status"""
        self.door_closed = door_closed
        self.air_pressure = air_pressure
        self.encoder_ready = encoder_ready
        self.interlockSig.emit(door_closed, air_pressure, encoder_ready)
        
    def update_progress(self, step_description, progress_percent):
        """Update tool change progress"""
        self.current_step = step_description
        self.progress_percent = progress_percent
        self.progressSig.emit(step_description, progress_percent)
        
    # Slot methods for external calls (e.g., from NGC macros via DEBUG statements)
    @Slot(str)
    def set_atc_state(self, state):
        self.update_atc_state(state)
        
    @Slot(int, str)
    def set_pocket_state(self, pocket, state):
        self.update_pocket_state(pocket, state)
        
    @Slot(bool, bool, bool)
    def set_interlocks(self, door_closed, air_pressure, encoder_ready):
        self.update_interlocks(door_closed, air_pressure, encoder_ready)
        
    @Slot(str, int)
    def set_progress(self, step_description, progress_percent):
        self.update_progress(step_description, progress_percent)
