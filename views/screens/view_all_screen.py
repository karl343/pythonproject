from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QMessageBox, QVBoxLayout, QWidget

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR
from utils.widget_factory import make_button, make_label, make_table, populate_table
from views.screens.base_screen import BaseScreen

class ViewAllScreen(BaseScreen):

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
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.addWidget(
            make_label("All Appointments", bold=True, size=16, colour=COLOUR["accent"])
        )
        header_row.addStretch()
        refresh_btn = make_button("\u27f3  Refresh", COLOUR["header_bg"], COLOUR["text_main"])
        refresh_btn.setStyleSheet(f"""
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
        refresh_btn.clicked.connect(self.refresh)
        header_row.addWidget(refresh_btn)
        root.addLayout(header_row)

        root.addWidget(
            make_label(
                "Full list. Click a column header to sort, or select a row to record outcome.",
                size=10, colour=COLOUR["text_dim"],
            )
        )
        root.addSpacing(14)

        self._count_lbl = make_label("", size=10, colour=COLOUR["text_dim"])
        root.addWidget(self._count_lbl)
        root.addSpacing(8)

        self._table = make_table(self._COLUMNS)
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        root.addWidget(self._table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._success_btn = make_button("\u2713  Mark as Successful", COLOUR["accent2"], "#FFFFFF")
        self._success_btn.setEnabled(False)
        self._success_btn.clicked.connect(self._on_mark_success)
        self._fail_btn = make_button("\u2715  Mark as Not Successful", COLOUR["accent3"], "#FFFFFF")
        self._fail_btn.setEnabled(False)
        self._fail_btn.clicked.connect(self._on_mark_fail)
        btn_row.addWidget(self._success_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(self._fail_btn)
        root.addSpacing(12)
        root.addLayout(btn_row)

    def refresh(self) -> None:
        result    = self._ctrl.get_all()
        records   = result["data"]
        populate_table(self._table, records)
        self._success_btn.setEnabled(False)
        self._fail_btn.setEnabled(False)
        total     = len(records)
        completed = sum(1 for r in records if r.get("status") in ("Completed", "Successful"))
        noshow    = sum(1 for r in records if r.get("status") in ("No Show", "Not Successful"))
        scheduled = sum(1 for r in records if r.get("status") == "Scheduled")
        cancelled = sum(1 for r in records if r.get("status") == "Cancelled")
        self._count_lbl.setText(
            f"Total: {total}  \u2502  Successful: {completed}  \u2502  Not Successful: {noshow}  \u2502  Scheduled: {scheduled}  \u2502  Cancelled: {cancelled}"
        )

    def _on_selection_changed(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            status = self._table.item(row, 6).text()
            self._success_btn.setEnabled(status not in ("Completed", "Successful"))
            self._fail_btn.setEnabled(status not in ("No Show", "Not Successful", "Cancelled"))
        else:
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
