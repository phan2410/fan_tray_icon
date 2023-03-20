import subprocess

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QInputDialog, QWidget, QApplication, QLineEdit, QMessageBox


def run_shell_command(cmd, sudo_password=None):
    assert cmd is not None, "Invalid cmd argument!"
    params = dict(
        args=cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    if sudo_password and isinstance(sudo_password, str):
        params['args'] = f'echo "{sudo_password}" | sudo -S {cmd}'

    return subprocess.run(**params)


def is_sudo(passwd):
    res = run_shell_command('ls /root', sudo_password=passwd)
    return res.returncode == 0


def ask_for_password(message="Password?", parent=None):
    pw, ok = QInputDialog.getText(parent, "Authentication Required",
                                  message,
                                  QLineEdit.Password,
                                  flags=Qt.SubWindow | Qt.Popup | Qt.WA_DeleteOnClose)
    if ok and pw:
        return pw


def center_widget(target: QWidget, parent: QWidget = None):
    if parent is None:
        parent = target.parent()

    if parent:
        parent_rect = parent.geometry()
        target.move(parent_rect.center() - target.rect().center())
    else:
        screen_size = QApplication.primaryScreen().size()
        target.move(
            int((screen_size.width() - target.width()) / 2),         # x
            int((screen_size.height() - target.height()) / 2)        # y
        )


def notify(message, title, icon):
    msg_box = QMessageBox(
        icon,
        title,
        message,
        buttons=QMessageBox.Ok,
        flags=Qt.SubWindow | Qt.Popup | Qt.WA_DeleteOnClose
    )
    msg_box.setEscapeButton(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    return msg_box.exec_()


def notify_info(message, title='Notification'):
    return notify(message, title=title, icon=QMessageBox.Icon.Information)


def notify_error(message='Unknown failure. Please contact the developer !!!', title='Error'):
    return notify(message, title=title, icon=QMessageBox.Icon.Critical)


def confirm_okcancel(
    message="Are you sure?",
    title="Confirmation Required",
    icon=QMessageBox.Icon.Question,
    button_to_text=None
):
    msg_box = QMessageBox(
        icon,
        title,
        message,
        buttons=QMessageBox.Ok | QMessageBox.Cancel,
        flags=Qt.SubWindow | Qt.Popup | Qt.WA_DeleteOnClose
    )
    msg_box.setEscapeButton(QMessageBox.Cancel)
    msg_box.setDefaultButton(QMessageBox.Cancel)

    if isinstance(button_to_text, dict):
        for btn, txt in button_to_text.items():
            msg_box.setButtonText(btn, txt)

    return msg_box.exec_()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    choice = notify_error()
    print(choice)
    sys.exit()
