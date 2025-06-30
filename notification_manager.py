from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStackedWidget,
    QSystemTrayIcon,
    QFrame,
    QToolButton,
    QScrollArea,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QSettings, QDate
from datetime import timedelta
from db_manager import get_connection

# CSS for report‐style tables
_report_table_css = """
QTableWidget {
    background-color: #ffffff;
    border: none;
    alternate-background-color: #f9f9f9;
}
QHeaderView::section {
    background: #006666;
    color: white;
    padding: 8px;
    font-size: 16px;
    border: none;
}
"""

class NotificationManager:
    """Handles persistence of settings, periodic checks, and tray alerts."""
    def __init__(self, parent: QWidget = None):
        self.parent = parent
        self.settings = QSettings("CureVetClinic", "NotificationSettings")
        self.expiry_days         = self.settings.value("expiry_days", 1, type=int)
        self.reorder_enable      = self.settings.value("reorder_enable", True, type=bool)
        self.appointments_enable = self.settings.value("appointments_enable", True, type=bool)

        self.tray = QSystemTrayIcon(QIcon("assets/icon.png"), parent)
        self.tray.show()

        self.timer = QTimer(parent)
        self.timer.timeout.connect(self._show_tray_notifications)
        self.timer.start(60 * 1000)

    def update_settings(self, expiry_days: int, reorder: bool, appointments: bool):
        self.expiry_days         = expiry_days
        self.reorder_enable      = reorder
        self.appointments_enable = appointments
        self.settings.setValue("expiry_days", expiry_days)
        self.settings.setValue("reorder_enable", reorder)
        self.settings.setValue("appointments_enable", appointments)

    def fetch_notifications(self):
        """
        Returns list of (category, payload):
        - For Expiry/Reorder: payload is (item_name, detail)
        - For Tomorrow/Day After: payload is (pet_name, date_str)
        """
        notes = []
        conn = get_connection()
        cur = conn.cursor()
        today = QDate.currentDate().toPyDate()

        # Expiry
        if self.expiry_days > 0:
            cutoff = (today + timedelta(days=self.expiry_days)).isoformat()
            cur.execute(
                "SELECT name, expiration_date FROM inventory WHERE DATE(expiration_date) <= ?",
                (cutoff,)
            )
            for name, exp in cur.fetchall():
                notes.append(("Expiry", (name, exp)))

        # Reorder
        if self.reorder_enable:
            cur.execute(
                "SELECT name, quantity, reorder_level FROM inventory WHERE quantity <= reorder_level"
            )
            for name, qty, lvl in cur.fetchall():
                notes.append(("Reorder", (name, f"{qty} ≤ {lvl}")))

        # Appointments
        if self.appointments_enable:
            for offset, label in ((1, "Tomorrow"), (2, "Day After")):
                day = (today + timedelta(days=offset)).isoformat()
                cur.execute(
                    "SELECT p.pet_name, fa.appointment_date "
                    "FROM future_appointments fa "
                    "JOIN visits v ON fa.visit_id=v.id "
                    "JOIN pets p ON v.pet_id=p.id "
                    "WHERE DATE(fa.appointment_date)=?",
                    (day,)
                )
                for pet, dt in cur.fetchall():
                    notes.append((label, (pet, dt)))

        conn.close()
        return notes

    def _show_tray_notifications(self):
        for cat, payload in self.fetch_notifications():
            # payload may be tuple
            if isinstance(payload, tuple):
                msg = " — ".join(payload)
            else:
                msg = str(payload)
            self.tray.showMessage(f"{cat} Alert", msg, icon=QSystemTrayIcon.Information)


