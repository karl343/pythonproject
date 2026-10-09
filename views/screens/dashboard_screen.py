from __future__ import annotations

import matplotlib
matplotlib.use("qtagg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.appointment_controller import AppointmentController
from utils.constants import COLOUR
from utils.widget_factory import (
    StatusPillDelegate,
    make_button,
    make_label,
    make_secondary_button,
    make_stat_card,
)
from views.screens.base_screen import BaseScreen

class DashboardScreen(BaseScreen):

    request_navigation = pyqtSignal(int)

    def __init__(
        self,
        controller: AppointmentController,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(controller, parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: {COLOUR['bg_main']};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {COLOUR['bg_main']};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(36, 26, 36, 26)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_box = QVBoxLayout()
        header_box.setSpacing(3)
        header_box.addWidget(
            make_label("Clinical Overview & Analytics", bold=True, size=15, colour=COLOUR["text_main"])
        )
        header_box.addWidget(
            make_label(
                "Live clinic operations, consultation distributions, and daily caseload metrics.",
                size=10,
                colour=COLOUR["text_dim"],
            )
        )
        header_row.addLayout(header_box)
        header_row.addStretch()

        refresh_btn = make_button("\u27f3  Refresh Analytics", COLOUR["header_bg"], COLOUR["text_main"])
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
        layout.addLayout(header_row)

        self._kpi_row = QHBoxLayout()
        self._kpi_row.setSpacing(14)
        self._card_total = make_stat_card("Total Bookings", "0", "\U0001f4cb", COLOUR["text_main"], "All-time appointments")
        self._card_today = make_stat_card("Today's Schedule", "0", "\U0001f4c5", COLOUR["accent"], "Appointments for today")
        self._card_comp  = make_stat_card("Completed / Success", "0", "\u2705", COLOUR["accent2"], "Completed visits")
        self._card_miss  = make_stat_card("Cancelled / No Show", "0", "\u274c", COLOUR["accent3"], "Cancelled or missed")

        self._kpi_row.addWidget(self._card_total)
        self._kpi_row.addWidget(self._card_today)
        self._kpi_row.addWidget(self._card_comp)
        self._kpi_row.addWidget(self._card_miss)
        layout.addLayout(self._kpi_row)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        self._chart1_card = self._build_card_container("APPOINTMENT STATUS DISTRIBUTION")
        self._fig1 = Figure(figsize=(4.8, 3.0), dpi=100, facecolor="#FFFFFF")
        self._canvas1 = FigureCanvas(self._fig1)
        self._canvas1.setStyleSheet("background-color: transparent;")
        self._canvas1.setMinimumHeight(240)
        self._chart1_card.layout().addWidget(self._canvas1)
        charts_row.addWidget(self._chart1_card, 1)

        self._chart2_card = self._build_card_container("PHYSICIAN CONSULTATION CASELOAD")
        self._fig2 = Figure(figsize=(4.8, 3.0), dpi=100, facecolor="#FFFFFF")
        self._canvas2 = FigureCanvas(self._fig2)
        self._canvas2.setStyleSheet("background-color: transparent;")
        self._canvas2.setMinimumHeight(240)
        self._chart2_card.layout().addWidget(self._canvas2)
        charts_row.addWidget(self._chart2_card, 1)

        layout.addLayout(charts_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        schedule_card = self._build_card_container("TODAY'S SCHEDULE OVERVIEW")
        self._today_table = QTableWidget()
        self._today_table.setColumnCount(5)
        self._today_table.setHorizontalHeaderLabels(["ID", "Patient", "Physician", "Time", "Status"])
        self._today_table.verticalHeader().setVisible(False)
        self._today_table.verticalHeader().setDefaultSectionSize(36)
        self._today_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._today_table.setShowGrid(False)
        self._today_table.setAlternatingRowColors(True)
        self._today_table.setFont(QFont("Segoe UI", 9))
        self._today_table.setItemDelegateForColumn(4, StatusPillDelegate(self._today_table))

        th = self._today_table.horizontalHeader()
        th.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        th.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        th.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        th.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        th.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._today_table.setColumnWidth(4, 130)

        self._today_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                color: {COLOUR["text_main"]};
                border: none;
                alternate-background-color: {COLOUR["table_alt"]};
            }}
            QHeaderView::section {{
                background-color: {COLOUR["header_bg"]};
                color: {COLOUR["text_main"]};
                font-weight: bold;
                font-size: 10px;
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid {COLOUR["border"]};
            }}
        """)
        self._today_table.setMinimumHeight(180)
        schedule_card.layout().addWidget(self._today_table)
        bottom_row.addWidget(schedule_card, 2)

        actions_card = self._build_card_container("QUICK WORKFLOW ACTIONS")
        al = actions_card.layout()
        al.setSpacing(8)

        btn_add = make_button("  \u2795  Schedule New Appointment  ", COLOUR["accent"], "#FFFFFF")
        btn_add.clicked.connect(lambda: self.request_navigation.emit(1))
        al.addWidget(btn_add)

        btn_view = make_secondary_button("\U0001f4cb  View All Appointments")
        btn_view.clicked.connect(lambda: self.request_navigation.emit(2))
        al.addWidget(btn_view)

        btn_search = make_secondary_button("\U0001f50d  Search Patient Records")
        btn_search.clicked.connect(lambda: self.request_navigation.emit(3))
        al.addWidget(btn_search)

        btn_rep = make_secondary_button("\U0001f4ca  View Daily Clinical Report")
        btn_rep.clicked.connect(lambda: self.request_navigation.emit(6))
        al.addWidget(btn_rep)

        al.addStretch()
        bottom_row.addWidget(actions_card, 1)

        layout.addLayout(bottom_row)

        scroll.setWidget(container)
        root.addWidget(scroll)

    def _build_card_container(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("cardBox")
        card.setStyleSheet(f"""
            QFrame#cardBox {{
                background-color: #FFFFFF;
                border: 1px solid {COLOUR["border"]};
                border-radius: 10px;
            }}
            QFrame#cardBox QLabel {{
                border: none;
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = make_label(title, bold=True, size=9, colour=COLOUR["text_dim"])
        layout.addWidget(header)
        return card

    def refresh(self) -> None:
        result = self._ctrl.get_dashboard_analytics()
        if not result["ok"]:
            return
        data = result["data"]

        total = data["total"]
        today_total = data["today_total"]
        completed = data["completed"]
        missed = data["cancelled"] + data["noshow"]

        self._card_total.findChildren(QLabel)[2].setText(str(total))
        self._card_today.findChildren(QLabel)[2].setText(str(today_total))
        self._card_comp.findChildren(QLabel)[2].setText(str(completed))
        self._card_miss.findChildren(QLabel)[2].setText(str(missed))

        self._draw_status_chart(data["status_counts"])
        self._draw_physician_chart(data["physician_counts"])
        self._populate_today_table(data["today_appts"])

    def _draw_status_chart(self, status_counts: dict) -> None:
        self._fig1.clear()
        ax = self._fig1.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        labels = []
        sizes = []
        colors = []

        mapping = {
            "Completed": ("Completed", "#16A34A"),
            "Successful": ("Completed", "#16A34A"),
            "Completed (Successful)": ("Completed", "#16A34A"),
            "Scheduled": ("Scheduled", "#0284C7"),
            "Cancelled": ("Cancelled", "#DC2626"),
            "No Show": ("No Show", "#D97706"),
            "Not Successful": ("No Show", "#D97706"),
        }

        aggregated = {}
        for k, v in status_counts.items():
            mapped_name, hex_color = mapping.get(k, (k, "#64748B"))
            aggregated[mapped_name] = aggregated.get(mapped_name, 0) + v

        for name, count in aggregated.items():
            if count > 0:
                labels.append(name)
                sizes.append(count)
                for k, (m, c) in mapping.items():
                    if m == name:
                        colors.append(c)
                        break

        if not sizes:
            ax.text(0.5, 0.5, "No Appointments Data", horizontalalignment="center", verticalalignment="center",
                    transform=ax.transAxes, color="#94A3B8", fontsize=11)
            ax.axis("off")
        else:
            total = sum(sizes)
            wedges, _ = ax.pie(
                sizes,
                colors=colors,
                startangle=90,
                counterclock=False,
                radius=1.0,
                wedgeprops=dict(width=0.32, edgecolor="#FFFFFF", linewidth=2.5),
            )
            ax.text(0, 0.08, str(total), ha="center", va="center", fontsize=18, fontweight="bold", color="#0F172A")
            ax.text(0, -0.14, "TOTAL", ha="center", va="center", fontsize=8, fontweight="bold", color="#64748B")

            handles = [
                Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8)
                for c in colors
            ]
            legend_labels = [
                f"{l}: {s} ({s / total * 100:.0f}%)"
                for l, s in zip(labels, sizes)
            ]
            ax.legend(
                handles,
                legend_labels,
                loc="center left",
                bbox_to_anchor=(1.08, 0.5),
                frameon=False,
                fontsize=9,
                labelcolor="#0F172A",
                handlelength=1.0,
                handletextpad=0.6,
                borderaxespad=0,
            )

        self._fig1.subplots_adjust(left=0.04, right=0.50, top=0.92, bottom=0.08)
        self._canvas1.draw()

    def _draw_physician_chart(self, physician_counts: dict) -> None:
        self._fig2.clear()
        ax = self._fig2.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        docs = []
        counts = []
        for doc, count in sorted(physician_counts.items(), key=lambda x: x[1]):
            short_name = doc.replace("Dr. ", "")
            docs.append(short_name)
            counts.append(count)

        if not counts:
            ax.text(0.5, 0.5, "No Consultations Data", horizontalalignment="center", verticalalignment="center",
                    transform=ax.transAxes, color="#94A3B8", fontsize=11)
            ax.axis("off")
        else:
            bars = ax.barh(docs, counts, color="#0284C7", height=0.55, edgecolor="none")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#E2E8F0")
            ax.spines["bottom"].set_color("#E2E8F0")
            ax.tick_params(colors="#64748B", labelsize=8)
            ax.xaxis.grid(True, linestyle="--", alpha=0.5, color="#E2E8F0")
            ax.set_axisbelow(True)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlim(0, max(counts) * 1.25 + 0.5)

            for bar in bars:
                w = bar.get_width()
                if w > 0:
                    ax.text(w + 0.12, bar.get_y() + bar.get_height() / 2, str(int(w)),
                            va="center", color="#0F172A", fontsize=8, weight="bold")

        self._fig2.subplots_adjust(left=0.28, right=0.92, top=0.92, bottom=0.12)
        self._canvas2.draw()

    def _populate_today_table(self, today_records: list[dict]) -> None:
        self._today_table.setRowCount(0)
        sorted_records = sorted(today_records, key=lambda x: str(x.get("time", "")))
        for row_idx, r in enumerate(sorted_records):
            self._today_table.insertRow(row_idx)

            id_item = QTableWidgetItem(str(r.get("id", "")))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._today_table.setItem(row_idx, 0, id_item)

            p_item = QTableWidgetItem(str(r.get("patient_name", "")))
            p_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self._today_table.setItem(row_idx, 1, p_item)

            d_item = QTableWidgetItem(str(r.get("physician", "")))
            d_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self._today_table.setItem(row_idx, 2, d_item)

            t_item = QTableWidgetItem(str(r.get("time", "")))
            t_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._today_table.setItem(row_idx, 3, t_item)

            s_item = QTableWidgetItem(str(r.get("status", "")))
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._today_table.setItem(row_idx, 4, s_item)
