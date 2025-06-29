# ui/show_history.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QStackedLayout, QListWidget, QListWidgetItem, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolButton,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt


import db_manager

class ShowHistoryPage(QWidget):
    def __init__(self, on_back, on_add_visit):
        """
        on_back()                → return to Dashboard
        on_add_visit(owner,pet)  → open AddVisitPage with context
        """
        super().__init__()
        self.on_back      = on_back
        self.on_add_visit = on_add_visit
        self.selected_owner = None
        self.selected_pet   = None
        self._build_ui()

    def paintEvent(self, event):
        # Teal gradient header (top 12% of height)
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

        # ── Header with Back & Title ──
        hdr = QHBoxLayout()
        hdr.setContentsMargins(10, 10, 10, 5)
        back = QToolButton()
        back.setText("←")
        back.setFont(QFont("Segoe UI", 20))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            "QToolButton{color:white;background:transparent;border:none;}"
            "QToolButton:hover{color:#e0e0e0;}"
        )
        back.clicked.connect(self.on_back)
        hdr.addWidget(back, Qt.AlignLeft)

        title = QLabel("📋 Patient History")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(title, Qt.AlignLeft)
        hdr.addStretch()
        main.addLayout(hdr)

        # ── Panel with Shadow ──
        panel = QFrame()
        panel.setStyleSheet("QFrame{background:#e0e0e0; border-radius:8px;}")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(12); shadow.setOffset(0,2); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        container = QVBoxLayout(panel)
        container.setContentsMargins(20,20,20,20)
        container.setSpacing(10)

        # ── Helpers ──
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

        # ── Stacked Pages ──
        self.stack = QStackedLayout()

        # Page 0: Owner/Pet/Visit List
        page0 = QWidget()
        p0 = QVBoxLayout(page0)
        p0.setSpacing(12)

        p0.addWidget(QLabel("Search Owner:"))
        self.search_input = mk_lineedit(QLineEdit())
        self.search_input.setPlaceholderText("Name or phone…")
        self.search_input.textChanged.connect(self.on_search_owner)
        p0.addWidget(self.search_input)

        p0.addWidget(QLabel("Owners:"))
        self.owner_list = mk_list(QListWidget())
        self.owner_list.itemClicked.connect(self.on_owner_selected)
        p0.addWidget(self.owner_list, 1)

        p0.addWidget(QLabel("Pets:"))
        self.pet_list = mk_list(QListWidget())
        self.pet_list.itemClicked.connect(self.on_pet_selected)
        p0.addWidget(self.pet_list, 1)

        p0.addWidget(QLabel("Visits:"))
        self.history_list = mk_list(QListWidget())
        self.history_list.itemClicked.connect(self.on_history_selected)
        p0.addWidget(self.history_list, 1)

        nav0 = QHBoxLayout()
        nav0.addStretch()
        self.next_btn = QPushButton("Next: Details")
        self.next_btn.setFont(QFont("Segoe UI",18))
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        nav0.addWidget(self.next_btn)
        p0.addLayout(nav0)

        self.stack.addWidget(page0)

        # ── Page 1: Visit Details ──
        page1 = QWidget()
        p1 = QVBoxLayout(page1)
        p1.setSpacing(12)

        hdr1 = QHBoxLayout()
        hdr1.setContentsMargins(10,10,10,5)
        back1 = QToolButton()
        back1.setText("← Back")
        back1.setFont(QFont("Segoe UI",20))
        back1.setCursor(Qt.PointingHandCursor)
        back1.setStyleSheet(
            "QToolButton{color:#333333; background:transparent; border:none;}"
            "QToolButton:hover{color:black;}"
        )
        back1.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        hdr1.addWidget(back1, Qt.AlignLeft)
        hdr1.addStretch()
        p1.addLayout(hdr1)



        # styled content frame for details
        details_panel = QFrame()
        details_panel.setStyleSheet("QFrame{background:white; border-radius:8px;}")
        shadow2 = QGraphicsDropShadowEffect(details_panel)
        shadow2.setBlurRadius(15); shadow2.setOffset(0,3); shadow2.setColor(QColor(0,0,0,60))
        details_panel.setGraphicsEffect(shadow2)
        details_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        details_container = QVBoxLayout(details_panel)
        details_container.setContentsMargins(20,20,20,20)
        details_container.setSpacing(10)

        lbl = QLabel("Visit Details")
        lbl.setFont(QFont("Segoe UI",20,QFont.Bold))
        details_container.addWidget(lbl)

        self.details = QTextEdit()
        self.details.setFont(QFont("Segoe UI",16))
        self.details.setStyleSheet(
            "background: #fafafa; border:1px solid #ddd; border-radius:4px;"
            " padding:8px;"
        )
        self.details.setReadOnly(True)
        details_container.addWidget(self.details, 1)

        p1.addWidget(details_panel)

        # bottom nav
        nav1 = QHBoxLayout()
        nav1.addStretch()
        self.new_visit_btn = QPushButton("➕ Add New Visit")
        self.new_visit_btn.setFont(QFont("Segoe UI",16))
        self.new_visit_btn.setCursor(Qt.PointingHandCursor)
        self.new_visit_btn.setEnabled(False)
        self.new_visit_btn.clicked.connect(self._on_add_new_visit)
        nav1.addWidget(self.new_visit_btn)
        p1.addLayout(nav1)

        self.stack.addWidget(page1)

        # ── Assemble ──
        container.addLayout(self.stack)
        main.addWidget(panel)


    
    # ─── Handlers (from original) ───────────────────────────────────────────── :contentReference[oaicite:0]{index=0}

    def on_search_owner(self, text):
        term = text.strip()
        self.owner_list.clear()
        self.pet_list.clear()
        self.history_list.clear()
        self.details.clear()
        self.new_visit_btn.setEnabled(False)

        results = []
        if term.isdigit():
            owner = db_manager.get_owner_by_phone(term)
            if owner: results = [owner]
        else:
            results = db_manager.find_owners_by_name(term)

        for o in results:
            item = QListWidgetItem(f"{o['name']} — {o['phone']}")
            item.data = o
            self.owner_list.addItem(item)

    def on_owner_selected(self, item):
        self.selected_owner = item.data
        self.pet_list.clear()
        self.history_list.clear()
        self.details.clear()
        self.new_visit_btn.setEnabled(False)

        pets = db_manager.get_pets_by_owner(self.selected_owner['id'])
        for species, petname in pets:
            pi = QListWidgetItem(f"{petname} ({species})")
            pi.data = {'species': species, 'pet_name': petname}
            self.pet_list.addItem(pi)

    def on_pet_selected(self, item):
        info = item.data
        self.selected_pet = db_manager.find_pet(
            self.selected_owner['id'],
            info['species'],
            info['pet_name']
        )
        self.history_list.clear()
        self.details.clear()

        visits = db_manager.get_visits_by_pet(self.selected_pet['id'])
        for v in visits:
            wi = QListWidgetItem(f"{v['visit_date']}:  Dr.{v['doctor_name']}…")
            wi.data = v
            self.history_list.addItem(wi)

        self.new_visit_btn.setEnabled(True)

    def on_history_selected(self, item):
        v = item.data
        # 1) Clear previous contents
        self.details.clear()

        # 2) Basic visit info
        self.details.append(f"<b>Date:</b> {v['visit_date']}")
        self.details.append(f"<b>Doctor:</b> {v.get('doctor_name','—')}")
        self.details.append(f"<b>Notes:</b>\n{v['notes']}")

        # 3) Dispensed items
        prescs = db_manager.get_prescriptions_by_visit(v['id'])
        if prescs:
            self.details.append("\n<b>Dispensed:</b>")
            for p in prescs:
                src   = "Inventory" if p['is_inventory'] else "Pharmacy"
                name  = p['item_name'] if p['is_inventory'] else p['med_name']
                qty   = p['quantity']
                price = (
                    p['unit_price']
                    if p['unit_price'] is not None
                    else (p.get('default_sell_price') or 0.0)
                )
                self.details.append(f" • [{src}] {name}: {qty} @ {price}")
        else:
            self.details.append("\nNo items dispensed.")

        # 4) Future appointments
        apps = db_manager.get_future_appointments_by_visit(v['id'])
        if apps:
            self.details.append("\n<b>Future Appointments:</b>")
            for a in apps:
                date   = a['appointment_date']
                reason = a['reason'] or '—'
                self.details.append(f" • {date} — {reason}")

        # 5) Enable navigation buttons (no automatic page switch)
        self.next_btn.setEnabled(True)
        self.new_visit_btn.setEnabled(True)




    def _on_add_new_visit(self):
        # passes owner + pet to AddVisitPage
        self.on_add_visit(self.selected_owner, self.selected_pet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ShowHistoryPage(on_back=app.quit, on_add_visit=lambda o,p: print(o,p))
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec_())
