import sys

import mysql.connector
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from controllers.appointment_controller import AppointmentController
from controllers.auth_controller import AuthController
from models import database as db
from models.data_manager import DataManager, bootstrap_schema
from utils.constants import COLOUR
from views.db_setup_dialog import DBSetupDialog
from views.login_dialog import LoginDialog
from views.main_window import MainWindow

def _apply_app_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,     QColor(COLOUR["bg_main"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLOUR["text_main"]))
    palette.setColor(QPalette.ColorRole.Base,       QColor(COLOUR["input_bg"]))
    palette.setColor(QPalette.ColorRole.Text,       QColor(COLOUR["text_main"]))
    palette.setColor(QPalette.ColorRole.Button,     QColor(COLOUR["card_bg"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLOUR["text_main"]))
    app.setPalette(palette)

def _connect_with_retry(app: QApplication) -> bool:
    while True:
        try:
            db.init_pool()
            bootstrap_schema()
            return True
        except mysql.connector.Error as exc:
            dlg = DBSetupDialog(error_message=str(exc))
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return False

def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    _apply_app_palette(app)

    if not _connect_with_retry(app):
        sys.exit(0)

    data_manager = DataManager()

    auth_ctrl  = AuthController(data_manager)
    appt_ctrl  = AppointmentController(data_manager)

    login = LoginDialog(auth_ctrl)
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    window = MainWindow(appt_ctrl)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
