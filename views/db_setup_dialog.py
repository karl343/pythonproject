from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

import mysql.connector

from models import database as db
from utils.constants import COLOUR
from utils.widget_factory import make_button, make_input, make_label

class DBSetupDialog(QDialog):

    def __init__(self, error_message: str = "", parent=None) -> None:
        super().__init__(parent)
        self._error_message = error_message
        self._build_ui()
        self.setWindowTitle("Database Connection Setup")
        self.setFixedWidth(480)
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
        root.setContentsMargins(36, 36, 36, 36)
        root.setSpacing(0)

        title = make_label(
            "\U0001f5c4  MySQL Connection Setup",
            bold=True, size=15, colour=COLOUR["accent"],
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        root.addSpacing(8)

        if self._error_message:
            banner = QFrame()
            banner.setStyleSheet("""
                QFrame {
                    background-color: #FEE2E2;
                    border: 1px solid #DC2626;
                    border-radius: 6px;
                    padding: 6px;
                }
            """)
            bl = QVBoxLayout(banner)
            bl.setContentsMargins(10, 8, 10, 8)
            err_lbl = make_label(
                f"\u26a0  {self._error_message}", size=9, colour=COLOUR["accent3"]
            )
            err_lbl.setWordWrap(True)
            bl.addWidget(err_lbl)
            root.addSpacing(12)
            root.addWidget(banner)

        root.addSpacing(20)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        cfg = db.load_raw_config()

        self._host     = make_input("localhost")
        self._host.setText(cfg.get("host", "localhost"))

        self._port     = make_input("3306")
        self._port.setText(str(cfg.get("port", 3306)))

        self._user     = make_input("root")
        self._user.setText(cfg.get("user", "root"))

        self._password = make_input("password")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setText(cfg.get("password", ""))

        self._database = make_input("clinic_db")
        self._database.setText(cfg.get("database", "clinic_db"))

        rows = [
            ("Host",     self._host),
            ("Port",     self._port),
            ("Username", self._user),
            ("Password", self._password),
            ("Database", self._database),
        ]
        for i, (label, widget) in enumerate(rows):
            grid.addWidget(make_label(label, colour=COLOUR["text_dim"]), i, 0)
            grid.addWidget(widget, i, 1)

        grid.setColumnStretch(1, 1)
        root.addLayout(grid)
        root.addSpacing(8)

        self._status_lbl = make_label("", size=9)
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._status_lbl)
        root.addSpacing(20)

        btn_row = QHBoxLayout()
        test_btn = make_button("Test Connection", COLOUR["header_bg"], COLOUR["text_main"])
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOUR["header_bg"]};
                color: {COLOUR["text_main"]};
                border: 1px solid {COLOUR["border"]};
                border-radius: 6px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOUR["border"]};
            }}
        """)
        test_btn.clicked.connect(self._on_test)

        connect_btn = make_button("  Save & Connect  ", COLOUR["accent"], "#FFFFFF")
        connect_btn.clicked.connect(self._on_connect)

        exit_btn = make_button("Exit", COLOUR["border"], COLOUR["text_dim"])
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOUR["border"]};
                color: {COLOUR["text_dim"]};
                border: none;
                border-radius: 6px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: #CBD5E1;
                color: {COLOUR["text_main"]};
            }}
        """)
        exit_btn.clicked.connect(self.reject)

        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        btn_row.addWidget(exit_btn)
        btn_row.addSpacing(8)
        btn_row.addWidget(connect_btn)
        root.addLayout(btn_row)

    def _collect_config(self) -> dict:
        return {
            "host":     self._host.text().strip() or "localhost",
            "port":     int(self._port.text().strip() or "3306"),
            "user":     self._user.text().strip() or "root",
            "password": self._password.text(),
            "database": self._database.text().strip() or "clinic_db",
        }

    def _set_status(self, msg: str, ok: bool) -> None:
        colour = COLOUR["accent2"] if ok else COLOUR["accent3"]
        self._status_lbl.setStyleSheet(f"color: {colour};")
        self._status_lbl.setText(msg)

    def _on_test(self) -> None:
        cfg = self._collect_config()
        self._set_status("Testing\u2026", ok=True)
        try:
            conn = mysql.connector.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
            )
            conn.close()
            self._set_status(
                "\u2713  Connection successful! (database will be created if needed)",
                ok=True,
            )
        except mysql.connector.Error as exc:
            self._set_status(f"\u2717  {exc}", ok=False)

    def _on_connect(self) -> None:
        cfg = self._collect_config()

        try:
            conn = mysql.connector.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
            )
            cur = conn.cursor()
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cur.close()
            conn.close()
        except mysql.connector.Error as exc:
            self._set_status(f"\u2717  {exc}", ok=False)
            return

        db.save_config(cfg)
        self.accept()
