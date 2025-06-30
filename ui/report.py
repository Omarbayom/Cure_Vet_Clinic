# ui/report_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect, QMessageBox, QCalendarWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,QDialog, QTextEdit
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QDate

import db_manager
class VisitDetailsDialog(QDialog):
    def __init__(self, visit):
        super().__init__()
        self.setWindowTitle("Visit Details")
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(12)

        # Basic fields
        for label, key in [
            ("Pet", "pet_name"),
            ("Owner", "owner"),
            ("Date", "visit_date"),
            ("Doctor", "doctor_name")
        ]:
            lbl = QLabel(f"<b>{label}:</b> {visit[key]}")
            lbl.setFont(QFont("Segoe UI", 18))
            layout.addWidget(lbl)

        # Notes
        # ── AFTER: notes + prescriptions table ──
        notes_lbl = QLabel("<b>Notes:</b>")
        notes_lbl.setFont(QFont("Segoe UI", 18))
        layout.addWidget(notes_lbl)

        notes_txt = QTextEdit()
        notes_txt.setReadOnly(True)
        notes_txt.setFont(QFont("Segoe UI", 16))
        notes_txt.setPlainText(visit["notes"])
        notes_txt.setMinimumHeight(100)
        layout.addWidget(notes_txt)

        # Prescriptions (if any)
        from db_manager import get_prescriptions_by_visit
        prescs = get_prescriptions_by_visit(visit["id"])
        if prescs:
            pres_lbl = QLabel("<b>Prescriptions:</b>")
            pres_lbl.setFont(QFont("Segoe UI", 18))
            layout.addWidget(pres_lbl)

            tbl = QTableWidget(len(prescs), 4)
            tbl.setHorizontalHeaderLabels(["Medicine", "Qty", "Unit Price", "Total"])
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            for r, p in enumerate(prescs):
                med = p["item_name"] or p["med_name"]
                tbl.setItem(r, 0, QTableWidgetItem(med))
                tbl.setItem(r, 1, QTableWidgetItem(str(p["quantity"])))
                tbl.setItem(r, 2, QTableWidgetItem(f"{p['unit_price']:.2f}"))
                tbl.setItem(r, 3, QTableWidgetItem(f"{p['quantity'] * p['unit_price']:.2f}"))
            layout.addWidget(tbl)

        # Prescriptions (if any)
        from db_manager import get_prescriptions_by_visit
        prescs = get_prescriptions_by_visit(visit["id"])
        if prescs:
            pres_lbl = QLabel("<b>Prescriptions:</b>")
            pres_lbl.setFont(QFont("Segoe UI", 18))
            layout.addWidget(pres_lbl)

            tbl = QTableWidget(len(prescs), 4)
            tbl.setHorizontalHeaderLabels(["Item", "Qty", "Unit Price", "Total"])
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            for r, p in enumerate(prescs):
                item = p.get("item_name") or p.get("med_name")
                tbl.setItem(r, 0, QTableWidgetItem(item))
                tbl.setItem(r, 1, QTableWidgetItem(str(p["quantity"])))
                tbl.setItem(r, 2, QTableWidgetItem(f"{p['unit_price']:.2f}"))
                tbl.setItem(r, 3, QTableWidgetItem(f"{p['quantity']*p['unit_price']:.2f}"))
            layout.addWidget(tbl)

        # Future appointments (if any)
        from db_manager import get_future_appointments_by_visit
        appts = get_future_appointments_by_visit(visit["id"])
        if appts:
            appt_lbl = QLabel("<b>Future Appointments:</b>")
            appt_lbl.setFont(QFont("Segoe UI", 18))
            layout.addWidget(appt_lbl)
            for a in appts:
                line = QLabel(f"{a['appointment_date']} — {a['reason']}")
                line.setFont(QFont("Segoe UI", 16))
                layout.addWidget(line)

class ReportPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()
        self.load_visits()

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, int(self.height()*0.12))
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def make_dateedit(self, initial_date: QDate) -> QDateEdit:
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setFont(QFont("Segoe UI", 22))
        date_edit.setDisplayFormat("dd MMMM yyyy")
        date_edit.setDate(initial_date)
        cal = QCalendarWidget()
        cal.setNavigationBarVisible(True)
        cal.setMinimumSize(360, 300)
        cal.setFont(QFont("Segoe UI", 16))
        date_edit.setCalendarWidget(cal)
        date_edit.setStyleSheet("""
            QDateEdit {
                background: white; border: 1px solid #ccc;
                border-radius: 4px; padding: 6px 10px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 25px; border-left: 1px solid #aaa;
            }
            QDateEdit::down-arrow {
                image: url(:/icons/calendar.png);
                width: 16px; height: 16px;
            }
        """)
        return date_edit

    def _build_ui(self):
        self.setStyleSheet("background-color: #f2f2f2;")
        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)

        hdr = QHBoxLayout(); hdr.setContentsMargins(10,10,10,5)
        back = QPushButton("\u2190")
        back.setFont(QFont("Segoe UI",26))
        back.setStyleSheet("color:white;background:transparent;border:none;")
        back.clicked.connect(self.on_back)
        hdr.addWidget(back, Qt.AlignLeft)

        title = QLabel("\ud83d\udcc8 Detailed Reports")
        title.setFont(QFont("Segoe UI",32, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(title, Qt.AlignLeft)
        hdr.addStretch()

        header = QFrame()
        header.setLayout(hdr)
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame { background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #009999, stop:1 #006666
            ); }
        """)
        main.addWidget(header)

        panel = QFrame()
        panel.setStyleSheet("background:#e0e0e0; border-radius:8px;")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(12); shadow.setOffset(0,2); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        body = QVBoxLayout(panel)
        body.setContentsMargins(20,20,20,20)
        body.setSpacing(20)

        row = QHBoxLayout()
        # both start and end default to today
        today = QDate.currentDate()
        self.start_date = self.make_dateedit(today)
        self.end_date   = self.make_dateedit(today)

        start_lbl = QLabel("Start Date:")
        start_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        end_lbl = QLabel("End Date:")
        end_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        row.addWidget(start_lbl); row.addWidget(self.start_date)
        row.addSpacing(20)
        row.addWidget(end_lbl); row.addWidget(self.end_date)
        body.addLayout(row)

        gen = QPushButton("\ud83d\udcca Generate Report")
        gen.setFont(QFont("Segoe UI", 20, QFont.Bold))
        gen.setStyleSheet("background:#007777;color:white;padding:12px;border-radius:10px;")
        gen.clicked.connect(self._on_generate)
        body.addWidget(gen, alignment=Qt.AlignRight)

        self.lbl_revenue = QLabel("Total Revenue: —")
        self.lbl_cost = QLabel("Total Cost: —")
        self.lbl_appointments = QLabel("Appointments: —")
        for lbl in [self.lbl_revenue, self.lbl_cost, self.lbl_appointments]:
            lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
            lbl.setStyleSheet("color: #333;")
            body.addWidget(lbl)

        btns = QHBoxLayout()
        for label, func in [
            ("\ud83d\udcb8 Purchases", self.load_purchases),
            ("\ud83d\udcb0 Sales", self.load_sales),
            ("\ud83d\udcc5 Visits", self.load_visits)
        ]:
            b = QPushButton(label)
            b.setFont(QFont("Segoe UI", 16))
            b.setStyleSheet("background:#007777;color:white;padding:10px;border-radius:8px;")
            b.clicked.connect(func)
            btns.addWidget(b)
        body.addLayout(btns)

        self.table = QTableWidget(0, 1)
        self.table.setFont(QFont("Segoe UI", 18))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # ── Hide the default row numbers ──
        self.table.verticalHeader().setVisible(False)
        # ── Remove grid lines and enable alternating row colors ──
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                font-size: 18px;
                border: none;
                border-radius: 8px;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #e0f7fa;
            }
            QHeaderView::section {
                background-color: #006666;
                color: #ffffff;
                font-weight: bold;
                font-size: 18px;
                padding: 10px;
                border: none;
            }
            /* Rounded corners on the top‐left and top‐right header cells */
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }
        """)
        body.addWidget(self.table)


        hide = QPushButton("\u274c Hide Table")
        hide.setFont(QFont("Segoe UI", 14))
        hide.setStyleSheet("background:#aaaaaa;color:white;padding:8px;border-radius:6px;")
        hide.clicked.connect(lambda: self.table.setVisible(False))
        body.addWidget(hide, alignment=Qt.AlignRight)

        main.addWidget(panel)

    def _on_generate(self):
        sd = self.start_date.date().toString("yyyy-MM-dd")
        ed = self.end_date.date().toString("yyyy-MM-dd")
        if sd > ed:
            QMessageBox.warning(self, "Invalid Range", "Start date must be before end date.")
            return
        stats = db_manager.get_revenue_and_cost(sd, ed)
        count = db_manager.get_appointment_count(sd, ed)
        self.lbl_revenue.setText(f"Total Revenue:  ${stats['revenue']:.2f}")
        self.lbl_cost.setText(f"Total Cost:     ${stats['cost']:.2f}")
        self.lbl_appointments.setText(f"Appointments:   {count}")

    def load_purchases(self):
        from db_manager import get_purchase_details
        sd = self.start_date.date().toString("yyyy-MM-dd")
        ed = self.end_date.date().toString("yyyy-MM-dd")
        rows = get_purchase_details(sd, ed)
        self._fill_table(rows, ["item", "quantity", "unit_cost", "total_cost", "purchase_date"],
                         ["Item", "Qty", "Unit Cost", "Total", "Date"])

    def load_sales(self):
        from db_manager import get_sales_details
        sd = self.start_date.date().toString("yyyy-MM-dd")
        ed = self.end_date.date().toString("yyyy-MM-dd")
        rows = get_sales_details(sd, ed)
        self._fill_table(rows, ["service", "owner", "quantity", "total", "visit_date"],
                         ["Service", "Owner", "Qty", "Total", "Date"])

    def load_visits(self):
        from db_manager import get_visit_report_details
        sd = self.start_date.date().toString("yyyy-MM-dd")
        ed = self.end_date.date().toString("yyyy-MM-dd")
        rows = get_visit_report_details(sd, ed)
        self.visit_rows = rows
        self._fill_table_with_details(rows)

    def _fill_table(self, rows, keys, headers):
        self.table.clear()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        self.table.setVisible(True)
        self.table.cellDoubleClicked.connect(self._on_notes_click)

        for r, row in enumerate(rows):
            for c, k in enumerate(keys):
                item = QTableWidgetItem(str(row.get(k, "")))
                self.table.setItem(r, c, item)
                if headers[c] == "Notes":
                    item.setForeground(QColor("blue"))
                    item.setToolTip("Click to view details")
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def _on_notes_click(self, row, column):
        if self.table.horizontalHeaderItem(column).text() != "Notes":
            return
        pet = self.table.item(row, 0).text()
        owner = self.table.item(row, 1).text()
        visit_date = self.table.item(row, 2).text()
        doctor = self.table.item(row, 3).text()
        notes = self.table.item(row, column).text()

        details = f"""
        <b>Pet:</b> {pet}<br>
        <b>Owner:</b> {owner}<br>
        <b>Date:</b> {visit_date}<br>
        <b>Doctor:</b> {doctor}<br>
        <b>Notes:</b><br>{notes}
        """
        QMessageBox.information(self, "Visit Details", details)

    def on_back(self):
        self.on_back()

    def _fill_table_with_details(self, rows):
        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Pet", "Owner", "Date", "Doctor", "Details"])
        self.table.setRowCount(len(rows))
        self.table.setVisible(True)

        # Remove old double‐click handler if present
        try:
            self.table.cellDoubleClicked.disconnect(self._on_notes_click)
        except Exception:
            pass

        for r, visit in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(visit["pet_name"]))
            self.table.setItem(r, 1, QTableWidgetItem(visit["owner"]))
            self.table.setItem(r, 2, QTableWidgetItem(visit["visit_date"]))
            self.table.setItem(r, 3, QTableWidgetItem(visit["doctor_name"]))

            btn = QPushButton("View Details")
            btn.setFont(QFont("Segoe UI", 16))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #006666;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #008080;
                }
                QPushButton:pressed {
                    background-color: #005757;
                }
            """)
            btn.clicked.connect(lambda _, r=r: self.show_visit_details(r))
            self.table.setCellWidget(r, 4, btn)


    def show_visit_details(self, row_index):
        dlg = VisitDetailsDialog(self.visit_rows[row_index])
        dlg.exec_()
