# ui/dashboard.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QScrollArea, QGridLayout,
    QMessageBox, QVBoxLayout, QToolButton, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt

class DashboardWidget(QWidget):
    def __init__(self,
                 on_back,
                 on_book_appointment,
                 on_show_history,
                 on_add_patient,
                 on_manage_inventory,
                 on_show_calendar,
                 on_show_report):
        super().__init__()
        self.on_back             = on_back
        self.on_book_appointment = on_book_appointment
        self.on_show_history     = on_show_history
        self.on_add_patient      = on_add_patient
        self.on_manage_inventory = on_manage_inventory
        self.on_calendar         = on_show_calendar
        self.on_report           = on_show_report  # Placeholder for future report functionality
        self.buttons             = []
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#009999"))
        grad.setColorAt(1.0, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        # ← Back
        top_bar = QHBoxLayout()
        arrow = QToolButton()
        arrow.setText("←")
        arrow.setFont(QFont("Segoe UI", 32, QFont.Bold))
        arrow.setFixedSize(60, 60)
        arrow.setCursor(Qt.PointingHandCursor)
        arrow.setStyleSheet(
            "QToolButton { background: transparent; color: white; border: none; }"
            "QToolButton:hover { color: #ffdddd; }"
        )
        arrow.clicked.connect(self.on_back)
        top_bar.addWidget(arrow)
        self.main_layout.addLayout(top_bar)

        # Title
        title = QLabel("Welcome to Cure Vet Clinic")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        # Scrollable feature grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(20)
        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)

        # Feature buttons
        texts = [
            "📅 Book an Appointment",
            "📋 Show Patient History",
            "✏️ Update Patient Data",
            "📆 Show Calendar",
            "➕ Add New Patient",
            "🧾 Generate Invoice",
            "📦 Manage Inventory",
            "👨‍⚕️ Staff Management",
            "📊 Reports and Analytics"
        ]
        for t in texts:
            btn = QPushButton(t)
            btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton {"
                "  background-color: white;"
                "  color: #007f7f;"
                "  padding: 16px;"
                "  border-radius: 12px;"
                "  border: 2px solid #009999;"
                "}"
                "QPushButton:hover { background-color: #e6f2f2; }"
            )

            # connect signals
            if t == "📅 Book an Appointment":
                btn.clicked.connect(self.on_book_appointment)
            elif t == "📋 Show Patient History":
                btn.clicked.connect(self.on_show_history)
            elif t == "📆 Show Calendar":
                btn.clicked.connect(self.on_calendar)
            elif t == "➕ Add New Patient":
                btn.clicked.connect(self.on_add_patient)
            elif t == "📦 Manage Inventory":
                btn.clicked.connect(self.on_manage_inventory)
            elif t == "📊 Reports and Analytics":
                btn.clicked.connect(self.on_report)  # Placeholder for invoice generation
            else:
                btn.clicked.connect(
                    lambda _, name=t: QMessageBox.information(
                        self,
                        "Coming Soon",
                        f"🔧 '{name}' will be implemented soon."
                    )
                )

            self.buttons.append(btn)

        # Populate grid
        self._update_grid()

    def resizeEvent(self, event):
        self._update_grid()
        super().resizeEvent(event)

    def _update_grid(self):
        # clear old widgets
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            w.setParent(None)
        # choose columns based on width
        w = self.width()
        cols = 3 if w >= 1200 else 2 if w >= 800 else 1
        for idx, btn in enumerate(self.buttons):
            r, c = divmod(idx, cols)
            self.grid_layout.addWidget(btn, r, c)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from ui.calendar_page import CalendarPage
    app = QApplication(sys.argv)
    dash = DashboardWidget(
        on_back=lambda: print("Back"),
        on_book_appointment=lambda: print("Book Visit"),
        on_show_history=lambda: print("Show History"),
        on_add_patient=lambda: print("Add Patient"),
        on_manage_inventory=lambda: print("Inventory"),
        on_calendar=lambda: print("Show Calendar")
    )
    dash.show()
    sys.exit(app.exec_())
