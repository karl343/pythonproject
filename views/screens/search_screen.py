from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout, QWidget

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR
from utils.widget_factory import (
    make_button,
    make_combo,
    make_input,
    make_label,
    make_table,
    populate_table,
)
from views.screens.base_screen import BaseScreen

class SearchScreen(BaseScreen):

    _COLUMNS = ["ID", "Patient Name", "Contact", "Physician", "Date", "Time", "Status"]

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
            make_label("Search Appointments", bold=True, size=15, colour=COLOUR["text_main"])
        )
        header_box.addWidget(
            make_label(
                "Filter records instantly by Patient Name, Appointment ID, or Status.",
                size=10,
                colour=COLOUR["text_dim"],
            )
        )
        root.addLayout(header_box)
        root.addSpacing(18)

        search_bar = QHBoxLayout()
        search_bar.setSpacing(10)

        self._search_input = make_input("\U0001f50d  Search patient name or ID\u2026")
        self._search_input.textChanged.connect(self._on_filter_changed)
        search_bar.addWidget(self._search_input, 2)

        self._status_filter = make_combo([
            "All Statuses",
            "Scheduled",
            "Completed",
            "Cancelled",
            "No Show",
        ])
        self._status_filter.currentIndexChanged.connect(self._on_filter_changed)
        search_bar.addWidget(self._status_filter, 1)

        clear_btn = make_button("\u2715  Clear", COLOUR["header_bg"], COLOUR["text_dim"])
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOUR["header_bg"]};
                color: {COLOUR["text_dim"]};
                border: 1px solid {COLOUR["border"]};
                border-radius: 6px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOUR["border"]};
                color: {COLOUR["text_main"]};
            }}
        """)
        clear_btn.clicked.connect(self._clear_search)
        search_bar.addWidget(clear_btn)

        root.addLayout(search_bar)
        root.addSpacing(12)

        self._result_lbl = make_label("", size=9, colour=COLOUR["text_dim"])
        root.addWidget(self._result_lbl)
        root.addSpacing(8)

        self._table = make_table(self._COLUMNS)
        root.addWidget(self._table)

    def refresh(self) -> None:
        self._on_filter_changed()

    def _on_filter_changed(self) -> None:
        query = self._search_input.text().strip()
        result = self._ctrl.search(query)
        records = result.get("data", [])

        status_filter = self._status_filter.currentText()
        if status_filter != "All Statuses":
            if status_filter == "Completed":
                records = [r for r in records if r.get("status") in ("Completed", "Successful", "Completed (Successful)")]
            elif status_filter == "No Show":
                records = [r for r in records if r.get("status") in ("No Show", "Not Successful", "No Show (Not Successful)")]
            else:
                records = [r for r in records if r.get("status") == status_filter]

        populate_table(self._table, records)
        count = len(records)
        if count == 0:
            self._result_lbl.setText("No matching appointments found.")
        else:
            self._result_lbl.setText(f"Showing {count} matching appointment(s).")

    def _clear_search(self) -> None:
        self._search_input.clear()
        self._status_filter.setCurrentIndex(0)
        self._on_filter_changed()
