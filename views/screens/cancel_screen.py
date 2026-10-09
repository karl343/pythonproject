from __future__ import annotations

from PyQt6.QtCore import Qt
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
    make_input,
    make_label,
    make_secondary_button,
    make_table,
    populate_table,
)
from views.screens.base_screen import BaseScreen

class CancelScreen(BaseScreen):

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
            make_label("Cancel / Delete Appointments", bold=True, size=15, colour=COLOUR["text_main"])
        )
        header_box.addWidget(
            make_label(
                "Cancel appointments to retain audit history, or permanently remove records from the database.",
                size=10,
                colour=COLOUR["text_dim"],
            )
        )
        root.addLayout(header_box)
        root.addSpacing(16)

        info_banner = QFrame()
        info_banner.setStyleSheet(f"""
            QFrame {{
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        ibl = QHBoxLayout(info_banner)
        ibl.setContentsMargins(14, 8, 14, 8)
        info_txt = make_label(
            "\u2139\ufe0f  Tip: Marking as 'Cancelled' preserves patient records for clinic history and auditing. "
            "'Delete Permanently' completely erases the record.",
            size=9,
            colour="#15803D",
        )
        ibl.addWidget(info_txt)
        root.addWidget(info_banner)
        root.addSpacing(16)

        jump_row = QHBoxLayout()
        jump_row.addWidget(make_label("Jump to ID:", bold=True, size=9, colour=COLOUR["text_dim"]))
        self._id_jump = make_input("e.g. APT-0001")
        self._id_jump.returnPressed.connect(self._jump_to_id)
        jump_row.addWidget(self._id_jump)

        jump_btn = make_secondary_button("Find ID")
        jump_btn.clicked.connect(self._jump_to_id)
        jump_row.addWidget(jump_btn)
        jump_row.addStretch()
        root.addLayout(jump_row)
        root.addSpacing(10)

        self._table = make_table(self._COLUMNS)
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        root.addWidget(self._table)
        root.addSpacing(12)

        self._preview_card = QFrame()
        self._preview_card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLOUR["border"]};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        pcl = QHBoxLayout(self._preview_card)
        pcl.setContentsMargins(18, 10, 18, 10)
        self._selected_lbl = make_label(
            "Select an appointment from the table above to view actions.",
            size=9,
            colour=COLOUR["text_dim"],
        )
        pcl.addWidget(self._selected_lbl)
        pcl.addStretch()

        self._cancel_btn = make_button("  \U0001f6ab  Mark as Cancelled  ", "#D97706", "#FFFFFF")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._on_mark_cancelled)
        pcl.addWidget(self._cancel_btn)
        pcl.addSpacing(8)

        self._delete_btn = make_button("  \U0001f5d1  Delete Permanently  ", COLOUR["accent3"], "#FFFFFF")
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete)
        pcl.addWidget(self._delete_btn)

        root.addWidget(self._preview_card)

    def refresh(self) -> None:
        result = self._ctrl.get_all()
        populate_table(self._table, result.get("data", []))
        self._cancel_btn.setEnabled(False)
        self._delete_btn.setEnabled(False)
        self._selected_lbl.setText("Select an appointment from the table above to view actions.")

    def _on_selection_changed(self) -> None:
        row = self._selected_row_index()
        if row is None:
            self._selected_lbl.setText("Select an appointment from the table above to view actions.")
            self._cancel_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)
            return

        appt_id = self._table.item(row, 0).text()
        patient = self._table.item(row, 1).text()
        physician = self._table.item(row, 3).text()
        status  = self._table.item(row, 6).text()

        self._selected_lbl.setText(
            f"Selected: <b>{appt_id}</b> \u2502 Patient: <b>{patient}</b> \u2502 Physician: {physician} \u2502 Status: <b>{status}</b>"
        )
        self._cancel_btn.setEnabled(status != "Cancelled")
        self._delete_btn.setEnabled(True)

    def _jump_to_id(self) -> None:
        target = self._id_jump.text().strip().upper()
        if not target:
            return
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.text().upper() == target:
                self._table.selectRow(row)
                self._table.scrollToItem(item)
                return
        QMessageBox.information(self, "Not Found", f"Appointment ID '{target}' was not found in the list.")

    def _on_mark_cancelled(self) -> None:
        appt_id = self._selected_id()
        if not appt_id:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Cancellation",
            f"Mark appointment {appt_id} as Cancelled?\n\n"
            "The appointment will remain in the clinic database with 'Cancelled' status for auditing.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        result = self._ctrl.cancel(appt_id)
        if result["ok"]:
            QMessageBox.information(self, "Status Updated", result["message"])
            self.refresh()
        else:
            QMessageBox.critical(self, "Error", result["message"])

    def _on_delete(self) -> None:
        appt_id = self._selected_id()
        if not appt_id:
            return
        reply = QMessageBox.warning(
            self,
            "\u26a0 Confirm Permanent Deletion",
            f"Are you sure you want to permanently delete appointment {appt_id}?\n\n"
            "This action CANNOT be undone and will permanently erase this record.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        result = self._ctrl.delete(appt_id)
        if result["ok"]:
            QMessageBox.information(self, "Record Deleted", result["message"])
            self.refresh()
        else:
            QMessageBox.critical(self, "Error", result["message"])

    def _selected_row_index(self) -> int | None:
        rows = self._table.selectionModel().selectedRows()
        return rows[0].row() if rows else None

    def _selected_id(self) -> str | None:
        row = self._selected_row_index()
        if row is None:
            return None
        item = self._table.item(row, 0)
        return item.text() if item else None
