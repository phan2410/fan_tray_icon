import os
import sys
from functools import partial

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QAction

from uis.reboot_to_win_option_dialog import RebootToWinOptionDialog
from utils import run_shell_command, is_sudo, center_widget, ask_for_password, notify_error

OS_NAME = os.uname().sysname.lower()
PARENT_DIR = os.path.dirname(__file__)
ICON_DIR = os.path.join(PARENT_DIR, "icons")


class FanTrayIcon(QSystemTrayIcon):
    def __init__(self, *args, **kwargs):
        QSystemTrayIcon.__init__(self, *args, **kwargs)
        self.setToolTip('Utilities by FanBear')
        menu = QMenu(parent=self.parent())

        if OS_NAME == 'linux':

            self._is_2nd_screen_activated = None
            self._action_toggle_2nd_screen = toggle_2nd_screen = QAction(
                icon=QIcon(os.path.join(ICON_DIR, "toggle_2nd_monitor_icon.png")),
                text="Toggle 2nd Screen"
            )
            toggle_2nd_screen.triggered.connect(self._toggle_2nd_screen)
            menu.addAction(toggle_2nd_screen)

        _system_menu = QMenu(title="System")

        if OS_NAME == 'linux':

            reboot_to_win = _system_menu.addAction("Restart To Windows 10")
            reboot_to_win.setIcon(QIcon(os.path.join(ICON_DIR, "win10_logo.png")))
            reboot_to_win.triggered.connect(self._reboot_to_win)

            hibernate = _system_menu.addAction("Hibernate")
            hibernate.setIcon(QIcon(os.path.join(ICON_DIR, "hibernate_icon.png")))
            hibernate.triggered.connect(
                partial(run_shell_command, 'xdg-screensaver lock && systemctl hibernate')
            )

        if len(_system_menu.children()) > 1:
            menu.addMenu(_system_menu)

        menu.addSeparator()

        _quit = menu.addAction("Quit")
        _quit.triggered.connect(sys.exit)

        self.setContextMenu(menu)

    @staticmethod
    def _turn_off_2nd_screen():
        return run_shell_command('xrandr --output HDMI-0 --off')

    @staticmethod
    def _turn_on_2nd_screen():
        return run_shell_command('xrandr --output HDMI-0 --pos 1920x-370 --rotate right --mode 1920x1080')

    def _toggle_2nd_screen(self):
        if self._is_2nd_screen_activated:
            ret_code = self._turn_off_2nd_screen().returncode
            self._is_2nd_screen_activated = False
            self._action_toggle_2nd_screen.setText("Enable 2nd Screen")
        else:
            ret_code = 0
            if self._is_2nd_screen_activated is None:
                ret_code = self._turn_off_2nd_screen().returncode
            ret_code += self._turn_on_2nd_screen().returncode
            self._is_2nd_screen_activated = True
            self._action_toggle_2nd_screen.setText("Disable 2nd Screen")

        if ret_code != 0:
            notify_error()

    @staticmethod
    def _reboot_to_win():
        assert OS_NAME == 'linux', 'Invalid OS'

        ask_for_password_message = "To restart into Windows 10, please enter sudo password:"
        while True:
            pw = ask_for_password(message=ask_for_password_message)
            if pw is None:
                return
            if is_sudo(pw):
                break
            else:
                ask_for_password_message = "Wrong sudo password. Please enter again:"

        _dialog = RebootToWinOptionDialog(sudo_password=pw, check=False)
        _dialog.exec_()


def main():
    app = QApplication(sys.argv)
    w = QWidget()
    center_widget(w)
    tray_icon = FanTrayIcon(
        icon=QIcon(os.path.join(ICON_DIR, "main.png")),
        parent=w
    )
    tray_icon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
