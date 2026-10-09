from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLineEdit, QVBoxLayout

from controllers.auth_controller import AuthController
from utils.constants import COLOUR
from utils.widget_factory import make_button, make_input, make_label

class LoginDialog(QDialog):

    def __init__(self, auth_controller: AuthController, parent=None) -> None:
        super().__init__(parent)
        self._auth = auth_controller
        self._build_ui()
        self.setWindowTitle("Clinic System \u2014 Login")
        self.setFixedSize(400, 480)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOUR["card_bg"]};
                border: 2px solid {COLOUR["border"]};
                border-radius: 12px;
            }}
        """)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(0)

        title = make_label(
            "\U0001f3e5  Clinic System", bold=True, size=18, colour=COLOUR["accent"]
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = make_label("Appointment Management", size=11, colour=COLOUR["text_dim"])
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        root.addWidget(sub)
        root.addSpacing(36)

        root.addWidget(make_label("Username", colour=COLOUR["text_dim"]))
        root.addSpacing(4)
        self._username = make_input("Enter username")
        root.addWidget(self._username)
        root.addSpacing(14)

        root.addWidget(make_label("Password", colour=COLOUR["text_dim"]))
        root.addSpacing(4)
        self._password = make_input("Enter password")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.returnPressed.connect(self._on_login)
        root.addWidget(self._password)
        root.addSpacing(28)

        self._error_lbl = make_label("", size=9, colour=COLOUR["accent3"])
        self._error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._error_lbl)
        root.addSpacing(8)

        login_btn = make_button("  Sign In  ", COLOUR["accent"], "#FFFFFF")
        login_btn.setFixedHeight(44)
        login_btn.clicked.connect(self._on_login)
        root.addWidget(login_btn)
        root.addStretch()

        hint = make_label(
            "Default credentials: admin / admin123", size=9, colour=COLOUR["text_dim"]
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

    def _on_login(self) -> None:
        success, message = self._auth.login(
            self._username.text(), self._password.text()
        )
        if success:
            self.accept()
        else:
            self._error_lbl.setText(f"\u2717  {message}")
            self._password.clear()
            self._password.setFocus()
