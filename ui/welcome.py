from PyQt5.QtWidgets import (
    QWidget, QGraphicsDropShadowEffect, QPushButton,
    QLabel, QVBoxLayout
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime
import sys, os

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and for PyInstaller bundle.
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.getcwd()
    return os.path.join(base, relative_path)

class WelcomeWidget(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start
        self.build_ui()

    def paintEvent(self, event):
        """Paint a vertical teal gradient behind everything."""
        p = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#009999"))
        grad.setColorAt(1.0, QColor("#006666"))
        p.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(60)

        logo = QLabel()
        pix = QPixmap(resource_path("assets/logo.png")).scaled(300, 300,
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignCenter)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        logo.setGraphicsEffect(shadow)
        layout.addWidget(logo)

        self.dt = QLabel()
        self.dt.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.dt.setStyleSheet("color: white")
        self.dt.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.dt)
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

        btn = QPushButton("🚀 Start Cure Vet Clinic")
        btn.setFont(QFont("Segoe UI", 18, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.on_start)
        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #009999;
                padding: 18px 36px;
                border-radius: 16px;
                border: 2px solid #007f7f;
            }
            QPushButton:hover {
                background-color: #e6f2f2;
            }
        """)
        layout.addWidget(btn)

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.dt.setText(now.toString("dddd, MMMM d, yyyy   ⏰  hh:mm:ss AP"))
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.on_start()
        else:
            super().keyPressEvent(event)
