from __future__ import annotations

from PyQt6.QtCore import QDate, QRegularExpression, QTime, Qt
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR, PHYSICIANS, STATUSES
from utils.widget_factory import (
    make_button,
    make_combo,
    make_date_edit,
    make_input,
    make_label,
    make_secondary_button,
    make_time_edit,
)
from views.screens.base_screen import BaseScreen

class AddScreen(BaseScreen):

    def __init__(
        self,
        controller: AppointmentController,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(controller, parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(0)

        header_box = QVBoxLayout()
        header_box.setSpacing(3)
        header_box.addWidget(
            make_label("Schedule Appointment", bold=True, size=15, colour=COLOUR["text_main"])
        )
        header_box.addWidget(
            make_label(
                "Enter patient and scheduling details. Double-booking conflicts are automatically detected.",
                size=10,
                colour=COLOUR["text_dim"],
            )
        )
        root.addLayout(header_box)
        root.addSpacing(20)

        root.addWidget(self._make_form_card())
        root.addStretch()

    def _make_form_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet(f"""
            QFrame#formCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLOUR["border"]};
                border-radius: 10px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(16)

        sec1_lbl = make_label("PATIENT DETAILS", bold=True, size=9, colour=COLOUR["accent"])
        card_layout.addWidget(sec1_lbl)

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(24)
        grid1.setVerticalSpacing(12)

        self._patient_name = make_input("Patient full name")
        self._contact = make_input()
        self._contact.setMaxLength(11)
        self._contact.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]{0,11}$")))

        grid1.addWidget(make_label("Patient Name *", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 0)
        grid1.addWidget(self._patient_name, 1, 0)

        grid1.addWidget(make_label("Contact Information *", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 1)
        grid1.addWidget(self._contact, 1, 1)

        card_layout.addLayout(grid1)
        card_layout.addSpacing(6)

        sec2_lbl = make_label("CONSULTATION & TIME SLOT", bold=True, size=9, colour=COLOUR["accent"])
        card_layout.addWidget(sec2_lbl)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(24)
        grid2.setVerticalSpacing(12)

        self._physician = make_combo(PHYSICIANS)
        self._status = make_combo(STATUSES)
        self._date = make_date_edit()
        self._time = make_time_edit()

        grid2.addWidget(make_label("Assigned Physician *", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 0)
        grid2.addWidget(self._physician, 1, 0)

        grid2.addWidget(make_label("Initial Status", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 1)
        grid2.addWidget(self._status, 1, 1)

        grid2.addWidget(make_label("Appointment Date *", bold=True, size=9, colour=COLOUR["text_dim"]), 2, 0)
        grid2.addWidget(self._date, 3, 0)

        grid2.addWidget(make_label("Appointment Time *", bold=True, size=9, colour=COLOUR["text_dim"]), 2, 1)
        grid2.addWidget(self._time, 3, 1)

        card_layout.addLayout(grid2)
        card_layout.addSpacing(10)

        self._banner = QFrame()
        self._banner.setVisible(False)
        self._banner_layout = QHBoxLayout(self._banner)
        self._banner_layout.setContentsMargins(14, 10, 14, 10)
        self._banner_lbl = make_label("", bold=True, size=9)
        self._banner_layout.addWidget(self._banner_lbl)
        card_layout.addWidget(self._banner)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        clear_btn = make_secondary_button("Clear Fields")
        clear_btn.clicked.connect(self._clear_form)
        btn_row.addWidget(clear_btn)

        save_btn = make_button("  \u2713  Save Appointment  ", COLOUR["accent"], "#FFFFFF")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        card_layout.addLayout(btn_row)

        return card

    def _clear_form(self) -> None:
        self._patient_name.clear()
        self._contact.clear()
        self._physician.setCurrentIndex(0)
        self._date.setDate(QDate.currentDate())
        self._time.setTime(QTime(8, 0))
        self._status.setCurrentIndex(0)
        self._hide_banner()

    def _on_save(self) -> None:
        result = self._ctrl.add({
            "patient_name": self._patient_name.text(),
            "contact":      self._contact.text(),
            "physician":    self._physician.currentText(),
            "date":         self._date.date().toString("yyyy-MM-dd"),
            "time":         self._time.time().toString("HH:mm"),
            "status":       self._status.currentText(),
        })
        if result["ok"]:
            self._show_banner(f"\u2713  {result['message']}", success=True)
            self._clear_form_inputs()
        elif result.get("error") == "double_booking":
            self._show_banner(f"\u26a0  {result['message']}", success=False)
            QMessageBox.warning(
                self, "Double Booking Detected",
                f"\u26a0\u2002{result['message']}\n\nPlease choose a different physician, date, or time slot.",
            )
        else:
            self._show_banner(f"\u2717  {result['message']}", success=False)

    def _clear_form_inputs(self) -> None:
        self._patient_name.clear()
        self._contact.clear()
        self._physician.setCurrentIndex(0)
        self._date.setDate(QDate.currentDate())
        self._time.setTime(QTime(8, 0))
        self._status.setCurrentIndex(0)

    def _show_banner(self, msg: str, success: bool) -> None:
        bg = "#DCFCE7" if success else "#FEE2E2"
        border = "#86EFAC" if success else "#FCA5A5"
        text_color = "#16A34A" if success else "#DC2626"

        self._banner.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
        """)
        self._banner_lbl.setStyleSheet(f"color: {text_color};")
        self._banner_lbl.setText(msg)
        self._banner.setVisible(True)

    def _hide_banner(self) -> None:
        self._banner.setVisible(False)
        self._banner_lbl.setText("")
