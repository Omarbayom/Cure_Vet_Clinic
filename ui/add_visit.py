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


        # Page 1: Visit Details (goes next to Appointments)
        nav1 = QHBoxLayout()
        back1 = QPushButton("← Back"); back1.setStyleSheet(btn_style)
        back1.clicked.connect(lambda: self._goto(0))
        next1 = QPushButton("Next: Appointments"); next1.setStyleSheet(btn_style)
        next1.clicked.connect(self._save_visit_and_next)
        nav1.addWidget(back1); nav1.addStretch(); nav1.addWidget(next1)
        p1.addLayout(nav1)
        self.stack.addWidget(page1)

        # Page 2: Future Appointments (optional)
        page2 = QWidget()
        p2 = QVBoxLayout(page2); p2.setSpacing(8)
        p2.addWidget(QLabel("Future Appointments (optional):"))
        self.app_table = QTableWidget(0, 2)
        self.app_table.setFont(QFont("Segoe UI",18))
        self.app_table.setHorizontalHeaderLabels(["Date", "Reason"])
        p2.addWidget(self.app_table, stretch=1)

        add_app = QPushButton("➕ Add Date/Reason"); add_app.setStyleSheet(btn_style)
        add_app.clicked.connect(self.on_add_app_row)
        p2.addWidget(add_app, alignment=Qt.AlignLeft)

        nav2 = QHBoxLayout()
        back2 = QPushButton("← Back"); back2.setStyleSheet(btn_style)
        back2.clicked.connect(lambda: self._goto(1))
        next2 = QPushButton("Next: Prescriptions"); next2.setStyleSheet(btn_style)
        next2.clicked.connect(self._save_apps_and_next)
        nav2.addWidget(back2); nav2.addStretch(); nav2.addWidget(next2)
        p2.addLayout(nav2)
        self.stack.addWidget(page2)

        # Page 3: Prescriptions
        page3 = QWidget()
        p3 = QVBoxLayout(page3); p3.setSpacing(8)
        p3.addWidget(QLabel("Prescriptions:"))
        self.pres_table = QTableWidget(0,5)
        self.pres_table.setFont(QFont("Segoe UI",18))
        self.pres_table.setHorizontalHeaderLabels(
            ["Source","Medicine","Batch","Qty","Unit Price"]
        )
        p3.addWidget(self.pres_table, stretch=1)

        nav3 = QHBoxLayout()
        back3 = QPushButton("← Back"); back3.setStyleSheet(btn_style)
        back3.clicked.connect(self._confirm_leave_prescriptions)
        add3 = QPushButton("Add Medicine"); add3.setStyleSheet(btn_style)
        add3.clicked.connect(self.on_add_pres_row)
        save3 = QPushButton("Save All"); save3.setStyleSheet(btn_style)
        save3.clicked.connect(self.on_save_prescriptions)
        self.save_pres_btn = save3
        nav3.addWidget(back3); nav3.addStretch()
        nav3.addWidget(add3); nav3.addWidget(save3)
        p3.addLayout(nav3)
        self.stack.addWidget(page3)

        # Page 4: History Detail
        page4 = QWidget()
        p4 = QVBoxLayout(page4); p4.setSpacing(8)
        p4.addWidget(QLabel("Visit Details"))
        self.detail_text = QTextEdit(); self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Segoe UI",16))
        self.detail_text.setStyleSheet("background:white; border:1px solid #ccc;")
        p4.addWidget(self.detail_text, stretch=1)

        nav4 = QHBoxLayout()
        back4 = QPushButton("← Back to History"); back4.setStyleSheet(btn_style)
        back4.clicked.connect(lambda: self._goto(0))
        nv4 = QPushButton("➕ Add New Visit"); nv4.setStyleSheet(btn_style)
        nv4.clicked.connect(lambda: self._goto(1))
        nav4.addWidget(back4); nav4.addStretch(); nav4.addWidget(nv4)
        p4.addLayout(nav4)
        self.stack.addWidget(page4)

        # finish layout
        container.addLayout(self.stack)
        main.addWidget(panel)

    def reset_visit_forms(self):
        self.selected_owner = None
        self.selected_pet   = None
        self.visit_id       = None

        # Page 0: clear search/history
        self.search_input.clear()
        self.owner_list.clear()
        self.pet_list.clear()
        self.history_list.clear()

        # Page 1: clear doctor & notes
        self.dr_name.clear()
        self.notes.clear()

        # Page 2: clear future‐appointments table
        self.app_table.setRowCount(0)

        # Page 3: clear prescriptions table
        self.pres_table.setRowCount(0)
        self.pres_table.setEnabled(False)
        self.save_pres_btn.setEnabled(False)

        # back to start
        self._goto(0)

    def _goto(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def _save_visit_and_next(self):
        if not (self.selected_owner and self.selected_pet and self.dr_name.text().strip()):
            QMessageBox.warning(self, "Missing Data",
                                "Select owner, pet, and enter doctor name first.")
            return
        self.visit_data = {
            'pet_id':           self.selected_pet['id'],
            'visit_date':       QDate.currentDate().toString("yyyy-MM-dd"),
            'notes':            self.notes.toPlainText(),
            'doctor_name':      self.dr_name.text().strip()
        }
        self.pres_table.setEnabled(True)
        self.save_pres_btn.setEnabled(True)
        self._goto(2)

    def _confirm_leave_prescriptions(self):
        # if no rows, go straight back
        if self.pres_table.rowCount() == 0:
            return self._goto(1)

        # otherwise ask first
        resp = QMessageBox.question(
            self,
            "Unsaved Medicines",
            "You have added one or more medicines but haven’t saved yet.\n"
            "If you go back now, these will be lost.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self._goto(1)

    def _show_history_detail(self, item):
        v = item.data
        # base visit info
        txt = (f"Date: {v['visit_date']}\n"
               f"Doctor: {v.get('doctor_name','—')}\n\n"
               f"{v['notes']}\n\nDispensed:\n")
        # prescriptions
        prescs = db_manager.get_prescriptions_by_visit(v['id'])
        if prescs:
            for p in prescs:
                src  = "Inventory" if p['is_inventory'] else "Pharmacy"
                name = p['item_name'] if p['is_inventory'] else p['med_name']
                txt += f" • [{src}] {name}: {p['quantity']}\n"
        else:
            txt += "None\n"

        # — now load future appointments —
        apps = db_manager.get_future_appointments_by_visit(v['id'])
        if apps:
            txt += "\nFuture Appointments:\n"
            for a in apps:
                txt += f" • {a['appointment_date']} — {a['reason'] or '—'}\n"

        self.detail_text.setPlainText(txt)
        self._goto(4)


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
            date   = v.get('visit_date', '')
            doctor = v.get('doctor_name', 'Unknown')
            # show date + doctor up front, then a snippet of notes
            wi = QListWidgetItem(f"{date} — Dr. {doctor}…")
            wi.data = v
            self.history_list.addItem(wi)


    def on_add_pres_row(self):
        row = self.pres_table.rowCount()
        self.pres_table.insertRow(row)

        src = QComboBox()
        # re-check inventory stock every time you add a medicine row
        items = db_manager.get_all_inventory()
        if any(item.get('quantity', 0) > 0 for item in items):
            src.addItem("Inventory")
        src.addItem("Pharmacy")

        src.currentTextChanged.connect(lambda t, r=row: self.on_source_changed(r, t))
        self.pres_table.setCellWidget(row, 0, src)

        # placeholder for medicine name / widget
        self.pres_table.setCellWidget(row, 1, QLineEdit())
        # placeholder for batch combo or label
        self.pres_table.setCellWidget(row, 2, QLabel(""))

        # qty and price
        qty = QSpinBox()
        qty.setMaximum(999)
        self.pres_table.setCellWidget(row, 3, qty)

        pr = QDoubleSpinBox()
        pr.setMinimum(0)
        pr.setMaximum(9999999999999999.99)
        self.pres_table.setCellWidget(row, 4, pr)

        # initialize the row’s widgets based on current source selection
        self.on_source_changed(row, src.currentText())

    def on_source_changed(self, row, source):
        if source == "Inventory":
            combo = QComboBox()
            # only include medications with quantity > 0
            for m in db_manager.get_all_inventory():
                if m.get('quantity', 0) > 0:
                    combo.addItem(m['name'], m)
            combo.currentTextChanged.connect(lambda n, r=row: self.load_batches(r, n))
            self.pres_table.setCellWidget(row, 1, combo)

            batch = QComboBox()
            self.pres_table.setCellWidget(row, 2, batch)
            self.load_batches(row, combo.currentText())
        else:
            self.pres_table.setCellWidget(row, 1, QLineEdit())
            self.pres_table.setCellWidget(row, 2, QLabel("N/A"))

    def load_batches(self, row, med_name):
        batch_combo = self.pres_table.cellWidget(row, 2)
        price_spin  = self.pres_table.cellWidget(row, 4)

        batch_combo.clear()
        # only include batches that still have stock > 0
        batches = [
            b for b in db_manager.get_inventory_batches(med_name)
            if b.get('quantity', 0) > 0
        ]

        for b in batches:
            batch_combo.addItem(
                f"{b['expiration_date']} (stock:{b['quantity']})",
                b
            )

        if batches:
            # pre-fill price with the first batch’s default_sell_price
            price_spin.setValue(batches[0].get('default_sell_price', 0.0))
        else:
            price_spin.setValue(0.0)

        # update price whenever a different batch is selected
        batch_combo.currentIndexChanged.connect(
            lambda idx, r=row: self._update_price_for_row(r)
        )


    def _update_price_for_row(self, row):
        batch_combo = self.pres_table.cellWidget(row, 2)
        price_spin  = self.pres_table.cellWidget(row, 4)
        batch = batch_combo.currentData()
        if batch:
            price_spin.setValue(batch.get('default_sell_price', 0.0))
        else:
            price_spin.setValue(0.0)

    def on_save_prescriptions(self):
        row_count = self.pres_table.rowCount()

        # 1) Create the visit record regardless of prescription rows
        try:
            self.visit_id = db_manager.add_visit(self.visit_data)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Visit", str(e))
            return

        # 1a) Save all Future Appointments
        for app in self.visit_data.get('future_appointments', []):
            date   = app['date']
            reason = app['reason']
            # ensure reason exists (adds if new)
            rid = db_manager.add_reason(reason) if reason else None
            db_manager.add_future_appointment(self.visit_id, date, rid)


        # 2) If no prescriptions were added, we’re done
        if row_count == 0:
            QMessageBox.information(
                self,
                "Visit Saved",
                "Visit has been saved (no medications added)."
            )
            self.reset_visit_forms()
            return

        # 3) Loop through each prescription row
        for row in range(row_count):
            source = self.pres_table.cellWidget(row, 0).currentText()
            is_inv = (source == "Inventory")

            qty_widget   = self.pres_table.cellWidget(row, 3)
            price_widget = self.pres_table.cellWidget(row, 4)
            qty   = qty_widget.value()
            price = price_widget.value()

            if is_inv:
                batch_combo = self.pres_table.cellWidget(row, 2)
                batch       = batch_combo.currentData() or {}
                inv_id      = batch.get('id')
                available   = batch.get('quantity', 0)

                if qty > available:
                    QMessageBox.warning(
                        self,
                        "Insufficient Stock",
                        f"Requested {qty}, but only {available} available for batch "
                        f"{batch.get('expiration_date','?')}."
                    )
                    return

                med_name = None
            else:
                med_item = self.pres_table.cellWidget(row, 1)
                med_name = med_item.text().strip() or None
                inv_id   = None

            # insert prescription
            try:
                db_manager.add_prescription({
                    'visit_id':     self.visit_id,
                    'inventory_id': inv_id,
                    'med_name':     med_name,
                    'is_inventory': int(is_inv),
                    'quantity':     qty,
                    'unit_price':   price
                })
            except Exception as e:
                QMessageBox.critical(self, "Error Saving Prescription", str(e))
                return

            # deduct stock if from inventory
            if is_inv:
                new_qty = available - qty
                try:
                    db_manager.update_inventory_quantity(inv_id, new_qty)
                except Exception as e:
                    QMessageBox.critical(self, "Error Updating Stock", str(e))
                    return

        # 4) All done!
        QMessageBox.information(
            self,
            "Done",
            "Visit and all prescriptions have been saved."
        )
        self.reset_visit_forms()

    def set_context(self, owner: dict, pet: dict):
        """
        Called when user clicks “Add New Visit” on the history page.
        Pre-selects the owner/pet, loads recent visits, and resets the wizard.
        """
        # 1. reset everything and go to page 0
        self.reset_visit_forms()
        self._goto(0)

        # 2. stash owner/pet
        self.selected_owner = owner
        self.selected_pet   = pet

        # 3. populate owner_list with just this owner
        from PyQt5.QtWidgets import QListWidgetItem
        self.owner_list.clear()
        oi = QListWidgetItem(f"{owner['name']} — {owner['phone']}")
        oi.data = owner
        self.owner_list.addItem(oi)
        self.owner_list.setCurrentItem(oi)

        # 4. populate pet_list and select this pet
        self.pet_list.clear()
        for species, petname in db_manager.get_pets_by_owner(owner['id']):
            pi = QListWidgetItem(f"{petname} ({species})")
            pi.data = {'species': species, 'pet_name': petname}
            self.pet_list.addItem(pi)
            if petname == pet['pet_name'] and species == pet['species']:
                self.pet_list.setCurrentItem(pi)
                # fire the selection logic
                self.on_pet_selected(pi)

        # 5. load that pet’s recent visits into history_list
        self.history_list.clear()
        for v in db_manager.get_visits_by_pet(pet['id']):
            wi = QListWidgetItem(f"{v['visit_date']}: {v['notes'][:40]}…")
            wi.data = v
            self.history_list.addItem(wi)

        # 6. move to page 1 (Visit Details) so they can start entering data
        self._goto(1)

    def on_add_app_row(self):
        """Insert a new row for date+reason."""
        row = self.app_table.rowCount()
        self.app_table.insertRow(row)

        # create a date edit with a styled popup calendar
        date_edit = QDateEdit(calendarPopup=True)
        date_edit.setDisplayFormat("yyyy-MM-dd")

        # create & configure the popup calendar
        from PyQt5.QtWidgets import QCalendarWidget
        cal = QCalendarWidget(self)
        cal.setNavigationBarVisible(True)
        cal.setMinimumSize(360, 300)
        cal.setFont(QFont("Segoe UI", 14))
        cal.setStyleSheet("""
            /* overall font size */
            QCalendarWidget { font-size: 14pt; }
            /* nav‐bar background */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: white; height: 40px;
            }
            /* arrows & month/year text */
            QCalendarWidget QToolButton {
                color: black; background: transparent; border: none; font-size: 14pt;
            }
            /* month/year dropdown */
            QCalendarWidget QComboBox {
                color: black; background: white; font-size: 14pt;
            }
        """)

        # wire it up
        date_edit.setCalendarWidget(cal)
        date_edit.setDate(QDate.currentDate())
        self.app_table.setCellWidget(row, 0, date_edit)

        reason_cb = QComboBox()
        reason_cb.setEditable(True)
        reason_cb.addItems(db_manager.get_all_reasons())
        self.app_table.setCellWidget(row, 1, reason_cb)

    def _save_apps_and_next(self):
        """
        Collect the future-appointments table into visit_data,
        persist any new reasons, then advance to Prescriptions.
        """
        apps = []
        for r in range(self.app_table.rowCount()):
            date = self.app_table.cellWidget(r, 0).date().toString("yyyy-MM-dd")
            cb   = self.app_table.cellWidget(r, 1)
            reason = cb.currentText().strip()
            if reason and reason not in db_manager.get_all_reasons():
                db_manager.add_reason(reason)
            apps.append({'date': date, 'reason': reason})

        # attach to visit_data for later saving
        self.visit_data['future_appointments'] = apps
        self._goto(3)
