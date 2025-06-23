import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QScrollArea, QGridLayout,
    QMessageBox, QVBoxLayout, QToolButton, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QTimer, QEvent

class DashboardWidget(QWidget):
    def __init__(self, on_back, on_add_patient):
        super().__init__()
        self.on_back = on_back
        self.on_add_patient = on_add_patient
        self.buttons = []
        self._build_ui()

    def paintEvent(self, event):
        # Teal gradient background
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

        # Top-left back arrow (now larger)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setAlignment(Qt.AlignLeft)
        arrow = QToolButton()
        arrow.setText("←")
        arrow.setFont(QFont("Segoe UI", 32, QFont.Bold))  # bigger font
        arrow.setFixedSize(60, 60)                        # fixed square size
        arrow.setCursor(Qt.PointingHandCursor)
        arrow.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: white;
                border: none;
                padding: 0;
            }
            QToolButton:hover {
                color: #ffdddd;
            }
        """)
        arrow.clicked.connect(self.on_back)
        top_bar.addWidget(arrow)
        self.main_layout.addLayout(top_bar)

        # Title
        title = QLabel("Welcome to Cure Vet Clinic")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        # Scrollable, transparent grid area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_root = QWidget()
        self.grid_root.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_root)
        self.grid_layout.setSpacing(20)
        scroll.setWidget(self.grid_root)
        self.main_layout.addWidget(scroll)

        # Feature buttons (3→2→1 columns)
        texts = [
            "📅 Book an Appointment",
            "📋 Show Patient History",
            "✏️ Update Patient Data",
            "📆 Show Today's Schedule",
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
            btn.setStyleSheet("""
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
            if t == "➕ Add New Patient":
                btn.clicked.connect(self.on_add_patient)
            else:
                btn.clicked.connect(
                    lambda _, name=t: QMessageBox.information(
                        self, "Coming Soon", f"🔧 '{name}' will be implemented soon."
                    )
                )
            self.buttons.append(btn)

        # Initial grid layout
        self._update_grid()

    def resizeEvent(self, event):
        # Reflow buttons on every resize
        self._update_grid()
        super().resizeEvent(event)

    def _update_grid(self):
        # Clear existing
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            w.setParent(None)

        # Decide columns by width
        w = self.width()
        cols = 3 if w >= 1200 else 2 if w >= 800 else 1

        # Re-add buttons
        for idx, btn in enumerate(self.buttons):
            row, col = divmod(idx, cols)
            self.grid_layout.addWidget(btn, row, col)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = DashboardWidget(on_back=lambda: print("Back!"))
    w.showFullScreen()
    sys.exit(app.exec_())
