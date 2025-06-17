import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QMessageBox, QGridLayout, QScrollArea
)
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QEvent

class Dashboard(QWidget):
    def __init__(self, return_to_welcome_callback=None):
        super().__init__()
        self.setWindowTitle("𝐂ure Vet Clinic - Dashboard")
        self.is_fullscreen = True
        self.return_to_welcome = return_to_welcome_callback
        self.showFullScreen()

        self.setup_background()
        self.init_ui()

    def setup_background(self):
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#009999"))
        gradient.setColorAt(1.0, QColor("#006666"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def init_ui(self):
        # 1) Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(20)

        # 2) Title
        title = QLabel("Welcome to 𝐂ure Vet Clinic")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        self.main_layout.addWidget(title)

        # 3) Scrollable grid area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()           # ← grid_layout is created here
        self.grid_layout.setSpacing(20)
        self.grid_widget.setLayout(self.grid_layout)
        scroll.setWidget(self.grid_widget)

        self.main_layout.addWidget(scroll)

        # 4) Return button
        return_btn = QPushButton("🔙 Return to Welcome Page")
        return_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        return_btn.setCursor(Qt.PointingHandCursor)
        return_btn.setStyleSheet("""
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
        return_btn.clicked.connect(self.back_to_welcome)
        self.main_layout.addWidget(return_btn)

        # 5) Set it all on the widget
        self.setLayout(self.main_layout)

        # 6) Create and store buttons
        self.buttons = []
        self.button_texts = [
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
        for text in self.button_texts:
            btn = QPushButton(text)
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
            btn.clicked.connect(lambda _, t=text: self.not_implemented(t))
            self.buttons.append(btn)

        # 7) Lay them out
        self.update_grid_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # only update after grid_layout exists
        if hasattr(self, 'grid_layout'):
            self.update_grid_layout()


    def update_grid_layout(self):
        # clear existing
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            widget.setParent(None)

        # decide columns
        w = self.width()
        if w >= 1200:
            cols = 3
        elif w >= 800:
            cols = 2
        else:
            cols = 1

        # re-add
        for idx, btn in enumerate(self.buttons):
            r, c = divmod(idx, cols)
            self.grid_layout.addWidget(btn, r, c)

    def not_implemented(self, feature_name):
        QMessageBox.information(self, "Coming Soon",
                                f"🔧 '{feature_name}' will be added soon.")

    def back_to_welcome(self):
        if self.return_to_welcome:
            self.return_to_welcome()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.toggle_window_mode()

    def toggle_window_mode(self):
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
    win = Dashboard()
    win.show()
    sys.exit(app.exec_())
