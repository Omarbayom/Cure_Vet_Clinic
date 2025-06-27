# ui/add_visit.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QDateEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QTableWidget, QMessageBox,
    QToolButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect, QStackedLayout
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QDate

import db_manager

class AddVisitPage(QWidget):
    def __init__(self, on_back, on_show_history):
        super().__init__()
        self.on_back = on_back
        self.on_show_history = on_show_history
        self.selected_owner = None
        self.selected_pet   = None
        self.visit_id       = None

        self._build_ui()
        self.reset_visit_forms()

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, int(self.height() * 0.12))
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _build_ui(self):
        # base stylesheet: background + scrollbars + list/table borders
        self.setStyleSheet("""
            QWidget { background-color: #f2f2f2; }
            QListWidget, QTableWidget {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                width: 12px; background: #e0e0e0;
            }
            QScrollBar::handle:vertical {
                background: #00CED1; min-height: 20px; border-radius: 6px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0px; width: 0px;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)

        # header
        hdr = QHBoxLayout(); hdr.setContentsMargins(10,10,10,5)
        back = QToolButton(); back.setText("←"); back.setFont(QFont("Segoe UI",20))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            "QToolButton{color:white;background:transparent;border:none;}"
            "QToolButton:hover{color:#e0e0e0;}"
        )
        back.clicked.connect(self.on_back)
        hdr.addWidget(back, Qt.AlignLeft)
        title = QLabel("📋 Add Visit")
        title.setFont(QFont("Segoe UI",26,QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(title, Qt.AlignLeft)
        hdr.addStretch()
        main.addLayout(hdr)

        # panel with shadow
        panel = QFrame()
        panel.setStyleSheet("background:#e0e0e0; border-radius:8px;")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(15); shadow.setOffset(0,3); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        container = QVBoxLayout(panel)
        container.setContentsMargins(20,20,20,20)
        container.setSpacing(10)

        # helpers
        def mk_lineedit(w):
            w.setFont(QFont("Segoe UI",18))
            w.setStyleSheet(
                "background:white; border:1px solid #ccc;"
                " border-radius:4px; padding:6px 10px;"
            )
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return w

        def mk_list(w):
            w.setFont(QFont("Segoe UI",18))
            w.setStyleSheet(
                "background:white; border:1px solid #ccc; border-radius:4px;"
            )
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return w

        btn_style = (
            "QPushButton{background:white; border:2px solid #00CED1;"
            " border-radius:6px; padding:8px 16px; font:18pt 'Segoe UI';}"
            "QPushButton:hover{background:#e0ffff;}"
        )

        # stacked wizard layout
        self.stack = QStackedLayout()

        # Page 0: Search & History
        page0 = QWidget()
        p0 = QVBoxLayout(page0); p0.setSpacing(8)
        p0.addWidget(QLabel("Search Owner:"))
        self.search_input = mk_lineedit(QLineEdit())
        self.search_input.setPlaceholderText("Name or phone…")
        self.search_input.textChanged.connect(self.on_search_owner)
        p0.addWidget(self.search_input)

        p0.addWidget(QLabel("Owners:"))
        self.owner_list = mk_list(QListWidget())
        self.owner_list.itemClicked.connect(self.on_owner_selected)
        p0.addWidget(self.owner_list, stretch=1)

        p0.addWidget(QLabel("Pets:"))
        self.pet_list = mk_list(QListWidget())
        self.pet_list.itemClicked.connect(self.on_pet_selected)
        p0.addWidget(self.pet_list, stretch=1)

        p0.addWidget(QLabel("Recent Visits:"))
        self.history_list = mk_list(QListWidget())
        self.history_list.itemClicked.connect(self._show_history_detail)
        p0.addWidget(self.history_list, stretch=1)

        next0 = QPushButton("Next: Visit Details"); next0.setStyleSheet(btn_style)
        next0.clicked.connect(lambda: self._goto(1))
        p0.addWidget(next0)
        self.stack.addWidget(page0)

        # Page 1: Visit Details
        page1 = QWidget()
        p1 = QVBoxLayout(page1); p1.setSpacing(8)
        p1.addWidget(QLabel("Doctor Name:"))
        self.dr_name = mk_lineedit(QLineEdit())
        p1.addWidget(self.dr_name)

        p1.addWidget(QLabel("Notes:"))
        self.notes = QTextEdit()
        self.notes.setFont(QFont("Segoe UI",18))
        self.notes.setStyleSheet("background:white; border:1px solid #ccc;")
        p1.addWidget(self.notes, stretch=1)

        p1.addWidget(QLabel("Next Appointment:"))
        self.next_date = QDateEdit(calendarPopup=True)
        self.next_date.setFont(QFont("Segoe UI",18))
        self.next_date.setDate(QDate.currentDate())
        # style the date edit dropdown & scrollbars
        self.next_date.setStyleSheet("""
            QDateEdit {
              background:white; border:1px solid #ccc;
              border-radius:4px; padding:6px 10px;
            }
            QDateEdit::drop-down { border:none; }
            QCalendarWidget QToolButton {
              background: #00CED1; color:white; border:none;
            }
        """)
        p1.addWidget(self.next_date)

        nav1 = QHBoxLayout()
        back1 = QPushButton("← Back"); back1.setStyleSheet(btn_style)
        back1.clicked.connect(lambda: self._goto(0))
        next1 = QPushButton("Next: Prescriptions"); next1.setStyleSheet(btn_style)
        next1.clicked.connect(self._save_visit_and_next)
        nav1.addWidget(back1); nav1.addStretch(); nav1.addWidget(next1)
        p1.addLayout(nav1)
        self.stack.addWidget(page1)

        # Page 2: Prescriptions
        page2 = QWidget()
        p2 = QVBoxLayout(page2); p2.setSpacing(8)
        p2.addWidget(QLabel("Prescriptions:"))
        self.pres_table = QTableWidget(0,5)
        self.pres_table.setFont(QFont("Segoe UI",18))
        self.pres_table.setHorizontalHeaderLabels(
            ["Source","Medicine","Batch","Qty","Unit Price"]
        )
        p2.addWidget(self.pres_table, stretch=1)

        nav2 = QHBoxLayout()
        back2 = QPushButton("← Back"); back2.setStyleSheet(btn_style)
        back2.clicked.connect(lambda: self._goto(1))
        add2 = QPushButton("Add Medicine"); add2.setStyleSheet(btn_style)
        add2.clicked.connect(self.on_add_pres_row)
        save2 = QPushButton("Save All"); save2.setStyleSheet(btn_style)
        save2.clicked.connect(self.on_save_prescriptions)
        self.save_pres_btn = save2
        nav2.addWidget(back2); nav2.addStretch()
        nav2.addWidget(add2); nav2.addWidget(save2)
        p2.addLayout(nav2)
        self.stack.addWidget(page2)

        # Page 3: History Detail
        page3 = QWidget()
        p3 = QVBoxLayout(page3); p3.setSpacing(8)
        p3.addWidget(QLabel("Visit Details"))
        self.detail_text = QTextEdit(); self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Segoe UI",16))
        self.detail_text.setStyleSheet("background:white; border:1px solid #ccc;")
        p3.addWidget(self.detail_text, stretch=1)

        nav3 = QHBoxLayout()
        back3 = QPushButton("← Back to History"); back3.setStyleSheet(btn_style)
        back3.clicked.connect(lambda: self._goto(0))
        nv3 = QPushButton("➕ Add New Visit"); nv3.setStyleSheet(btn_style)
        nv3.clicked.connect(lambda: self._goto(1))
        nav3.addWidget(back3); nav3.addStretch(); nav3.addWidget(nv3)
        p3.addLayout(nav3)
        self.stack.addWidget(page3)

        container.addLayout(self.stack)
        main.addWidget(panel)

    def reset_visit_forms(self):
        self.selected_owner = None
        self.selected_pet   = None
        self.visit_id       = None
        # Page 0
        self.search_input.clear()
        self.owner_list.clear()
        self.pet_list.clear()
        self.history_list.clear()
        # Page 1
        self.dr_name.clear()
        self.notes.clear()
        self.next_date.setDate(QDate.currentDate())
        # Page 2
        self.pres_table.setRowCount(0)
        self.pres_table.setEnabled(False)
        self.save_pres_btn.setEnabled(False)
        self._goto(0)

    def _goto(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def _save_visit_and_next(self):
        if not (self.selected_owner and self.selected_pet and self.dr_name.text().strip()):
            QMessageBox.warning(self, "Missing Data",
                                "Select owner, pet, and enter doctor name first.")
            return
        self.visit_id = db_manager.add_visit({
            'pet_id':           self.selected_pet['id'],
            'visit_date':       QDate.currentDate().toString("yyyy-MM-dd"),
            'notes':            self.notes.toPlainText(),
            'next_appointment': self.next_date.date().toString("yyyy-MM-dd"),
            'doctor_name':      self.dr_name.text().strip()
        })
        self.pres_table.setEnabled(True)
        self.save_pres_btn.setEnabled(True)
        self._goto(2)

    def _show_history_detail(self, item):
        v = item.data
        txt = (f"Date: {v['visit_date']}\n"
               f"Doctor: {v.get('doctor_name','—')}\n"
               f"Next Appt: {v['next_appointment']}\n\n"
               f"{v['notes']}\n\nDispensed:\n")
        prescs = db_manager.get_prescriptions_by_visit(v['id'])
        if prescs:
            for p in prescs:
                src = "Inventory" if p['is_inventory'] else "Pharmacy"
                name = p['item_name'] if p['is_inventory'] else p['med_name']
                txt += f" • [{src}] {name}: {p['quantity']}\n"
        else:
            txt += "None"
        self.detail_text.setPlainText(txt)
        self._goto(3)

    def on_search_owner(self, text):
        term = text.strip()
        self.owner_list.clear()
        self.pet_list.clear()
        self.history_list.clear()
        results = []
        if term.isdigit():
            o = db_manager.get_owner_by_phone(term)
            if o: results = [o]
        else:
            results = db_manager.find_owners_by_name(term)
        for o in results:
            itm = QListWidgetItem(f"{o['name']} — {o['phone']}")
            itm.data = o
            self.owner_list.addItem(itm)

    def on_owner_selected(self, item):
        self.selected_owner = item.data
        self.pet_list.clear()
        self.history_list.clear()
        for species, petname in db_manager.get_pets_by_owner(self.selected_owner['id']):
            pi = QListWidgetItem(f"{petname} ({species})")
            pi.data = {'species': species, 'pet_name': petname}
            self.pet_list.addItem(pi)

    def on_pet_selected(self, item):
        info = item.data
        self.selected_pet = db_manager.find_pet(
            self.selected_owner['id'], info['species'], info['pet_name']
        )
        self.history_list.clear()
        for v in db_manager.get_visits_by_pet(self.selected_pet['id']):
            wi = QListWidgetItem(f"{v['visit_date']}: {v['notes'][:40]}…")
            wi.data = v
            self.history_list.addItem(wi)

    def on_add_pres_row(self):
        row = self.pres_table.rowCount()
        self.pres_table.insertRow(row)
        src = QComboBox()
        if db_manager.get_all_inventory():
            src.addItem("Inventory")
        src.addItem("Pharmacy")
        src.currentTextChanged.connect(lambda t,r=row: self.on_source_changed(r, t))
        self.pres_table.setCellWidget(row, 0, src)
        self.pres_table.setCellWidget(row, 1, QLineEdit())
        self.pres_table.setCellWidget(row, 2, QLabel(""))
        qty = QSpinBox(); qty.setMaximum(999)
        pr  = QDoubleSpinBox(); pr.setMinimum(0)
        self.pres_table.setCellWidget(row, 3, qty)
        self.pres_table.setCellWidget(row, 4, pr)
        self.on_source_changed(row, src.currentText())

    def on_source_changed(self, row, source):
        if source == "Inventory":
            combo = QComboBox()
            for m in db_manager.get_all_inventory():
                combo.addItem(m['name'], m)
            combo.currentTextChanged.connect(lambda n,r=row: self.load_batches(r, n))
            self.pres_table.setCellWidget(row, 1, combo)
            batch = QComboBox()
            self.pres_table.setCellWidget(row, 2, batch)
            self.load_batches(row, combo.currentText())
        else:
            self.pres_table.setCellWidget(row, 1, QLineEdit())
            self.pres_table.setCellWidget(row, 2, QLabel("N/A"))

    def load_batches(self, row, med_name):
        batch_combo = self.pres_table.cellWidget(row, 2)
        batch_combo.clear()
        for b in db_manager.get_inventory_batches(med_name):
            batch_combo.addItem(f"{b['expiration_date']} (stock:{b['quantity']})", b)

    def on_save_prescriptions(self):
        for r in range(self.pres_table.rowCount()):
            source = self.pres_table.cellWidget(r, 0).currentText()
            is_inv = (source == "Inventory")
            if is_inv:
                combo = self.pres_table.cellWidget(r, 1)
                batch = self.pres_table.cellWidget(r, 2).currentData()
                inv_id = batch['id']
                available = batch['quantity']
                qty = self.pres_table.cellWidget(r, 3).value()
                if qty > available:
                    QMessageBox.warning(self, "Stock Error",
                                        f"{batch['name']}: {qty} > {available}")
                    return
            else:
                inv_id = None
                qty = self.pres_table.cellWidget(r, 3).value()
            price = self.pres_table.cellWidget(r, 4).value() or (batch.get('default_sell_price', 0) if is_inv else 0)
            db_manager.add_prescription({
                'visit_id':     self.visit_id,
                'inventory_id': inv_id,
                'med_name':     None if is_inv else self.pres_table.cellWidget(r, 1).text(),
                'is_inventory': int(is_inv),
                'quantity':     qty,
                'unit_price':   price
            })
            if is_inv:
                new_qty = available - qty
                db_manager.update_inventory_quantity(inv_id, new_qty)

        QMessageBox.information(self, "Done", "Prescriptions saved.")
        self.reset_visit_forms()
