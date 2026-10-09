from __future__ import annotations

from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR
from utils.widget_factory import make_label
from views.outcome_dialog import AppointmentOutcomeDialog
from views.screens.add_screen import AddScreen
from views.screens.base_screen import BaseScreen
from views.screens.cancel_screen import CancelScreen
from views.screens.daily_report_screen import DailyReportScreen
from views.screens.dashboard_screen import DashboardScreen
from views.screens.modify_screen import ModifyScreen
from views.screens.search_screen import SearchScreen
from views.screens.view_all_screen import ViewAllScreen
from views.widgets.sidebar_button import SidebarButton

class MainWindow(QMainWindow):

    _NAV_ITEMS: list[tuple[str, str]] = [
        ("\U0001f4ca",       "Dashboard"),
        ("\u2795",           "Add Appointment"),
        ("\U0001f4cb",       "View All"),
        ("\U0001f50d",       "Search"),
        ("\u270f\ufe0f",     "Modify"),
        ("\U0001f6ab",       "Cancel / Delete"),
        ("\U0001f4c5",       "Daily Report"),
    ]

    def __init__(self, controller: AppointmentController, parent=None) -> None:
        super().__init__(parent)
        self._ctrl = controller
        self._sidebar_btns: list[SidebarButton] = []
        self._screens: list[BaseScreen] = []
        self._snoozed: dict[str, datetime] = {}
        self._dialog_active = False

        self._build_ui()
        self._apply_global_styles()
        self._switch_to(0)

        self.setWindowTitle("\U0001f3e5  Clinic Appointment Management System")
        self.resize(1180, 740)
        self.setMinimumSize(980, 620)
        self._center_on_screen()

        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_arrived_appointments)
        self._check_timer.start(10_000)
        QTimer.singleShot(1500, self._check_arrived_appointments)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(x, y)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_h = QHBoxLayout(central)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)
        main_h.addWidget(self._build_sidebar())
        main_h.addWidget(self._build_content_area())

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        brand = QFrame()
        brand.setFixedHeight(75)
        brand.setObjectName("brand")
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(2)
        brand_title = make_label("\U0001f3e5  ClinicMS", bold=True, size=13, colour=COLOUR["sidebar_active"])
        brand_sub = make_label("Medical Practice Suite", size=8, colour=COLOUR["sidebar_text"])
        bl.addWidget(brand_title)
        bl.addWidget(brand_sub)
        layout.addWidget(brand)

        layout.addWidget(self._sidebar_divider())
        layout.addSpacing(10)

        for icon, label in self._NAV_ITEMS:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(
                lambda _, idx=len(self._sidebar_btns): self._switch_to(idx)
            )
            self._sidebar_btns.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        layout.addWidget(self._sidebar_divider())

        user_card = QFrame()
        user_card.setFixedHeight(64)
        ul = QHBoxLayout(user_card)
        ul.setContentsMargins(16, 8, 16, 8)
        ul.setSpacing(10)

        avatar_lbl = make_label("\U0001f464", size=14, colour=COLOUR["sidebar_active"])
        ul.addWidget(avatar_lbl)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        name_lbl = make_label("admin", bold=True, size=10, colour="#F8FAFC")
        role_lbl = make_label("Administrator", size=8, colour=COLOUR["sidebar_text"])
        user_info.addWidget(name_lbl)
        user_info.addWidget(role_lbl)
        ul.addLayout(user_info)
        ul.addStretch()

        logout_btn = QPushButton("\U0001f6aa")
        logout_btn.setToolTip("Sign Out")
        logout_btn.setFixedSize(32, 32)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EF4444;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FCA5A5;
            }
        """)
        logout_btn.clicked.connect(self._on_logout)
        ul.addWidget(logout_btn)

        layout.addWidget(user_card)
        layout.addSpacing(6)

        return sidebar

    def _build_content_area(self) -> QWidget:
        area = QWidget()
        area.setObjectName("contentArea")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = QFrame()
        topbar.setFixedHeight(58)
        topbar.setObjectName("topbar")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(36, 0, 36, 0)

        self._topbar_title = make_label("", bold=True, size=14, colour=COLOUR["text_main"])
        tb.addWidget(self._topbar_title)
        tb.addStretch()

        self._arrived_btn = QPushButton("")
        self._arrived_btn.setVisible(False)
        self._arrived_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._arrived_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF3C7;
                color: #D97706;
                border: 1px solid #FDE68A;
                border-radius: 14px;
                padding: 5px 14px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #FDE68A;
            }
        """)
        self._arrived_btn.clicked.connect(lambda: self._open_outcome_dialog())
        tb.addWidget(self._arrived_btn)
        tb.addSpacing(16)

        self._clock_lbl = make_label("", size=9, colour=COLOUR["text_dim"])
        tb.addWidget(self._clock_lbl)
        layout.addWidget(topbar)

        self._stack = QStackedWidget()
        screen_classes = [
            DashboardScreen,
            AddScreen,
            ViewAllScreen,
            SearchScreen,
            ModifyScreen,
            CancelScreen,
            DailyReportScreen,
        ]
        for cls in screen_classes:
            screen = cls(self._ctrl)
            if isinstance(screen, DashboardScreen):
                screen.request_navigation.connect(self._switch_to)
            self._screens.append(screen)
            self._stack.addWidget(screen)

        layout.addWidget(self._stack, 1)

        self._update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(30_000)

        return area

    def _switch_to(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._sidebar_btns):
            btn.set_active(i == index)
        _, label = self._NAV_ITEMS[index]
        self._topbar_title.setText(label)
        self._screens[index].refresh()

    def _update_clock(self) -> None:
        now_str = datetime.now().strftime("%A, %b %d, %Y  \u2502  %H:%M")
        self._clock_lbl.setText(f"\U0001f552 {now_str}")

    def _check_arrived_appointments(self) -> None:
        result = self._ctrl.get_arrived_appointments()
        if not result["ok"]:
            return
        arrived = result["data"]
        now = datetime.now()
        due = [
            a for a in arrived
            if a["id"] not in self._snoozed or now >= self._snoozed[a["id"]]
        ]
        if due:
            self._arrived_btn.setText(f"\u23f0 {len(due)} Arrived (Outcome Needed)")
            self._arrived_btn.setVisible(True)
            if not self._dialog_active:
                self._open_outcome_dialog(due)
        else:
            self._arrived_btn.setVisible(False)

    def _open_outcome_dialog(self, due_list: list[dict] | None = None) -> None:
        if due_list is None:
            res = self._ctrl.get_arrived_appointments()
            if not res["ok"] or not res["data"]:
                return
            due_list = res["data"]
        if not due_list:
            return

        self._dialog_active = True
        dlg = AppointmentOutcomeDialog(self._ctrl, due_list, parent=self)
        dlg.exec()
        self._dialog_active = False

        now = datetime.now()
        for a in due_list:
            self._snoozed[a["id"]] = now + timedelta(minutes=5)

        curr_idx = self._stack.currentIndex()
        if 0 <= curr_idx < len(self._screens):
            self._screens[curr_idx].refresh()

        res = self._ctrl.get_arrived_appointments()
        remaining = res.get("data", [])
        if remaining:
            self._arrived_btn.setText(f"\u23f0 {len(remaining)} Arrived (Outcome Needed)")
            self._arrived_btn.setVisible(True)
        else:
            self._arrived_btn.setVisible(False)

    def _on_logout(self) -> None:
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to sign out of the clinic system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    @staticmethod
    def _sidebar_divider() -> QFrame:
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #1E293B;")
        return div

    def _apply_global_styles(self) -> None:
        self.setStyleSheet(f"""
            QMainWindow, QWidget#contentArea {{
                background-color: {COLOUR["bg_main"]};
            }}
            QFrame#sidebar {{
                background-color: {COLOUR["sidebar_bg"]};
                border-right: 1px solid #1E293B;
            }}
            QFrame#brand {{
                background-color: {COLOUR["sidebar_bg"]};
            }}
            QFrame#topbar {{
                background-color: #FFFFFF;
                border-bottom: 1px solid {COLOUR["border"]};
            }}
            QMessageBox {{
                background-color: #FFFFFF;
                color: {COLOUR["text_main"]};
            }}
            QMessageBox QLabel {{
                color: {COLOUR["text_main"]};
                font-size: 11px;
            }}
            QMessageBox QPushButton {{
                background-color: {COLOUR["accent"]};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 7px 20px;
                min-width: 75px;
                font-weight: bold;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {COLOUR["accent_hover"]};
            }}
            QCalendarWidget {{
                background-color: #FFFFFF;
                color: {COLOUR["text_main"]};
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: #FFFFFF;
                color: {COLOUR["text_main"]};
                selection-background-color: {COLOUR["accent"]};
                selection-color: #FFFFFF;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {COLOUR["header_bg"]};
            }}
            QCalendarWidget QToolButton {{
                color: {COLOUR["text_main"]};
                background-color: transparent;
            }}
        """)
