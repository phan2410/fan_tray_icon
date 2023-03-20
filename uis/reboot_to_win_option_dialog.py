from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QSizePolicy, QPushButton, QLabel, QMessageBox

from utils import run_shell_command, notify_info, notify_error, is_sudo, confirm_okcancel


class RebootToWinOptionDialog(object):

    def _schedule_reboot_to_win(self):
        return run_shell_command(
            cmd='grub-reboot "Windows 10 (on /dev/sda1)"',
            sudo_password=self.sudo_password
        )

    def _schedule_reboot_to_ubuntu(self):
        return run_shell_command(
            cmd='grub-reboot "Ubuntu"',
            sudo_password=self.sudo_password
        )

    def __init__(self, sudo_password, **kwargs):
        if kwargs.pop('check', True):
            assert is_sudo(sudo_password), "Wrong sudo_password"

        self.sudo_password = sudo_password

        self.dialog = dialog = QDialog(kwargs.pop('parent', None))
        dialog.setWindowFlags(Qt.SubWindow | Qt.Popup | Qt.WA_DeleteOnClose)
        dialog.setObjectName(self.__class__.__name__)
        dialog.resize(382, 95)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(dialog.sizePolicy().hasHeightForWidth())
        dialog.setSizePolicy(size_policy)
        dialog.setAccessibleName("")
        dialog.setSizeGripEnabled(False)
        dialog.setModal(False)
        dialog.setWindowTitle("Restart To Windows 10")

        self.label = label = QLabel(dialog)
        label.setGeometry(QtCore.QRect(20, 20, 291, 17))
        label.setObjectName("label")
        label.setText("Ready To Windows 10?")
        
        self.restart_now_button = restart_now_button = QPushButton(dialog)
        restart_now_button.setGeometry(QtCore.QRect(20, 50, 101, 25))
        restart_now_button.setObjectName("restart_now_button")
        restart_now_button.setText("Restart Now")
        restart_now_button.setToolTip("WARNING: Save all current works before clicking this button!")
        restart_now_button.clicked.connect(self._restart_now_handler)
        restart_now_button.clicked.connect(dialog.close)

        self.restart_later_button = restart_later_button = QPushButton(dialog)
        restart_later_button.setGeometry(QtCore.QRect(140, 50, 101, 25))
        restart_later_button.setObjectName("restart_later_button")
        restart_later_button.setText("Restart Later")
        restart_later_button.setToolTip("The computer will get to Windows 10 on the next start.")
        restart_later_button.clicked.connect(self._restart_later_handler)
        restart_later_button.clicked.connect(dialog.close)

        self.cancel_button = cancel_button = QPushButton(dialog)
        cancel_button.setGeometry(QtCore.QRect(260, 50, 101, 25))
        cancel_button.setObjectName("cancel_button")
        cancel_button.setText("Cancel")
        cancel_button.clicked.connect(self._cancel_restart)
        cancel_button.clicked.connect(dialog.close)

    def exec_(self):
        return self.dialog.exec_()

    def _restart_now_handler(self):
        if self._schedule_reboot_to_win().returncode == 0:
            _choice = confirm_okcancel(
                icon=QMessageBox.Icon.Warning,
                title="Confirmation Required",
                message="Please save your current works before continuing to restart the system !!!",
                button_to_text={QMessageBox.Ok: "Continue"}
            )

            if _choice == QMessageBox.Ok:
                run_shell_command(
                    cmd='reboot now',
                    sudo_password=self.sudo_password
                )
            else:
                self._schedule_reboot_to_ubuntu()
        else:
            notify_error()

    def _restart_later_handler(self):
        if self._schedule_reboot_to_win().returncode == 0:
            notify_info(
                message="You can continue working. The system will run Windows 10 on the next start "
                        "after you shutdown or restart it.",
                title="Schedule Success"
            )
        else:
            notify_error()

    def _cancel_restart(self):
        if self._schedule_reboot_to_ubuntu().returncode != 0:
            notify_error()


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication

    app = QApplication(sys.argv)
    _dialog = RebootToWinOptionDialog(
        sudo_password='wrong_pass',
        check=False
    )
    _dialog.dialog.finished.connect(sys.exit)
    _dialog.exec_()