class NotificationPage(QWidget):
    """UI page: settings + tabbed, two‐column tables for alerts + hide toggle."""
    def __init__(self, parent=None, notif_manager=None, on_back=None):
        super().__init__(parent)
        self.notif_manager = notif_manager
        self.on_back       = on_back
        self._init_ui()
        self.load_notifications()

    def paintEvent(self, ev):
        p = QPainter(self)
        grad = QLinearGradient(0, 0, 0, 60)
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        p.fillRect(0, 0, self.width(), 60, grad)
        super().paintEvent(ev)

    def _init_ui(self):
        self.setStyleSheet("background-color: #f2f2f2;")
        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0); main.setSpacing(0)

        # Header
        hdr = QFrame(self); hdr.setFixedHeight(60)
        hdr.setStyleSheet("background: transparent;")
        hb = QHBoxLayout(hdr); hb.setContentsMargins(10,0,10,0)
        if self.on_back:
            b = QToolButton(); b.setText("←"); b.setFont(QFont("Segoe UI",20))
            b.setStyleSheet("color:white; background:transparent; border:none;")
            b.clicked.connect(self.on_back); hb.addWidget(b)
        t = QLabel("Notifications"); t.setFont(QFont("Segoe UI",18,QFont.Bold))
        t.setStyleSheet("color:white;"); hb.addStretch(); hb.addWidget(t); hb.addStretch()
        main.addWidget(hdr)

        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget(); content = QVBoxLayout(container)
        content.setContentsMargins(20,20,20,20); content.setSpacing(24)

        # Settings panel (enhanced)
        sb = QGroupBox("Settings")
        sb.setStyleSheet("QGroupBox { font: bold 16pt 'Segoe UI'; }")
        sh = QGraphicsDropShadowEffect(); sh.setBlurRadius(16); sh.setOffset(0,3)
        sh.setColor(QColor(0,0,0,80)); sb.setGraphicsEffect(sh)
        frm = QFormLayout(sb); frm.setLabelAlignment(Qt.AlignLeft)
        frm.setContentsMargins(20,30,20,20); frm.setSpacing(24)

        lbl = QLabel("Days ahead for expiry:"); lbl.setFont(QFont("Segoe UI",14))
        self.expiry = QSpinBox(); self.expiry.setRange(0,30)
        self.expiry.setValue(self.notif_manager.expiry_days)
        self.expiry.setFont(QFont("Segoe UI",14)); self.expiry.setMinimumHeight(32)
        frm.addRow(lbl, self.expiry)

        self.chk_lo = QCheckBox("Enable low-stock alerts")
        self.chk_lo.setFont(QFont("Segoe UI",14))
        self.chk_lo.setChecked(self.notif_manager.reorder_enable)
        frm.addRow(self.chk_lo)

        self.chk_ap = QCheckBox("Enable appointment alerts")
        self.chk_ap.setFont(QFont("Segoe UI",14))
        self.chk_ap.setChecked(self.notif_manager.appointments_enable)
        frm.addRow(self.chk_ap)

        sv = QPushButton("💾 Save Settings"); sv.setFont(QFont("Segoe UI",16))
        sv.setCursor(Qt.PointingHandCursor); sv.setMinimumHeight(48)
        sv.setStyleSheet("background:#007777;color:white;padding:12px;border-radius:8px;")
        sv.clicked.connect(self._save_settings)
        frm.addRow(sv)
        content.addWidget(sb)

        # Tab buttons
        tb = QHBoxLayout(); tb.setSpacing(12)
        self.btn_e = QPushButton("Expiry Alerts")
        self.btn_r = QPushButton("Reorder Alerts")
        self.btn_a = QPushButton("Appointment Alerts")
        for b in (self.btn_e,self.btn_r,self.btn_a):
            b.setCheckable(True); b.setFont(QFont("Segoe UI",14))
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(
                "QPushButton{background:#e0e0e0;border:none;padding:8px;}"
                "QPushButton:checked{background:#009999;color:white;}"
            )
            tb.addWidget(b)
        self.btn_e.setChecked(True)
        content.addLayout(tb)

        # Tables
        self.stack = QStackedWidget()
        # Expiry: two cols
        eb = QGroupBox(); el = QVBoxLayout(eb)
        self.tbl_e = QTableWidget(0,2); 
        self.tbl_e.setFont(QFont("Segoe UI",13))
        self.tbl_e.setHorizontalHeaderLabels(["Item","Expiry Date"])
        self.tbl_e.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_e.verticalHeader().setVisible(False)
        self.tbl_e.setAlternatingRowColors(True)
        eb.setStyleSheet(_report_table_css); el.addWidget(self.tbl_e)
        self.stack.addWidget(eb)
        # Reorder: two cols
        rb = QGroupBox(); rl = QVBoxLayout(rb)
        self.tbl_r = QTableWidget(0,2)
        self.tbl_r.setFont(QFont("Segoe UI",13))
        self.tbl_r.setHorizontalHeaderLabels(["Item","Qty ≤ Reorder"])
        self.tbl_r.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_r.verticalHeader().setVisible(False)
        self.tbl_r.setAlternatingRowColors(True)
        rb.setStyleSheet(_report_table_css); rl.addWidget(self.tbl_r)
        self.stack.addWidget(rb)
        # Appt
        ab = QGroupBox(); al = QVBoxLayout(ab)
        self.tbl_a = QTableWidget(0,2)
        self.tbl_a.setFont(QFont("Segoe UI",13))
        self.tbl_a.setHorizontalHeaderLabels(["When","Pet — Date"])
        self.tbl_a.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_a.verticalHeader().setVisible(False)
        self.tbl_a.setAlternatingRowColors(True)
        ab.setStyleSheet(_report_table_css); al.addWidget(self.tbl_a)
        self.stack.addWidget(ab)

        content.addWidget(self.stack)

        # Hide toggle below
        self.toggle = QPushButton("Hide Tables")
        self.toggle.setCheckable(True)
        self.toggle.setFont(QFont("Segoe UI",14))
        self.toggle.setCursor(Qt.PointingHandCursor)
        self.toggle.setStyleSheet(
            "QPushButton{background:#f2f2f2;color:#cc0000;border:none;padding:8px;}"
            "QPushButton:checked{background:#cc0000;color:white;}"
        )
        self.toggle.clicked.connect(self._toggle)
        content.addWidget(self.toggle)

        # connect tabs
        self.btn_e.clicked.connect(lambda: self._switch(0))
        self.btn_r.clicked.connect(lambda: self._switch(1))
        self.btn_a.clicked.connect(lambda: self._switch(2))

        scroll.setWidget(container)
        main.addWidget(scroll)

    def _switch(self, idx):
        for i,b in enumerate((self.btn_e,self.btn_r,self.btn_a)):
            b.setChecked(i==idx)
        self.stack.setCurrentIndex(idx)

    def _save_settings(self):
        self.notif_manager.update_settings(
            self.expiry.value(),
            self.chk_lo.isChecked(),
            self.chk_ap.isChecked()
        )
        QMessageBox.information(self,"Notifications","Settings saved.")
        self.load_notifications()

    def load_notifications(self):
        notes = self.notif_manager.fetch_notifications()
        # clear
        for tbl in (self.tbl_e, self.tbl_r, self.tbl_a):
            tbl.setRowCount(0)
        # fill
        for cat, payload in notes:
            if cat=="Expiry":
                name, exp = payload
                r = self.tbl_e.rowCount(); self.tbl_e.insertRow(r)
                self.tbl_e.setItem(r,0,QTableWidgetItem(name))
                self.tbl_e.setItem(r,1,QTableWidgetItem(exp))
            elif cat=="Reorder":
                name, txt = payload
                r = self.tbl_r.rowCount(); self.tbl_r.insertRow(r)
                self.tbl_r.setItem(r,0,QTableWidgetItem(name))
                self.tbl_r.setItem(r,1,QTableWidgetItem(txt))
            else:
                when, (pet,dt) = cat, payload
                r = self.tbl_a.rowCount(); self.tbl_a.insertRow(r)
                self.tbl_a.setItem(r,0,QTableWidgetItem(when))
                self.tbl_a.setItem(r,1,QTableWidgetItem(f"{pet} — {dt}"))

    def _toggle(self):
        hide = self.toggle.isChecked()
        for b in (self.btn_e,self.btn_r,self.btn_a):
            b.setVisible(not hide)
        self.stack.setVisible(not hide)
        self.toggle.setText("Show Tables" if hide else "Hide Tables")


if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    mgr = NotificationManager()
    pg = NotificationPage(None, notif_manager=mgr, on_back=app.quit)
    pg.show()
    sys.exit(app.exec_())
