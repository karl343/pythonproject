from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR
from utils.widget_factory import make_button, make_label, make_secondary_button

class AppointmentOutcomeDialog(QDialog):

    def __init__(
        self,
        controller: AppointmentController,
        appointments: list[dict],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._ctrl = controller
        self._appointments = list(appointments)
        self._current_index = 0
        self._recorded_count = 0
        self._build_ui()
        self.setWindowTitle("Appointment Arrival \u2014 Visit Outcome")
        self.setFixedWidth(520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #FFFFFF;
                border: 2px solid {COLOUR["border"]};
                border-radius: 12px;
            }}
        """)
        self._show_current_appointment()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 26, 32, 26)
        root.setSpacing(0)

        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = make_label(
            "\u23f0  Appointment Time Arrived",
            bold=True,
            size=13,
            colour=COLOUR["accent"],
        )
        subtitle = make_label(
            "The scheduled appointment date and time has arrived. Record the visit outcome:",
            size=9,
            colour=COLOUR["text_dim"],
        )
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self._counter_lbl = make_label("", bold=True, size=10, colour=COLOUR["accent"])
        header_layout.addWidget(self._counter_lbl)
        root.addLayout(header_layout)
        root.addSpacing(16)

        self._card = QFrame()
        self._card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOUR["table_alt"]};
                border: 1px solid {COLOUR["border"]};
                border-radius: 8px;
            }}
        """)
        card_layout = QGridLayout(self._card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setHorizontalSpacing(16)
        card_layout.setVerticalSpacing(8)

        card_layout.addWidget(make_label("Appointment ID:", bold=True, size=9, colour=COLOUR["text_dim"]), 0, 0)
        self._val_id = make_label("", bold=True, size=10, colour=COLOUR["accent"])
        card_layout.addWidget(self._val_id, 0, 1)

        card_layout.addWidget(make_label("Patient Name:", bold=True, size=9, colour=COLOUR["text_dim"]), 1, 0)
        self._val_patient = make_label("", bold=True, size=10)
        card_layout.addWidget(self._val_patient, 1, 1)

        card_layout.addWidget(make_label("Contact Info:", bold=True, size=9, colour=COLOUR["text_dim"]), 2, 0)
        self._val_contact = make_label("", size=9)
        card_layout.addWidget(self._val_contact, 2, 1)

        card_layout.addWidget(make_label("Physician:", bold=True, size=9, colour=COLOUR["text_dim"]), 3, 0)
        self._val_physician = make_label("", size=9)
        card_layout.addWidget(self._val_physician, 3, 1)

        card_layout.addWidget(make_label("Scheduled For:", bold=True, size=9, colour=COLOUR["text_dim"]), 4, 0)
        self._val_datetime = make_label("", bold=True, size=10, colour=COLOUR["accent2"])
        card_layout.addWidget(self._val_datetime, 4, 1)

        root.addWidget(self._card)
        root.addSpacing(18)

        prompt_lbl = make_label(
            "Was this appointment visit successful?",
            bold=True,
            size=11,
            colour=COLOUR["text_main"],
        )
        prompt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(prompt_lbl)
        root.addSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._success_btn = make_button("  \u2713  Successful (Completed)  ", COLOUR["accent2"], "#FFFFFF")
        self._success_btn.clicked.connect(self._on_successful)
        btn_row.addWidget(self._success_btn)

        self._fail_btn = make_button("  \u2715  Not Successful (No Show)  ", COLOUR["accent3"], "#FFFFFF")
        self._fail_btn.clicked.connect(self._on_unsuccessful)
        btn_row.addWidget(self._fail_btn)

        root.addLayout(btn_row)
        root.addSpacing(10)

        later_btn = make_secondary_button("Remind Later (Snooze 5m)")
        later_btn.clicked.connect(self._on_remind_later)
        root.addWidget(later_btn)

    def _show_current_appointment(self) -> None:
        if self._current_index >= len(self._appointments):
            self.accept()
            return

        appt = self._appointments[self._current_index]
        total = len(self._appointments)
        if total > 1:
            self._counter_lbl.setText(f"Record {self._current_index + 1} of {total}")
        else:
            self._counter_lbl.setText("")

        self._val_id.setText(appt.get("id", ""))
        self._val_patient.setText(appt.get("patient_name", ""))
        self._val_contact.setText(appt.get("contact", ""))
        self._val_physician.setText(appt.get("physician", ""))
        self._val_datetime.setText(f"{appt.get('date', '')}  \u2502  {appt.get('time', '')}")

    def _on_successful(self) -> None:
        if self._current_index < len(self._appointments):
            appt = self._appointments[self._current_index]
            self._ctrl.record_outcome(appt["id"], successful=True)
            self._recorded_count += 1
            self._current_index += 1
            self._show_current_appointment()

    def _on_unsuccessful(self) -> None:
        if self._current_index < len(self._appointments):
            appt = self._appointments[self._current_index]
            self._ctrl.record_outcome(appt["id"], successful=False)
            self._recorded_count += 1
            self._current_index += 1
            self._show_current_appointment()

    def _on_remind_later(self) -> None:
        self._current_index += 1
        if self._current_index >= len(self._appointments):
            self.reject()
        else:
            self._show_current_appointment()

    @property
    def recorded_count(self) -> int:
        return self._recorded_count
