import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QMessageBox, QGridLayout, QScrollArea
)
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QEvent, QByteArray

class Dashboard(QWidget):
    def __init__(
        self,
        initial_geometry: QByteArray = None,
        initial_fullscreen: bool = True,
        return_to_welcome_callback=None
    ):
        super().__init__()
        self.setWindowTitle("𝐂ure Vet Clinic - Dashboard")
        self.return_to_welcome = return_to_welcome_callback
        self.is_fullscreen = initial_fullscreen

        # 1) Restore geometry if provided
        if initial_geometry:
            self.restoreGeometry(initial_geometry)

        # 2) Show full-screen or normal
        if initial_fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()

        # 3) Build UI
        self.setup_background()
        self.init_ui()

    def setup_background(self):
        pal = QPalette()
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        pal.setBrush(QPalette.Window, QBrush(grad))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def init_ui(self):
        # Main vertical layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(20)

        # Title
        title = QLabel("Welcome to 𝐂ure Vet Clinic")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        self.main_layout.addWidget(title)

        # Scrollable grid container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_widget.setLayout(self.grid_layout)
        scroll.setWidget(self.grid_widget)
        self.main_layout.addWidget(scroll)

        # Return button
        back_btn = QPushButton("🔙 Return to Welcome Page")
        back_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
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
        back_btn.clicked.connect(self.back_to_welcome)
        self.main_layout.addWidget(back_btn)

        self.setLayout(self.main_layout)

        # Prepare feature buttons
        self.buttons = []
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
            b.clicked.connect(lambda _, x=t: self.not_implemented(x))
            self.buttons.append(b)

        # Lay them out once
        self.update_grid_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'grid_layout'):
            self.update_grid_layout()

    def update_grid_layout(self):
        # Clear old widgets
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            w.setParent(None)

        # Compute columns by width
        w = self.width()
        cols = 3 if w >= 1200 else 2 if w >= 800 else 1

        # Re-add buttons
        for idx, btn in enumerate(self.buttons):
            r, c = divmod(idx, cols)
            self.grid_layout.addWidget(btn, r, c)

    def not_implemented(self, name):
        QMessageBox.information(self, "Coming Soon", f"🔧 '{name}' will be added soon.")

    def back_to_welcome(self):
        geom = self.saveGeometry()
        fs   = self.isFullScreen()
        if self.return_to_welcome:
            self.return_to_welcome(geom, fs)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Toggle windowed/fullscreen
            if self.isFullScreen():
                self.showNormal()
                self.resize(1000, 600)
                self.move(200, 100)
                self.is_fullscreen = False
            else:
                self.showFullScreen()
                self.is_fullscreen = True

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() == Qt.WindowMaximized:
                self.showFullScreen()
                self.is_fullscreen = True
            elif self.windowState() == Qt.WindowNoState:
                self.showNormal()
                self.is_fullscreen = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Example: no previous geometry → full-screen
    dash = Dashboard()
    dash.show()
    sys.exit(app.exec_())
