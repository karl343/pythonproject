from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from controllers.appointment_controller import AppointmentController

class BaseScreen(QWidget):

    def __init__(
        self,
        controller: AppointmentController,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctrl = controller

    def refresh(self) -> None:
        pass
