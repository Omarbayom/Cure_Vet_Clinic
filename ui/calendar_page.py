# ui/calendar_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCalendarWidget, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QDate

import db_manager

class AppointmentCalendar(QCalendarWidget):
    """
    Subclass QCalendarWidget to draw a star on days that have appointments.
    """
    def __init__(self, appointments_by_date: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_map = appointments_by_date
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

    def paintCell(self, painter: QPainter, rect, date: QDate):
        super().paintCell(painter, rect, date)
        key = date.toString("yyyy-MM-dd")
        if key in self.app_map and self.app_map[key]:
            # draw a small orange star in top-right
            painter.setPen(QColor("#FF8C00"))
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(
                rect.x() + rect.width() - 12,
                rect.y() + 12,
                "★"
            )

class CalendarPage(QWidget):
    """
    A page showing a styled calendar with appointment markers,
    a side panel listing the appointments for the selected date,
    and the ability to open a patient's history.
    """
    def __init__(self, on_back, on_show_history):
        super().__init__()
        self.on_back = on_back
        self.on_show_history = on_show_history
        self._load_appointments()
        self._build_ui()

    def _load_appointments(self):
        # fetch all future appointments, group by next_appointment date
        self.apps_by_date = {}
        today = QDate.currentDate().toString("yyyy-MM-dd")
        conn = db_manager.get_connection()
        cur = conn.cursor()
        cur.execute("""
          SELECT
            v.id AS visit_id,
            v.next_appointment,
            o.id   AS owner_id,
            o.name AS owner_name,
            o.phone,
            p.id   AS pet_id,
            p.pet_name,
            s.name AS species,
            v.doctor_name
          FROM visits v
          JOIN pets     p ON v.pet_id = p.id
          JOIN species  s ON p.species_id = s.id
          JOIN owners   o ON p.owner_id  = o.id
          WHERE v.next_appointment >= ?
          ORDER BY v.next_appointment
        """, (today,))
        for r in cur.fetchall():
            d = dict(r)
            date = d['next_appointment']
            self.apps_by_date.setdefault(date, []).append(d)
        conn.close()

    def _build_ui(self):
        # overall layout
        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)

        # header with gradient
        hdr_layout = QHBoxLayout(); hdr_layout.setContentsMargins(10,10,10,5)
        back = QPushButton("←"); back.setFont(QFont("Segoe UI",20))
        back.setStyleSheet("color:white;background:transparent;border:none;")
        back.clicked.connect(self.on_back)
        hdr_layout.addWidget(back, Qt.AlignLeft)
        title = QLabel("📅 Appointments Calendar")
        title.setFont(QFont("Segoe UI",26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr_layout.addWidget(title, Qt.AlignLeft)
        hdr_layout.addStretch()

        header = QFrame()
        header.setLayout(hdr_layout)
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame { background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #009999, stop:1 #006666
            ); }
        """)
        main.addWidget(header)

        # content: calendar + side panel
        content = QHBoxLayout(); content.setContentsMargins(20,20,20,20); content.setSpacing(15)

        # calendar widget
        self.calendar = AppointmentCalendar(self.apps_by_date)
        self.calendar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.calendar.clicked.connect(self.on_date_selected)
        content.addWidget(self.calendar, 2)

        # side panel with list
        panel = QFrame()
        panel.setStyleSheet("background:#e0e0e0; border-radius:8px;")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(12); shadow.setOffset(0,2); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        side = QVBoxLayout(panel); side.setContentsMargins(15,15,15,15); side.setSpacing(10)

        side.addWidget(QLabel("Appointments on Selected Date:"))
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Segoe UI",16))
        self.list_widget.itemClicked.connect(self._on_appointment_clicked)
        side.addWidget(self.list_widget, 1)

        content.addWidget(panel, 1)
        main.addLayout(content)

        # show today's by default
        self._show_appointments_for(QDate.currentDate().toString("yyyy-MM-dd"))

    def on_date_selected(self, date: QDate):
        self._show_appointments_for(date.toString("yyyy-MM-dd"))

    def _show_appointments_for(self, date_str: str):
        self.list_widget.clear()
        visits = self.apps_by_date.get(date_str, [])
        if not visits:
            self.list_widget.addItem("(No appointments)")
        else:
            for v in visits:
                text = f"{v['owner_name']} — {v['pet_name']} ({v['doctor_name']})"
                itm = QListWidgetItem(text)
                itm.setData(Qt.UserRole, v)
                self.list_widget.addItem(itm)

    def _on_appointment_clicked(self, item: QListWidgetItem):
        v = item.data(Qt.UserRole)
        # build owner & pet dicts
        owner = {'id': v['owner_id'], 'name': v['owner_name'], 'phone': v['phone']}
        pet   = {'id': v['pet_id'],    'pet_name': v['pet_name'],    'species': v['species']}
        # navigate to history
        self.on_show_history(owner, pet)
