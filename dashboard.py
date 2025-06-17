from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QScrollArea, QGridLayout, QMessageBox
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt

class DashboardWidget(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.buttons = []
        self.build_ui()

    def paintEvent(self, event):
        """Same teal gradient background."""
        p = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#009999"))
        grad.setColorAt(1.0, QColor("#006666"))
        p.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        title = QLabel("Welcome to 𝐂ure Vet Clinic")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        # ==== scroll + transparent grid container ====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # make scroll’s viewport transparent
        scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_root = QWidget()
        self.grid_root.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_root)
        self.grid_layout.setSpacing(20)
        scroll.setWidget(self.grid_root)

        self.main_layout.addWidget(scroll)

        back = QPushButton("🔙 Return to Welcome Page")
        back.setFont(QFont("Segoe UI", 14, QFont.Bold))
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(self.on_back)
        back.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #b40000;
                padding: 12px;
                border-radius: 10px;
                border: 2px solid #b40000;
            }
            QPushButton:hover {
                background-color: #ffe6e6;
            }
        """)
        self.main_layout.addWidget(back)

        # Create buttons (but do _not_ yet add to layout)
        texts = [
            "📅 Book an Appointment", "📋 Show Patient History",
            "✏️ Update Patient Data", "📆 Show Today's Schedule",
            "➕ Add New Patient", "🧾 Generate Invoice",
            "📦 Manage Inventory", "👨‍⚕️ Staff Management",
            "📊 Reports and Analytics"
        ]
        for t in texts:
            b = QPushButton(t)
            b.setFont(QFont("Segoe UI", 14, QFont.Bold))
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #007f7f;
                    padding: 16px;
                    border-radius: 12px;
                    border: 2px solid #009999;
                }
                QPushButton:hover {
                    background-color: #e6f2f2;
                }
            """)
            b.clicked.connect(lambda _, x=t: QMessageBox.information(
                self, "Coming Soon", f"🔧 {x}"))
            self.buttons.append(b)

        # Do the initial layout pass
        self.update_grid()

    def resizeEvent(self, event):
        # recompute on every resize
        self.update_grid()
        super().resizeEvent(event)

    def update_grid(self):
        # clear
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            w.setParent(None)

        # decide cols by current width
        w = self.width()
        cols = 3 if w >= 1200 else 2 if w >= 800 else 1

        # re-add
        for idx, btn in enumerate(self.buttons):
            r, c = divmod(idx, cols)
            self.grid_layout.addWidget(btn, r, c)
