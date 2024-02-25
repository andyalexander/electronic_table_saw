import sys
import os
import linuxcnc

from PyQt5 import QtCore, QtWidgets

from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.widgets.gcode_editor import GcodeEditor as GCODE
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action

from functools import partial

# Set up logging
from qtvcp import logger
LOG = logger.getLogger(__name__)

# Set the log level for this module
LOG.setLevel(logger.INFO) # One of DEBUG, INFO, WARNING, ERROR, CRITICAL

###########################################
# **** INSTANTIATE LIBRARIES SECTION **** #
###########################################

KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()
###################################
# **** HANDLER CLASS SECTION **** #
###################################

class HandlerClass:

    ########################
    # **** INITIALIZE **** #
    ########################
    # widgets allows access to  widgets from the QtVCP files
    # at this point the widgets and hal pins are not instantiated
    def __init__(self, halcomp,widgets,paths):
        self.hal = halcomp
        self.w = widgets
        self.PATHS = paths

    ##########################################
    # SPECIAL FUNCTIONS SECTION              #
    ##########################################

    # at this point:
    # the widgets are instantiated.
    # the HAL pins are built but HAL is not set ready
    # This is where you make HAL pins or initialize state of widgets etc
    def initialized__(self):
        for but_name in ['0','1','2','3','4','5','6','7','8','9','dot','clear']:
            but = getattr(self.w, f'but_num_{but_name}')
            but.clicked.connect(partial(self.calc_button_handler, but_name))
        # pass

    def fence_move_to(self):
        print("move")

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)

    @QtCore.pyqtSlot(str)
    def calc_button_handler(self, text):
        txt = self.w.txt_fence_calc.text()
        if text == 'clear':
            txt = ''
        elif text == 'dot':
            if '.' not in txt:
                txt = f'{txt}.'
        else:
            if txt == '0':
                txt = text
            else:
                txt =f'{txt}{text}'
        txt = txt.replace('..', '.')
        self.w.txt_fence_calc.setText(txt)


################################
# required handler boiler code #
################################

def get_handlers(halcomp,widgets,paths):
     return [HandlerClass(halcomp,widgets,paths)]