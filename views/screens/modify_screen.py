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

class ModifyScreen(BaseScreen):

    def __init__(
        self,
        controller: AppointmentController,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(controller, parent)
        self._current_id: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(0)

        header_box = QVBoxLayout()
        header_box.setSpacing(3)
        header_box.addWidget(
            make_label("Modify Appointment", bold=True, size=15, colour=COLOUR["text_main"])
        )
        header_box.addWidget(
            make_label(
                "Enter an Appointment ID to retrieve details, adjust the schedule, or update patient info.",
                size=10,
                colour=COLOUR["text_dim"],
            )
        )
        root.addLayout(header_box)
        root.addSpacing(18)

        root.addWidget(self._build_lookup_card())
        root.addSpacing(16)

        self._edit_card = self._build_edit_card()
        self._edit_card.setVisible(False)
        root.addWidget(self._edit_card)

        root.addStretch()

    def _build_lookup_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("lookupCard")
        card.setStyleSheet(f"""
            QFrame#lookupCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLOUR["border"]};
                border-radius: 10px;
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(14)

        icon_lbl = make_label("\U0001f50d", size=14)
        layout.addWidget(icon_lbl)

        layout.addWidget(make_label("Appointment ID:", bold=True, colour=COLOUR["text_dim"]))

        self._id_input = make_input("e.g. APT-0001")
        self._id_input.returnPressed.connect(self._on_fetch)
        layout.addWidget(self._id_input, 1)

        fetch_btn = make_button("  Load Details  ", COLOUR["accent"], "#FFFFFF")
        fetch_btn.clicked.connect(self._on_fetch)
        layout.addWidget(fetch_btn)

        return card

    def _build_edit_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("editCard")
        card.setStyleSheet(f"""
            QFrame#editCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLOUR["border"]};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 26, 32, 26)
        layout.setSpacing(16)

        title_row = QHBoxLayout()
        self._loaded_lbl = make_label("", bold=True, size=12, colour=COLOUR["accent"])
        title_row.addWidget(self._loaded_lbl)
        title_row.addStretch()
        layout.addLayout(title_row)

        sec1 = make_label("PATIENT DETAILS", bold=True, size=9, colour=COLOUR["text_dim"])
        layout.addWidget(sec1)

        grid1 = QGridLayout()
        grid1.setHorizontalSpacing(24)
        grid1.setVerticalSpacing(10)

        self._patient_name = make_input()
        self._contact = make_input()
        self._contact.setMaxLength(11)
        self._contact.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]{0,11}$")))

        grid1.addWidget(make_label("Patient Name *", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 0)
        grid1.addWidget(self._patient_name, 1, 0)

        grid1.addWidget(make_label("Contact Information *", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 1)
        grid1.addWidget(self._contact, 1, 1)

        layout.addLayout(grid1)
        layout.addSpacing(4)

        sec2 = make_label("CONSULTATION & TIME SLOT", bold=True, size=9, colour=COLOUR["text_dim"])
        layout.addWidget(sec2)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(24)
        grid2.setVerticalSpacing(10)

        self._physician = make_combo(PHYSICIANS)
        self._status = make_combo(STATUSES)
        self._date = make_date_edit()
        self._time = make_time_edit()

        grid2.addWidget(make_label("Assigned Physician *", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 0)
        grid2.addWidget(self._physician, 1, 0)

        grid2.addWidget(make_label("Status", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 1)
        grid2.addWidget(self._status, 1, 1)

        grid2.addWidget(make_label("Appointment Date *", bold=True, size=9, colour=COLOUR["text_dim"]), 2, 0)
        grid2.addWidget(self._date, 3, 0)

        grid2.addWidget(make_label("Appointment Time *", bold=True, size=9, colour=COLOUR["text_dim"]), 2, 1)
        grid2.addWidget(self._time, 3, 1)

        layout.addLayout(grid2)
        layout.addSpacing(8)

        self._banner = QFrame()
        self._banner.setVisible(False)
        self._banner_layout = QHBoxLayout(self._banner)
        self._banner_layout.setContentsMargins(14, 10, 14, 10)
        self._banner_lbl = make_label("", bold=True, size=9)
        self._banner_layout.addWidget(self._banner_lbl)
        layout.addWidget(self._banner)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        close_btn = make_secondary_button("Cancel / Close")
        close_btn.clicked.connect(self._on_close_editor)
        btn_row.addWidget(close_btn)

        save_btn = make_button("  \u2713  Save Changes  ", COLOUR["accent2"], "#FFFFFF")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

        return card

    def refresh(self) -> None:
        self._id_input.clear()
        self._edit_card.setVisible(False)
        self._current_id = None
        self._hide_banner()

    def _on_close_editor(self) -> None:
        self._edit_card.setVisible(False)
        self._current_id = None
        self._id_input.clear()
        self._id_input.setFocus()

    def _on_fetch(self) -> None:
        appt_id = self._id_input.text().strip().upper()
        if not appt_id:
            QMessageBox.information(self, "Input Required", "Please enter an Appointment ID.")
            return

        result = self._ctrl.get_by_id(appt_id)
        if not result["ok"]:
            QMessageBox.warning(self, "Appointment Not Found", result["message"])
            self._edit_card.setVisible(False)
            return

        appt = result["data"]
        self._current_id = appt["id"]
        self._loaded_lbl.setText(f"\U0001f4cb  Editing Appointment: {appt['id']}")
        self._patient_name.setText(appt["patient_name"])
        self._contact.setText(appt["contact"])

        idx = self._physician.findText(appt["physician"])
        self._physician.setCurrentIndex(max(idx, 0))

        self._date.setDate(QDate.fromString(str(appt["date"]), "yyyy-MM-dd"))
        self._time.setTime(QTime.fromString(str(appt["time"])[:5], "HH:mm"))

        idx = self._status.findText(appt["status"])
        self._status.setCurrentIndex(max(idx, 0))

        self._hide_banner()
        self._edit_card.setVisible(True)

    def _on_save(self) -> None:
        if not self._current_id:
            return

        result = self._ctrl.update(self._current_id, {
            "patient_name": self._patient_name.text(),
            "contact":      self._contact.text(),
            "physician":    self._physician.currentText(),
            "date":         self._date.date().toString("yyyy-MM-dd"),
            "time":         self._time.time().toString("HH:mm"),
            "status":       self._status.currentText(),
        })

        if result["ok"]:
            self._show_banner(f"\u2713  {result['message']}", success=True)
        elif result.get("error") == "double_booking":
            self._show_banner(f"\u26a0  {result['message']}", success=False)
            QMessageBox.warning(
                self, "Double Booking Detected",
                f"\u26a0\u2002{result['message']}\n\nPlease choose a different physician, date, or time slot.",
            )
        else:
            self._show_banner(f"\u2717  {result['message']}", success=False)

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
