# ui/report_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QDate

import db_manager

class ReportPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()

    def paintEvent(self, event):
        # gradient header
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, int(self.height()*0.12))
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _build_ui(self):
        self.setStyleSheet("background-color: #f2f2f2;")

        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)

        # header bar
        hdr = QHBoxLayout(); hdr.setContentsMargins(10,10,10,5)
        back = QPushButton("←")
        back.setFont(QFont("Segoe UI",20))
        back.setStyleSheet("color:white;background:transparent;border:none;")
        back.clicked.connect(self.on_back)
        hdr.addWidget(back, Qt.AlignLeft)

        title = QLabel("📈 Status & Reports")
        title.setFont(QFont("Segoe UI",26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(title, Qt.AlignLeft)
        hdr.addStretch()

        header = QFrame()
        header.setLayout(hdr)
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame { background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #009999, stop:1 #006666
            ); }
        """)
        main.addWidget(header)

        # content panel
        panel = QFrame()
        panel.setStyleSheet("background:#e0e0e0; border-radius:8px;")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(12); shadow.setOffset(0,2); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        body = QVBoxLayout(panel)
        body.setContentsMargins(20,20,20,20)
        body.setSpacing(15)

        # date pickers
        row = QHBoxLayout()
        lbl1 = QLabel("Start Date:"); lbl1.setFont(QFont("Segoe UI",18))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setFont(QFont("Segoe UI",18))
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self._style_dateedit(self.start_date)

        lbl2 = QLabel("End Date:"); lbl2.setFont(QFont("Segoe UI",18))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setFont(QFont("Segoe UI",18))
        self.end_date.setDate(QDate.currentDate())
        self._style_dateedit(self.end_date)

        row.addWidget(lbl1); row.addWidget(self.start_date)
        row.addSpacing(20)
        row.addWidget(lbl2); row.addWidget(self.end_date)
        body.addLayout(row)

        # generate button
        gen = QPushButton("Generate Report")
        gen.setFont(QFont("Segoe UI",18))
        gen.setCursor(Qt.PointingHandCursor)
        gen.setStyleSheet(
            "QPushButton{background:white; border:2px solid #00CED1; border-radius:6px; padding:8px 16px;}"
            "QPushButton:hover{background:#e0ffff;}"
        )
        gen.clicked.connect(self._on_generate)
        body.addWidget(gen, alignment=Qt.AlignRight)

        # results labels
        self.lbl_revenue = QLabel("Total Revenue: —")
        self.lbl_revenue.setFont(QFont("Segoe UI",18))
        body.addWidget(self.lbl_revenue)

        self.lbl_cost = QLabel("Total Cost: —")
        self.lbl_cost.setFont(QFont("Segoe UI",18))
        body.addWidget(self.lbl_cost)

        self.lbl_appointments = QLabel("Number of Appointments: —")
        self.lbl_appointments.setFont(QFont("Segoe UI",18))
        body.addWidget(self.lbl_appointments)

        main.addWidget(panel)

    def _style_dateedit(self, widget: QDateEdit):
        widget.setCalendarPopup(True)
        widget.setStyleSheet(
            "QDateEdit { background:white; border:1px solid #ccc; border-radius:4px; padding:6px 10px; }"
            "QDateEdit::drop-down { border:none; }"
            "QCalendarWidget QToolButton { background:#00CED1; color:white; border:none; }"
        )

    def _on_generate(self):
        sd = self.start_date.date().toString("yyyy-MM-dd")
        ed = self.end_date.date().toString("yyyy-MM-dd")
        if sd > ed:
            QMessageBox.warning(self, "Invalid Range",
                                "Start date must be on or before end date.")
            return

        stats = db_manager.get_revenue_and_cost(sd, ed)
        cnt   = db_manager.get_appointment_count(sd, ed)

        self.lbl_revenue.setText(f"Total Revenue:  ${stats['revenue']:.2f}")
        self.lbl_cost.setText   (f"Total Cost:     ${stats['cost']:.2f}")
        self.lbl_appointments.setText(f"Appointments:   {cnt}")

    def on_back(self):
        # ensure calling the passed in callback
        self.on_back()
