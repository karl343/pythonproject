from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton

from utils.constants import COLOUR

class SidebarButton(QPushButton):

    def __init__(self, icon_text: str, label: str, parent=None) -> None:
        super().__init__(parent)
        self.setText(f"  {icon_text}   {label}")
        self.setFont(QFont("Segoe UI", 10))
        self.setFixedHeight(42)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self._apply_style(active=False)

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self._apply_style(active)

    def _apply_style(self, active: bool) -> None:
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOUR["sidebar_sel"]};
                    color: {COLOUR["sidebar_active"]};
                    border: none;
                    border-left: 3.5px solid {COLOUR["sidebar_active"]};
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 14px;
                    font-weight: bold;
                    margin: 2px 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOUR["sidebar_text"]};
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 17px;
                    margin: 2px 8px;
                }}
                QPushButton:hover {{
                    background-color: {COLOUR["sidebar_sel"]};
                    color: #F8FAFC;
                }}
            """)
