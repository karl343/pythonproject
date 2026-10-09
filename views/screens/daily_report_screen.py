from __future__ import annotations

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR
from utils.widget_factory import (
    make_button,
    make_date_edit,
    make_label,
    make_secondary_button,
    make_stat_card,
    make_table,
    populate_table,
)
from views.screens.base_screen import BaseScreen

class DailyReportScreen(BaseScreen):

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
            make_label("Daily Clinical Report", bold=True, size=15, colour=COLOUR["text_main"])
        )
        header_box.addWidget(
            make_label(
                "Chronological schedule, daily performance metrics, and patient visit outcomes.",
                size=10,
                colour=COLOUR["text_dim"],
            )
        )
        root.addLayout(header_box)
        root.addSpacing(16)

        root.addWidget(self._build_filter_bar())
        root.addSpacing(14)

        self._kpi_layout = QHBoxLayout()
        self._kpi_layout.setSpacing(14)
        self._card_total = make_stat_card("Total Appointments", "0", "\U0001f4cb", COLOUR["text_main"])
        self._card_sched = make_stat_card("Scheduled / Pending", "0", "\u23f3", COLOUR["accent"])
        self._card_comp  = make_stat_card("Successful / Completed", "0", "\u2705", COLOUR["accent2"])
        self._card_other = make_stat_card("Cancelled / No Show", "0", "\u274c", COLOUR["accent3"])

        self._kpi_layout.addWidget(self._card_total)
        self._kpi_layout.addWidget(self._card_sched)
        self._kpi_layout.addWidget(self._card_comp)
        self._kpi_layout.addWidget(self._card_other)
        root.addLayout(self._kpi_layout)
        root.addSpacing(14)

        self._table = make_table(self._COLUMNS)
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        root.addWidget(self._table)
        root.addSpacing(12)

        action_bar = QHBoxLayout()
        self._selected_lbl = make_label(
            "Select an appointment to record visit outcome.",
            size=9,
            colour=COLOUR["text_dim"],
        )
        action_bar.addWidget(self._selected_lbl)
        action_bar.addStretch()

        self._success_btn = make_button("  \u2713  Mark as Successful  ", COLOUR["accent2"], "#FFFFFF")
        self._success_btn.setEnabled(False)
        self._success_btn.clicked.connect(self._on_mark_success)
        action_bar.addWidget(self._success_btn)
        action_bar.addSpacing(8)

        self._fail_btn = make_button("  \u2715  Mark as Not Successful  ", COLOUR["accent3"], "#FFFFFF")
        self._fail_btn.setEnabled(False)
        self._fail_btn.clicked.connect(self._on_mark_fail)
        action_bar.addWidget(self._fail_btn)

        root.addLayout(action_bar)

    def _build_filter_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOUR["border"]};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        prev_btn = make_secondary_button("\u25c0  Yesterday")
        prev_btn.clicked.connect(self._on_yesterday)
        layout.addWidget(prev_btn)

        today_btn = make_secondary_button("Today")
        today_btn.clicked.connect(self._on_today)
        layout.addWidget(today_btn)

        next_btn = make_secondary_button("Tomorrow  \u25b6")
        next_btn.clicked.connect(self._on_tomorrow)
        layout.addWidget(next_btn)

        layout.addSpacing(8)
        layout.addWidget(make_label("\U0001f4c5  Date:", bold=True, size=9, colour=COLOUR["text_dim"]))

        self._date_picker = make_date_edit()
        self._date_picker.dateChanged.connect(self._on_generate)
        layout.addWidget(self._date_picker)

        generate_btn = make_button("  Generate  ", COLOUR["accent"], "#FFFFFF")
        generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(generate_btn)

        layout.addStretch()
        return bar

    def refresh(self) -> None:
        self._on_generate()

    def _on_yesterday(self) -> None:
        self._date_picker.setDate(self._date_picker.date().addDays(-1))

    def _on_today(self) -> None:
        self._date_picker.setDate(QDate.currentDate())

    def _on_tomorrow(self) -> None:
        self._date_picker.setDate(self._date_picker.date().addDays(1))

    def _on_generate(self) -> None:
        date_str = self._date_picker.date().toString("yyyy-MM-dd")
        result = self._ctrl.get_by_date(date_str)
        records = result.get("data", [])
        populate_table(self._table, records)

        self._success_btn.setEnabled(False)
        self._fail_btn.setEnabled(False)
        self._selected_lbl.setText("Select an appointment to record visit outcome.")

        total = len(records)
        completed = sum(1 for r in records if r.get("status") in ("Completed", "Successful", "Completed (Successful)"))
        noshow = sum(1 for r in records if r.get("status") in ("No Show", "Not Successful", "No Show (Not Successful)"))
        scheduled = sum(1 for r in records if r.get("status") == "Scheduled")
        cancelled = sum(1 for r in records if r.get("status") == "Cancelled")

        self._update_kpi(total, scheduled, completed, cancelled + noshow)

    def _update_kpi(self, total: int, scheduled: int, completed: int, other: int) -> None:
        self._card_total.findChildren(type(self._selected_lbl))[1].setText(str(total))
        self._card_sched.findChildren(type(self._selected_lbl))[1].setText(str(scheduled))
        self._card_comp.findChildren(type(self._selected_lbl))[1].setText(str(completed))
        self._card_other.findChildren(type(self._selected_lbl))[1].setText(str(other))

    def _on_selection_changed(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            appt_id = self._table.item(row, 0).text()
            patient = self._table.item(row, 1).text()
            status = self._table.item(row, 6).text()
            self._selected_lbl.setText(f"Selected: <b>{appt_id}</b> ({patient}) \u2502 Status: <b>{status}</b>")
            self._success_btn.setEnabled(status not in ("Completed", "Successful"))
            self._fail_btn.setEnabled(status not in ("No Show", "Not Successful", "Cancelled"))
        else:
            self._selected_lbl.setText("Select an appointment to record visit outcome.")
            self._success_btn.setEnabled(False)
            self._fail_btn.setEnabled(False)

    def _selected_id(self) -> str | None:
        rows = self._table.selectionModel().selectedRows()
        if rows:
            return self._table.item(rows[0].row(), 0).text()
        return None

    def _on_mark_success(self) -> None:
        appt_id = self._selected_id()
        if not appt_id:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Outcome",
            f"Mark appointment {appt_id} as Successful (Completed)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ctrl.record_outcome(appt_id, successful=True)
            self.refresh()

    def _on_mark_fail(self) -> None:
        appt_id = self._selected_id()
        if not appt_id:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Outcome",
            f"Mark appointment {appt_id} as Not Successful (No Show)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ctrl.record_outcome(appt_id, successful=False)
            self.refresh()
