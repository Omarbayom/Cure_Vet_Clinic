# ui/calendar_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCalendarWidget, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QInputDialog, QMessageBox,QDialog, QComboBox
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QDate

import db_manager
import wp

# ── New at top of file, after ModeSelectDialog ──
class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        # remove native title bar
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setFixedSize(400, 160)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #006666;
                border-radius: 8px;
            }
            QLabel#hdr {
                background-color: #006666;
                color: white;
                padding: 10px;
                font-size: 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QLabel#body {
                font-size: 18px;
                padding: 20px;
            }
            QPushButton {
                background-color: #006666;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #008080; }
            QPushButton:pressed { background-color: #005757; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        hdr = QLabel(title, objectName="hdr")
        hdr.setFont(QFont("Segoe UI", 18, QFont.Bold))
        hdr.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(hdr)

        body = QLabel(message, objectName="body")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignCenter)
        layout.addWidget(body)

        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        # center the button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


class ModeSelectDialog(QDialog):
    def __init__(self, date_str, parent=None):
        super().__init__(parent)
        # ── Remove native title bar ──
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #006666;
                border-radius: 8px;
            }
            QLabel#header {
                background-color: #006666;
                color: white;
                padding: 10px;
                font-size: 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # ── Header ──
        header = QLabel(" Send Reminders", objectName="header")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(header)

        # ── Body ──
        body = QVBoxLayout()
        body.setContentsMargins(20,20,20,20)
        body.setSpacing(12)

        lbl = QLabel(f"Mode for {date_str}:")
        lbl.setFont(QFont("Segoe UI", 18))
        body.addWidget(lbl)

        self.combo = QComboBox()
        self.combo.addItems(["desktop", "web", "auto"])
        self.combo.setFont(QFont("Segoe UI", 16))
        self.combo.setMinimumHeight(40)
        body.addWidget(self.combo)

        # ── Buttons ──
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFont(QFont("Segoe UI", 16))
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover { background-color: #AAAAAA; }
            QPushButton:pressed { background-color: #666666; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_ok = QPushButton("OK")
        btn_ok.setFont(QFont("Segoe UI", 16))
        btn_ok.setMinimumHeight(40)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #006666;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover { background-color: #008080; }
            QPushButton:pressed { background-color: #005757; }
        """)
        btn_ok.clicked.connect(self.accept)
        btns.addWidget(btn_ok)

        body.addLayout(btns)
        layout.addLayout(body)

    def selected_mode(self):
        return self.combo.currentText()


class AppointmentCalendar(QCalendarWidget):
    """
    Subclass QCalendarWidget to draw a star on days that have appointments.
    """
    def __init__(self, apps_by_date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apps_by_date = apps_by_date
        self.selectionChanged.connect(
            lambda: self.parent().on_date_selected(self.selectedDate())
        )

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        ds = date.toString("yyyy-MM-dd")
        if ds in self.apps_by_date:
            painter.save()
            # draw a filled circle in the top-right corner
            painter.setBrush(QColor("#FF5722"))      # orange-red fill
            painter.setPen(Qt.NoPen)                 # no border
            radius = 6
            cx = rect.right() - radius - 2
            cy = rect.top() + radius + 2
            painter.drawEllipse(cx - radius, cy - radius, radius*2, radius*2)
            painter.restore()


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
        self.current_date = QDate.currentDate().toString("yyyy-MM-dd")
        self._build_ui()
        self.on_date_selected(QDate.currentDate())

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#009999"))
        grad.setColorAt(1.0, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _load_appointments(self):
        """
        Load all future appointments from the new table, grouped by date.
        """
        self.apps_by_date = {}
        today = QDate.currentDate().toString("yyyy-MM-dd")
        conn = db_manager.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                v.id                  AS visit_id,
                fa.appointment_date   AS next_appointment,
                p.id                  AS pet_id,
                p.pet_name,
                p.species_id,
                s.name                AS species,
                o.id                  AS owner_id,
                o.name                AS owner_name,
                o.phone,
                v.doctor_name,
                r.name                AS reason
            FROM future_appointments fa
            JOIN visits          v  ON fa.visit_id    = v.id
            JOIN pets            p  ON v.pet_id       = p.id
            JOIN species         s  ON p.species_id   = s.id
            JOIN owners          o  ON p.owner_id     = o.id
            LEFT JOIN reasons    r  ON fa.reason_id   = r.id
            WHERE fa.appointment_date >= ?
            ORDER BY fa.appointment_date
        """, (today,))
        for r in cur.fetchall():
            record = dict(r)
            date = record['next_appointment']
            # each record now includes record['reason']
            self.apps_by_date.setdefault(date, []).append(record)
        conn.close()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        hdr_layout = QHBoxLayout()
        hdr_layout.setContentsMargins(10, 10, 10, 5)
        back = QPushButton("←")
        back.setFont(QFont("Segoe UI", 20))
        back.setStyleSheet("color:white;background:transparent;border:none;")
        back.clicked.connect(self.on_back)
        hdr_layout.addWidget(back, Qt.AlignLeft)

        title = QLabel("📅 Appointments Calendar")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr_layout.addWidget(title, Qt.AlignLeft)
        hdr_layout.addStretch()
        main.addLayout(hdr_layout)

        content = QHBoxLayout()
        self.cal = AppointmentCalendar(self.apps_by_date)
        self.cal.setFont(QFont("Segoe UI", 18))
        content.addWidget(self.cal, 2)

        panel = QFrame()
        panel.setStyleSheet("background:#e0e0e0; border-radius:8px;")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        side = QVBoxLayout(panel)
        side.setContentsMargins(15, 15, 15, 15)
        side.setSpacing(10)

        side.addWidget(QLabel("Appointments on Selected Date:"))
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Segoe UI", 18))
        self.list_widget.itemDoubleClicked.connect(self._on_appointment_clicked)
        side.addWidget(self.list_widget, 1)

        remind_btn = QPushButton("🔔 Send Reminders")
        remind_btn.setFont(QFont("Segoe UI", 16))
        remind_btn.setCursor(Qt.PointingHandCursor)
        remind_btn.clicked.connect(self.on_send_reminders)
        side.addWidget(remind_btn)

        content.addWidget(panel, 1)
        main.addLayout(content)

    def showEvent(self, event):
        super().showEvent(event)
        # 1) reload fresh data
        self._load_appointments()
        # 2) update the calendar’s appointment map
        self.cal.apps_by_date = self.apps_by_date
        # 3) force redraw of all cells (stars)
        self.cal.updateCells()
        # 4) refresh the side‐list for whatever date is currently selected
        self.on_date_selected(self.cal.selectedDate())



    def on_date_selected(self, date: QDate):
        date_str = date.toString("yyyy-MM-dd")
        self.current_date = date_str
        self._show_appointments_for(date_str)

    def _show_appointments_for(self, date_str: str):
        self.list_widget.clear()
        visits = self.apps_by_date.get(date_str, [])
        if not visits:
            self.list_widget.addItem("(No appointments)")
        else:
            for v in visits:
                text = f"{v['owner_name']} — {v['pet_name']} (Dr. {v['doctor_name']})"
                itm = QListWidgetItem(text)
                itm.setData(Qt.UserRole, v)
                # make it checkable and default to checked
                itm.setFlags(itm.flags() | Qt.ItemIsUserCheckable)
                itm.setCheckState(Qt.Checked)
                self.list_widget.addItem(itm)


    def _on_appointment_clicked(self, item: QListWidgetItem):
        v = item.data(Qt.UserRole)
        owner = {'id': v['owner_id'], 'name': v['owner_name'], 'phone': v['phone']}
        pet   = {'id': v['pet_id'],    'pet_name': v['pet_name'],    'species': v['species']}
        self.on_show_history(owner, pet)

    def on_send_reminders(self):
        date_str = self.current_date

        # 1) Collect only checked appointments
        raw_apps = []
        for i in range(self.list_widget.count()):
            itm = self.list_widget.item(i)
            if itm.checkState() == Qt.Checked:
                raw_apps.append(itm.data(Qt.UserRole))

        # 2) Warn if nothing is selected
        if not raw_apps:
            msg = QMessageBox(self)
            msg.setWindowTitle("No Selection")
            msg.setText("Please check at least one appointment to send reminders.")
            msg.setIcon(QMessageBox.Warning)
            msg.setFont(QFont("Segoe UI", 18))
            msg.setStyleSheet("""
                QLabel { min-width: 350px; font-size: 18px; }
                QPushButton { font-size: 16px; padding: 8px 20px; }
            """)
            msg.exec_()
            return

        # 3) Let user choose WhatsApp mode in a bigger dialog
        # 3) Let user choose WhatsApp mode via custom dialog
        dlg = ModeSelectDialog(date_str, parent=self)
        # exec_() returns QDialog.Accepted or Rejected
        if dlg.exec_() != QDialog.Accepted:
            return
        mode = dlg.selected_mode()


        # 4) Group & merge selected appointments by phone
        groups = {}
        for v in raw_apps:
            phone = v['phone']
            grp = groups.setdefault(phone, {
                'phone':            phone,
                'owner_name':       v['owner_name'],
                'doctor_name':      v['doctor_name'],
                'next_appointment': v['next_appointment'],
                'pet_names':        [],
                'reasons':          []
            })
            if v['pet_name'] not in grp['pet_names']:
                grp['pet_names'].append(v['pet_name'])
                grp['reasons'].append(v.get('reason', ''))

        merged_apps = []
        for g in groups.values():
            merged_apps.append({
                'phone':            g['phone'],
                'owner_name':       g['owner_name'],
                'doctor_name':      g['doctor_name'],
                'next_appointment': g['next_appointment'],
                'pet_name':         ' و '.join(g['pet_names']),
                'reason':           ' و '.join(g['reasons'])
            })

        # 5) Send and confirm
        wp.send_reminders(merged_apps, mode=mode)

        dlg = ConfirmDialog(
            "Reminders Sent",
            f"Sent {len(merged_apps)} reminder(s) for {date_str}.",
            parent=self
        )
        dlg.exec_()
