# ui/add_inventory.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout, QMessageBox,
    QFrame, QSizePolicy, QToolButton, QGraphicsDropShadowEffect,
    QApplication
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QDate

from db_manager import add_or_restock_inventory

class AddInventoryPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()

    def paintEvent(self, event):
        # Teal gradient header
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, int(self.height() * 0.12))
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _build_ui(self):
        self.setStyleSheet("background-color: #f2f2f2;")
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Back Arrow ──
        top = QHBoxLayout()
        top.setContentsMargins(10, 10, 10, 5)
        back = QToolButton()
        back.setText("←")
        back.setFont(QFont("Segoe UI", 20))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            "QToolButton { color:white; background:transparent; border:none; }"
            "QToolButton:hover { color:#e0e0e0; }"
        )
        back.clicked.connect(self.on_back)
        top.addWidget(back, Qt.AlignLeft)
        main.addLayout(top)

        # ── Header ──
        hdr = QHBoxLayout()
        hdr.addStretch()
        plus = QLabel("➕"); plus.setFont(QFont("Segoe UI", 26))
        plus.setStyleSheet("color:white; background:transparent;")
        title = QLabel("Add / Restock Inventory")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(plus)
        hdr.addWidget(title)
        hdr.addStretch()
        main.addLayout(hdr)

        # ── Form Panel ──
        panel = QFrame()
        panel.setStyleSheet("QFrame{background:#e0e0e0;border-radius:8px;}")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(15); shadow.setOffset(0, 3); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # container layout for form + buttons
        content = QVBoxLayout(panel)
        content.setContentsMargins(20, 20, 20, 20)
        content.setSpacing(15)

        # form layout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft|Qt.AlignTop)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(18)

        def mk(widget):
            widget.setFont(QFont("Segoe UI", 18))
            widget.setStyleSheet("""
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                min-height: 40px;
            """)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if isinstance(widget, QDateEdit):
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd MMMM yyyy")
            return widget

        def lbl(text):
            l = QLabel(text)
            l.setFont(QFont("Segoe UI", 18))
            l.setStyleSheet("color:#333;")
            return l

        # ── Form Fields ──
        self.name_input       = mk(QLineEdit());      self.name_input.setPlaceholderText("Item name")
        self.category_input   = mk(QLineEdit());      self.category_input.setPlaceholderText("Category")
        self.unit_input       = mk(QLineEdit());      self.unit_input.setPlaceholderText("Unit (e.g. tablet)")
        self.qty_input        = mk(QSpinBox());       self.qty_input.setRange(1, 100000)
        self.reorder_input    = mk(QSpinBox());       self.reorder_input.setRange(0, 100000)
        self.exp_input        = mk(QDateEdit())
        self.default_price_in = mk(QDoubleSpinBox()); self.default_price_in.setRange(0, 1e6)
        self.pur_date_input   = mk(QDateEdit())
        self.pur_price_input  = mk(QDoubleSpinBox()); self.pur_price_input.setRange(0, 1e6)

        for label_text, widget in [
            ("Name*:",             self.name_input),
            ("Category*:",         self.category_input),
            ("Unit*:",             self.unit_input),
            ("Quantity*:",         self.qty_input),
            ("Reorder Level:",     self.reorder_input),
            ("Expiry Date*:",      self.exp_input),
            ("Default Sell Price:",self.default_price_in),
            ("Purchase Date*:",    self.pur_date_input),
            ("Purchase Cost*:",    self.pur_price_input),
        ]:
            form.addRow(lbl(label_text), widget)

        content.addLayout(form)

        # ── Save / Cancel Buttons ──
        btn_h = QHBoxLayout()
        btn_h.setContentsMargins(0, 10, 0, 0)

        save = QPushButton("💾 Save")
        save.setFont(QFont("Segoe UI", 18))
        save.setCursor(Qt.PointingHandCursor)
        save.setFixedSize(140, 45)
        save.setStyleSheet(
            "QPushButton{background:#009999;color:white;border-radius:4px;}"
            "QPushButton:hover{background:#008080}"
        )
        save.clicked.connect(self._save)

        cancel = QPushButton("✖ Cancel")
        cancel.setFont(QFont("Segoe UI", 18))
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setFixedSize(140, 45)
        cancel.setStyleSheet(
            "QPushButton{background:#b40000;color:white;border-radius:4px;}"
            "QPushButton:hover{background:#8a0000}"
        )
        cancel.clicked.connect(self.on_back)

        btn_h.addStretch()
        btn_h.addWidget(save)
        btn_h.addWidget(cancel)
        content.addLayout(btn_h)

        panel.setLayout(content)
        main.addWidget(panel, alignment=Qt.AlignCenter)

        # set default dates
        today = QDate.currentDate()
        self.exp_input.setDate(today)
        self.pur_date_input.setDate(today)

    def _save(self):
        name    = self.name_input.text().strip()
        cat     = self.category_input.text().strip()
        unit    = self.unit_input.text().strip()
        qty     = self.qty_input.value()
        reorder = self.reorder_input.value()
        exp     = self.exp_input.date().toPyDate().isoformat()
        sell    = self.default_price_in.value()
        pdate   = self.pur_date_input.date().toPyDate().isoformat()
        cost    = self.pur_price_input.value()

        if not all([name, cat, unit, qty, exp, pdate, cost]):
            QMessageBox.warning(self, "Validation Error", "Please fill all required fields.")
            return

        batch = {
            'name':               name,
            'category':           cat,
            'quantity':           qty,
            'unit':               unit,
            'reorder_level':      reorder,
            'expiration_date':    exp,
            'default_sell_price': sell,
            'purchase_date':      pdate,
            'purchase_price':     cost
        }
        try:
            add_or_restock_inventory(batch)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(self, "Success", "Inventory updated.")
        self.on_back()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AddInventoryPage(on_back=app.quit)
    w.resize(980, 700)
    w.show()
    sys.exit(app.exec_())
