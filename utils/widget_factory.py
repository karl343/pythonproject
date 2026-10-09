from __future__ import annotations

from PyQt6.QtCore import QDate, QRectF, QTime, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from utils.constants import COLOUR

_STATUS_COLOURS: dict[str, dict[str, str]] = {
    "Scheduled":                {"fg": "#0284C7", "bg": "#E0F2FE"},
    "Completed":                {"fg": "#16A34A", "bg": "#DCFCE7"},
    "Successful":               {"fg": "#16A34A", "bg": "#DCFCE7"},
    "Completed (Successful)":   {"fg": "#16A34A", "bg": "#DCFCE7"},
    "Cancelled":                {"fg": "#DC2626", "bg": "#FEE2E2"},
    "No Show":                  {"fg": "#D97706", "bg": "#FEF3C7"},
    "Not Successful":           {"fg": "#DC2626", "bg": "#FEE2E2"},
    "No Show (Not Successful)": {"fg": "#D97706", "bg": "#FEF3C7"},
}

class StatusPillDelegate(QStyledItemDelegate):

    def paint(self, painter: QPainter, option, index) -> None:
        status_text = index.data(Qt.ItemDataRole.DisplayRole)
        if not status_text:
            super().paint(painter, option, index)
            return

        colors = _STATUS_COLOURS.get(
            status_text,
            {"fg": COLOUR["text_main"], "bg": COLOUR["header_bg"]},
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#E0F2FE"))
        else:
            if index.row() % 2 == 1:
                painter.fillRect(option.rect, QColor(COLOUR["table_alt"]))
            else:
                painter.fillRect(option.rect, QColor(COLOUR["card_bg"]))

        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(status_text)
        pill_w = min(option.rect.width() - 16, text_width + 24)
        pill_h = 24
        x = option.rect.x() + (option.rect.width() - pill_w) / 2.0
        y = option.rect.y() + (option.rect.height() - pill_h) / 2.0

        pill_rect = QRectF(x, y, pill_w, pill_h)
        painter.setBrush(QColor(colors["bg"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(pill_rect, 12.0, 12.0)

        painter.setFont(font)
        painter.setPen(QColor(colors["fg"]))
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, status_text)

        painter.restore()

def make_label(text: str, bold: bool = False, size: int = 10, colour: str = "") -> QLabel:
    lbl = QLabel(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    lbl.setFont(font)
    if colour:
        lbl.setStyleSheet(f"color: {colour};")
    else:
        lbl.setStyleSheet(f"color: {COLOUR['text_main']};")
    return lbl

def make_button(text: str, colour: str = COLOUR["accent"], text_colour: str = "#FFFFFF") -> QPushButton:
    btn = QPushButton(text)
    btn.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedHeight(38)

    q_col = QColor(colour)
    hover_col = q_col.darker(112).name()
    pressed_col = q_col.darker(125).name()

    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {colour};
            color: {text_colour};
            border: none;
            border-radius: 6px;
            padding: 0 18px;
        }}
        QPushButton:hover {{
            background-color: {hover_col};
        }}
        QPushButton:pressed {{
            background-color: {pressed_col};
        }}
        QPushButton:disabled {{
            background-color: #E2E8F0;
            color: #94A3B8;
        }}
    """)
    return btn

def make_secondary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setFont(QFont("Segoe UI", 10))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedHeight(38)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #FFFFFF;
            color: {COLOUR["text_main"]};
            border: 1px solid {COLOUR["border"]};
            border-radius: 6px;
            padding: 0 16px;
        }}
        QPushButton:hover {{
            background-color: {COLOUR["header_bg"]};
            border-color: {COLOUR["input_border"]};
        }}
        QPushButton:pressed {{
            background-color: #E2E8F0;
        }}
        QPushButton:disabled {{
            background-color: #F8FAFC;
            color: #94A3B8;
            border-color: #E2E8F0;
        }}
    """)
    return btn

def make_input(placeholder: str = "") -> QLineEdit:
    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setFont(QFont("Segoe UI", 10))
    inp.setFixedHeight(38)
    inp.setStyleSheet(f"""
        QLineEdit {{
            background-color: {COLOUR["input_bg"]};
            color: {COLOUR["text_main"]};
            border: 1px solid {COLOUR["input_border"]};
            border-radius: 6px;
            padding: 0 12px;
        }}
        QLineEdit:focus {{
            border: 1.5px solid {COLOUR["accent"]};
            background-color: #FFFFFF;
        }}
    """)
    return inp

def make_combo(items: list[str]) -> QComboBox:
    combo = QComboBox()
    combo.addItems(items)
    combo.setFont(QFont("Segoe UI", 10))
    combo.setFixedHeight(38)
    combo.setStyleSheet(f"""
        QComboBox {{
            background-color: {COLOUR["input_bg"]};
            color: {COLOUR["text_main"]};
            border: 1px solid {COLOUR["input_border"]};
            border-radius: 6px;
            padding: 0 12px;
        }}
        QComboBox:focus {{
            border: 1.5px solid {COLOUR["accent"]};
        }}
        QComboBox QAbstractItemView {{
            background-color: {COLOUR["card_bg"]};
            color: {COLOUR["text_main"]};
            selection-background-color: #E0F2FE;
            selection-color: {COLOUR["accent"]};
            border: 1px solid {COLOUR["border"]};
            padding: 4px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
    """)
    return combo

def make_date_edit(date: QDate | None = None) -> QDateEdit:
    de = QDateEdit()
    de.setDisplayFormat("yyyy-MM-dd")
    de.setCalendarPopup(True)
    de.setDate(date or QDate.currentDate())
    de.setFixedHeight(38)
    de.setFont(QFont("Segoe UI", 10))
    de.setStyleSheet(f"""
        QDateEdit {{
            background-color: {COLOUR["input_bg"]};
            color: {COLOUR["text_main"]};
            border: 1px solid {COLOUR["input_border"]};
            border-radius: 6px;
            padding: 0 12px;
        }}
        QDateEdit:focus {{
            border: 1.5px solid {COLOUR["accent"]};
        }}
        QDateEdit::drop-down {{
            border: none;
            width: 24px;
        }}
    """)
    return de

def make_time_edit(time: QTime | None = None) -> QTimeEdit:
    te = QTimeEdit()
    te.setDisplayFormat("HH:mm")
    te.setTime(time or QTime(8, 0))
    te.setFixedHeight(38)
    te.setFont(QFont("Segoe UI", 10))
    te.setStyleSheet(f"""
        QTimeEdit {{
            background-color: {COLOUR["input_bg"]};
            color: {COLOUR["text_main"]};
            border: 1px solid {COLOUR["input_border"]};
            border-radius: 6px;
            padding: 0 12px;
        }}
        QTimeEdit:focus {{
            border: 1.5px solid {COLOUR["accent"]};
        }}
        QTimeEdit::drop-down {{
            border: none;
            width: 24px;
        }}
    """)
    return te

def make_table(columns: list[str]) -> QTableWidget:
    tbl = QTableWidget()
    tbl.setColumnCount(len(columns))
    tbl.setHorizontalHeaderLabels(columns)
    tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    tbl.verticalHeader().setVisible(False)
    tbl.verticalHeader().setDefaultSectionSize(40)
    tbl.setSortingEnabled(True)
    tbl.setAlternatingRowColors(True)
    tbl.setShowGrid(False)
    tbl.setFont(QFont("Segoe UI", 10))

    if len(columns) >= 7:
        tbl.setItemDelegateForColumn(6, StatusPillDelegate(tbl))

    header = tbl.horizontalHeader()
    header.setHighlightSections(False)
    header.setStretchLastSection(False)
    if len(columns) == 7:
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        tbl.setColumnWidth(6, 140)
    else:
        header.setStretchLastSection(True)

    tbl.setStyleSheet(f"""
        QTableWidget {{
            background-color: {COLOUR["card_bg"]};
            color: {COLOUR["text_main"]};
            border: 1px solid {COLOUR["border"]};
            border-radius: 8px;
            alternate-background-color: {COLOUR["table_alt"]};
        }}
        QTableWidget::item {{
            padding: 6px 12px;
            border: none;
        }}
        QTableWidget::item:selected {{
            background-color: #E0F2FE;
            color: {COLOUR["accent"]};
            font-weight: bold;
        }}
        QHeaderView::section {{
            background-color: {COLOUR["header_bg"]};
            color: {COLOUR["text_main"]};
            font-weight: bold;
            font-size: 11px;
            padding: 10px 12px;
            border: none;
            border-bottom: 2px solid {COLOUR["border"]};
        }}
        QScrollBar:vertical {{
            background: {COLOUR["bg_main"]};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {COLOUR["input_border"]};
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLOUR["text_dim"]};
        }}
        QScrollBar:horizontal {{
            background: {COLOUR["bg_main"]};
            height: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {COLOUR["input_border"]};
            border-radius: 4px;
        }}
    """)
    return tbl

def populate_table(table: QTableWidget, records: list[dict]) -> None:
    table.setSortingEnabled(False)
    table.setRowCount(0)
    for row_idx, appt in enumerate(records):
        table.insertRow(row_idx)
        values = [
            appt.get("id", ""),
            appt.get("patient_name", ""),
            appt.get("contact", ""),
            appt.get("physician", ""),
            str(appt.get("date", "")),
            str(appt.get("time", "")),
            appt.get("status", ""),
        ]
        for col_idx, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            if col_idx in (0, 4, 5):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            elif col_idx == 6:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            table.setItem(row_idx, col_idx, item)
    table.setSortingEnabled(True)

def make_stat_card(title: str, value: str, icon: str, accent_color: str, subtitle: str = "") -> QFrame:
    card = QFrame()
    card.setObjectName("statCard")
    card.setStyleSheet(f"""
        QFrame#statCard {{
            background-color: #FFFFFF;
            border: 1px solid {COLOUR["border"]};
            border-radius: 10px;
        }}
        QFrame#statCard QLabel {{
            border: none;
            background-color: transparent;
        }}
    """)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(18, 14, 18, 14)
    layout.setSpacing(4)

    top_row = QHBoxLayout()
    title_lbl = make_label(title.upper(), bold=True, size=8, colour=COLOUR["text_dim"])
    icon_lbl = make_label(icon, size=12)
    top_row.addWidget(title_lbl)
    top_row.addStretch()
    top_row.addWidget(icon_lbl)
    layout.addLayout(top_row)

    val_lbl = make_label(value, bold=True, size=16, colour=accent_color)
    layout.addWidget(val_lbl)

    if subtitle:
        sub_lbl = make_label(subtitle, size=8, colour=COLOUR["text_dim"])
        layout.addWidget(sub_lbl)

    return card
