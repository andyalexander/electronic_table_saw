import sys
import os
import json
import re
import linuxcnc

from PyQt5 import QtCore, QtWidgets

from qtvcp.widgets.mdi_line import MDILine as MDI_WIDGET
from qtvcp.widgets.gcode_editor import GcodeEditor as GCODE
from qtvcp.lib.keybindings import Keylookup
from qtvcp.core import Status, Action

from functools import partial
import subprocess

# Set up logging
from qtvcp import logger

LOG = logger.getLogger(__name__)

# Set the log level for this module
LOG.setLevel(logger.INFO)  # One of DEBUG, INFO, WARNING, ERROR, CRITICAL

KEYBIND = Keylookup()
STATUS = Status()
ACTION = Action()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
INI_PATH = os.path.join(os.path.dirname(__file__), '..', 'esf.ini')

CONFIG_DEFAULTS = {
    'home_offset': 154.0,
    'kerf': 3.0,
    'kerf_include': False,  # False = measure to left of blade, True = include kerf (measure to right)
}


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
            # Fill in any missing keys with defaults
            for k, v in CONFIG_DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception as e:
            LOG.warning(f"Failed to load config: {e}, using defaults")
    return dict(CONFIG_DEFAULTS)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def update_ini_home_offset(value: float) -> None:
    """Update HOME_OFFSET and HOME values in esf.ini"""
    try:
        ini_path = os.path.realpath(INI_PATH)
        with open(ini_path, 'r') as f:
            text = f.read()
        text = re.sub(r'^HOME_OFFSET\s*=.*$', f'HOME_OFFSET = {value}', text, flags=re.MULTILINE)
        text = re.sub(r'^HOME\s*=.*$', f'HOME = {value}', text, flags=re.MULTILINE)
        with open(ini_path, 'w') as f:
            f.write(text)
    except Exception as e:
        LOG.error(f"Failed to update INI home offset: {e}")


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.config = dict(config)

        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        self.spin_home_offset = QtWidgets.QDoubleSpinBox()
        self.spin_home_offset.setRange(0.0, 1000.0)
        self.spin_home_offset.setDecimals(2)
        self.spin_home_offset.setSuffix(" mm")
        self.spin_home_offset.setValue(config['home_offset'])
        layout.addRow("Home offset:", self.spin_home_offset)

        self.spin_kerf = QtWidgets.QDoubleSpinBox()
        self.spin_kerf.setRange(0.0, 20.0)
        self.spin_kerf.setDecimals(2)
        self.spin_kerf.setSuffix(" mm")
        self.spin_kerf.setValue(config['kerf'])
        layout.addRow("Blade kerf:", self.spin_kerf)

        note = QtWidgets.QLabel(
            "Home offset change takes effect after next homing."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        layout.addRow(note)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setStyleSheet(
            "QDialog { background-color: #2b2b2b; color: #f0f0f0; }"
            "QLabel { color: #f0f0f0; }"
            "QDoubleSpinBox { background-color: #3c3f41; color: #f0f0f0; border: 1px solid #5a5a5a; "
            "    border-radius: 4px; padding: 4px; font-size: 14pt; }"
            "QCheckBox { color: #f0f0f0; font-size: 12pt; }"
            "QPushButton { font-size: 12pt; }"
        )
        self.resize(460, 220)

    def get_config(self) -> dict:
        return {
            'home_offset': self.spin_home_offset.value(),
            'kerf': self.spin_kerf.value(),
        }


class HandlerClass:

    # widgets allows access to  widgets from the QtVCP files
    # at this point the widgets and hal pins are not instantiated
    def __init__(self, halcomp, widgets, paths):
        self.hal = halcomp
        self.w = widgets
        self.PATHS = paths
        self.config = load_config()

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
        self.w.but_settings.clicked.connect(self.open_settings)
        self.w.chk_kerf_include.setChecked(self.config.get('kerf_include', True))
        self.w.chk_kerf_include.stateChanged.connect(self._kerf_checkbox_changed)
        self.w.showMaximized()

    def get_coord_sys(self) -> str:
        """Get the coordinate system string to use"""
        ret = 'G53'
        if self.w.rad_user_coord.isChecked():
            ret = 'G54'
        return ret

    def send_gcode_fence(self, gcode: str, require_calculator_value: bool) -> None:
        """Send Fence gcode after substituting values"""
        calculator_val = None

        if require_calculator_value:
            calculator_val = self.w.txt_fence_calc.text()
            gcode = gcode.replace('<X>', calculator_val)

        if calculator_val or not require_calculator_value:
            ACTION.CALL_MDI(gcode)

        if require_calculator_value:
            self.fence_clear_display()

    def _kerf_checkbox_changed(self) -> None:
        """Save kerf_include state when checkbox is toggled."""
        self.config['kerf_include'] = self.w.chk_kerf_include.isChecked()
        save_config(self.config)

    def _apply_kerf(self, value: float) -> float:
        """Adjust target position for kerf.
        Checked (RHS): measuring from right/far side of blade — no adjustment needed.
        Unchecked (LHS): measuring from left/near side — subtract kerf so fence lands at correct position.
        e.g. 200mm entry, 3mm kerf → fence moves to 197mm.
        """
        if not self.w.chk_kerf_include.isChecked():
            return value - self.config.get('kerf', 0.0)
        return value

    def fence_move_to(self) -> None:
        """Move fence to specific location using machine co-ordinates and absolute movement"""
        co_ord = self.get_coord_sys()
        try:
            raw = float(self.w.txt_fence_calc.text())
        except ValueError:
            return
        target = self._apply_kerf(raw)
        ACTION.CALL_MDI(f"{co_ord} G90 G0 X{target:.4f}")
        self.fence_clear_display()

    def fence_move_by(self) -> None:
        """Move fence by specific amount.  Uses relative co-ordinates"""
        self.send_gcode_fence("G91 G0 X<X>", True)

    def fence_set_position(self) -> None:
        """Set position of fence to current value in calculator using G10 L20"""
        self.send_gcode_fence("G10 L20 P1 X<X>", True)
        self.w.rad_user_coord.setChecked(True)

    def fence_set_home(self) -> None:
        """Set machine co-ordinate zero position to current location"""
        self.send_gcode_fence("G10 L20 P1 X0", False)
        self.w.rad_user_coord.setChecked(True)

    def fence_clear_display(self) -> None:
        self.w.txt_fence_calc.setText('0')

    def fence_home(self) -> None:
        ACTION.SET_MACHINE_HOMING(0)
        self.w.rad_machine_coord.setChecked(True)

    def open_settings(self) -> None:
        dlg = SettingsDialog(self.config, parent=self.w)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            new_config = dlg.get_config()
            home_offset_changed = new_config['home_offset'] != self.config.get('home_offset')
            self.config.update(new_config)
            save_config(self.config)
            if home_offset_changed:
                update_ini_home_offset(new_config['home_offset'])
                QtWidgets.QMessageBox.information(
                    self.w, "Home Offset Updated",
                    f"Home offset set to {new_config['home_offset']} mm.\n"
                    "Re-home the machine for the change to take effect."
                )

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

        if txt:
            self.w.move_but_grid.setEnabled(True)
        else:
            self.w.move_but_grid.setEnabled(False)

        self.w.txt_fence_calc.setText(txt)

    def _confirm_and_run(self, title: str, message: str, command: list) -> None:
        dlg = QtWidgets.QMessageBox(self.w)
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        dlg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        dlg.setStyleSheet(
            "QMessageBox { background-color: #2b2b2b; color: #f0f0f0; }"
            "QLabel { color: #f0f0f0; font-size: 14pt; }"
            "QPushButton { background-color: #3c3f41; color: #f0f0f0; border: 1px solid #5a5a5a;"
            "  border-radius: 4px; padding: 6px 20px; font-size: 13pt; }"
            "QPushButton:hover { background-color: #4c5052; }"
        )
        if dlg.exec_() == QtWidgets.QMessageBox.Ok:
            subprocess.run(command)

    def system_shutdown(self):
        self._confirm_and_run("Shutdown", "Shut down the machine?", ['sudo', 'shutdown', '-h', 'now'])

    def system_reboot(self):
        self._confirm_and_run("Reboot", "Reboot the machine?", ['sudo', 'reboot'])


# required handler boiler code #
def get_handlers(halcomp, widgets, paths):
    return [HandlerClass(halcomp, widgets, paths)]
