import subprocess
from functools import partial

from PyQt5 import QtCore
# Set up logging
from qtvcp import logger
from qtvcp.core import Status, Action
from qtvcp.lib.keybindings import Keylookup

LOG = logger.getLogger(__name__)

# Set the log level for this module
LOG.setLevel(logger.INFO)  # One of DEBUG, INFO, WARNING, ERROR, CRITICAL

KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()


class HandlerClass:

    # widgets allows access to  widgets from the QtVCP files
    # at this point the widgets and hal pins are not instantiated
    def __init__(self, halcomp, widgets, paths):
        self.hal = halcomp
        self.w = widgets
        self.PATHS = paths

    # at this point:
    # the widgets are instantiated.
    # the HAL pins are built but HAL is not set ready
    # This is where you make HAL pins or initialize state of widgets etc
    def initialized__(self):
        # define and add handlers for all the numeric buttons in calc
        for but_name in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'dot', 'clear', 'sign']:
            but = getattr(self.w, f'but_num_{but_name}')
            but.clicked.connect(partial(self.calc_button_handler, but_name))

        self.w.move_but_grid.setEnabled(False)
        self.w.jogincrements.setCurrentIndex(1)
        self.w.showMaximized()

    def send_gcode_fence(self, gcode: str, require_calculator_value: bool) -> None:
        """Send Fence gcode after substituting values"""
        calculator_val = self.w.txt_fence_calc.text()
        gcode = gcode.replace('<X>', calculator_val)

        if calculator_val or not require_calculator_value:
            ACTION.CALL_MDI(gcode)

        if require_calculator_value:
            self.fence_clear_display()

    def fence_move_to(self) -> None:
        """Move fence to specific location using abs co-ordinates"""
        self.send_gcode_fence("G00 G90 X<X>", True)

    def fence_move_by(self) -> None:
        """Move fence by specific amount.  Uses relative co-ordinates"""
        self.send_gcode_fence("G00 G91 X<X>", True)

    def fence_set_position(self) -> None:
        """Set position of fence to current value in calculator"""
        self.send_gcode_fence("G10 L20 P0 X<X>", True)

    # def fence_set_home(self) -> None:
    #     """Set machine position to current location"""
    #     self.send_gcode_fence("G10 L20 P0 X0", False)

    def fence_clear_display(self) -> None:
        self.w.txt_fence_calc.setText('0')


    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)

    @QtCore.pyqtSlot(str)
    def calc_button_handler(self, text: str) -> None:
        """
        Handle button click for calculator buttons
        Called via partial() above.
        :param text: Button text
        :return: None
        """
        txt: str = self.w.txt_fence_calc.text()
        if text == 'clear':
            txt = ''
        elif text == 'dot':
            if '.' not in txt:
                txt = f'{txt}.'
        elif text == 'sign' and txt != '0':
            if txt.startswith('-'):
                txt = txt[1:]
            else:
                txt = f"-{txt}"
        else:
            if txt == '0':
                txt = text
            else:
                txt = f'{txt}{text}'
        txt = txt.replace('..', '.')

        if txt :
            self.w.move_but_grid.setEnabled(True)
        else:
            self.w.move_but_grid.setEnabled(False)

        self.w.txt_fence_calc.setText(txt)

    def system_shutdown(self):
        subprocess.run(['xfce4-session-logout', '--halt'])

    def system_reboot(self):
        subprocess.run(['xfce4-session-logout', '--reboot'])

# required handler boiler code #
def get_handlers(halcomp, widgets, paths):
    return [HandlerClass(halcomp, widgets, paths)]
