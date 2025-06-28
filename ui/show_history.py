# ui/show_history.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QMessageBox, QToolButton,
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
        top.addStretch()
        main.addLayout(top)

        # ── Header ──
        hdr = QHBoxLayout()
        hdr.setContentsMargins(20, 0, 20, 15)
        plus = QLabel("📋")
        plus.setFont(QFont("Segoe UI", 26))
        plus.setStyleSheet("color:white; background:transparent;")
        title = QLabel("Patient History")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(plus)
        hdr.addWidget(title)
        hdr.addStretch()
        main.addLayout(hdr)

        # ── Content Panel ──
        panel = QFrame()
        panel.setStyleSheet("QFrame{background:#e0e0e0; border-radius:8px;}")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(15)
        shadow.setOffset(0,3)
        shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content = QVBoxLayout(panel)
        content.setContentsMargins(20,20,20,20)
        content.setSpacing(12)

        # helper to style inputs & lists
        def mk_lineedit(w):
            w.setFont(QFont("Segoe UI", 18))
            w.setStyleSheet(
                "background:white; border:1px solid #ccc; "
                "border-radius:4px; padding:6px 10px; min-height:36px;"
            )
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return w

        def mk_list(w):
            w.setFont(QFont("Segoe UI", 18))
            w.setStyleSheet(
                "background:white; border:1px solid #ccc; "
                "border-radius:4px;"
            )
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return w

        # – Owner Search –
        self.search_input = mk_lineedit(QLineEdit())
        self.search_input.setPlaceholderText("Search owner by name or phone…")
        self.search_input.textChanged.connect(self.on_search_owner)
        content.addWidget(self.search_input)

        content.addWidget(QLabel("Owners:"))
        self.owner_list = mk_list(QListWidget())
        self.owner_list.itemClicked.connect(self.on_owner_selected)
        content.addWidget(self.owner_list, stretch=1)

        # – Pet Selection –
        content.addWidget(QLabel("Pets:"))
        self.pet_list = mk_list(QListWidget())
        self.pet_list.itemClicked.connect(self.on_pet_selected)
        content.addWidget(self.pet_list, stretch=1)

        # – Visit List –
        content.addWidget(QLabel("Visits:"))
        self.history_list = mk_list(QListWidget())
        self.history_list.itemClicked.connect(self.on_history_selected)
        content.addWidget(self.history_list, stretch=1)

        # – Details Pane –
        content.addWidget(QLabel("Details:"))
        self.details = QTextEdit()
        self.details.setFont(QFont("Segoe UI", 16))
        self.details.setStyleSheet("background:white; border:1px solid #ccc;")
        self.details.setReadOnly(True)
        content.addWidget(self.details, stretch=2)

        # – Action Buttons –
        btns = QHBoxLayout()
        btns.addStretch()
        self.new_visit_btn = QPushButton("➕ Add New Visit")
        self.new_visit_btn.setFont(QFont("Segoe UI", 18))
        self.new_visit_btn.setCursor(Qt.PointingHandCursor)
        self.new_visit_btn.setEnabled(False)
        self.new_visit_btn.setStyleSheet(
            "QPushButton{ background:#009999; color:white; border-radius:6px; "
            "padding:10px 20px; }"
            "QPushButton:hover{ background:#008080; }"
        )
        self.new_visit_btn.clicked.connect(self._on_add_new_visit)
        btns.addWidget(self.new_visit_btn)
        content.addLayout(btns)

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
            wi = QListWidgetItem(f"{v['visit_date']}: {v['doctor_name']}…")
            wi.data = v
            self.history_list.addItem(wi)

        self.new_visit_btn.setEnabled(True)

    def on_history_selected(self, item):
        v = item.data
        self.details.clear()
        self.details.append(f"<b>Date:</b> {v['visit_date']}")
        self.details.append(f"<b>Doctor:</b> {v.get('doctor_name','—')}")
        self.details.append(f"<b>Next Appt:</b> {v['next_appointment']}")
        self.details.append(f"<b>Notes:</b>\n{v['notes']}")

        prescs = db_manager.get_prescriptions_by_visit(v['id'])
        if prescs:
            self.details.append("\n<b>Dispensed:</b>")
            for p in prescs:
                src  = "Inventory" if p['is_inventory'] else "Pharmacy"
                name = p['item_name'] if p['is_inventory'] else p['med_name']
                qty  = p['quantity']
                # pick unit_price first if set, otherwise default_sell_price, else 0.0
                price = (
                    p['unit_price']
                    if p['unit_price'] is not None
                    else (p.get('default_sell_price') or 0.0)
                )
                self.details.append(f" • [{src}] {name}: {qty} ")
        else:
            self.details.append("\nNo items dispensed.")


    def _on_add_new_visit(self):
        # passes owner + pet to AddVisitPage
        self.on_add_visit(self.selected_owner, self.selected_pet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ShowHistoryPage(on_back=app.quit, on_add_visit=lambda o,p: print(o,p))
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec_())
