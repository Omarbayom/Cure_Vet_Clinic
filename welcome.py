import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QTimer, QDateTime, QEvent

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("𝐂ure Vet Clinic - Welcome")
        self.showFullScreen()
        self.is_fullscreen = True

        self.setup_background()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(30)

        # Top-right control bar
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignRight)
        top_bar.setSpacing(10)

        minimize_btn = QPushButton("➖")
        minimize_btn.setFixedSize(40, 30)
        minimize_btn.setToolTip("Minimize")
        minimize_btn.setStyleSheet(self.button_style())
        minimize_btn.clicked.connect(self.showMinimized)

        toggle_btn = QPushButton("▭")
        toggle_btn.setFixedSize(40, 30)
        toggle_btn.setToolTip("Toggle Window Size")
        toggle_btn.setStyleSheet(self.button_style())
        toggle_btn.clicked.connect(self.toggle_window_mode)

        close_btn = QPushButton("✖")
        close_btn.setFixedSize(40, 30)
        close_btn.setToolTip("Close")
        close_btn.setStyleSheet(self.button_style("red"))
        close_btn.clicked.connect(self.close)

        top_bar.addWidget(minimize_btn)
        top_bar.addWidget(toggle_btn)
        top_bar.addWidget(close_btn)
        main_layout.addLayout(top_bar)

        # Logo with shadow
        logo_label = QLabel()
        logo_path = os.path.join("assets", "logo.png")
        pixmap = QPixmap(logo_path).scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 5)
        logo_label.setGraphicsEffect(shadow)

        # Clock and Date
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.datetime_label.setStyleSheet("color: white")
        self.datetime_label.setAlignment(Qt.AlignCenter)
        self.update_time()

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

        # Start Button
        start_button = QPushButton("🚀 Start Cure Vet Clinic")
        start_button.setFont(QFont("Segoe UI", 20, QFont.Bold))
        start_button.setCursor(Qt.PointingHandCursor)
        start_button.setStyleSheet("""
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
        start_button.clicked.connect(self.launch_main_app)

        # Center layout for logo and rest
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.addSpacing(40)
        center_layout.addWidget(logo_label)
        center_layout.addSpacing(50)
        center_layout.addWidget(self.datetime_label)
        center_layout.addSpacing(40)
        center_layout.addWidget(start_button)

        main_layout.addLayout(center_layout)
        self.setLayout(main_layout)

    def setup_background(self):
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#009999"))
        gradient.setColorAt(1.0, QColor("#006666"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def update_time(self):
        current = QDateTime.currentDateTime()
        self.datetime_label.setText(
            current.toString("dddd, MMMM d, yyyy   ⏰  hh:mm:ss AP")
        )

    def toggle_window_mode(self):
        if self.isFullScreen():
            self.showNormal()
            self.resize(1000, 600)
            self.move(200, 100)
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def button_style(self, text_color="black"):
        return f"""
            QPushButton {{
                background-color: white;
                color: {text_color};
                border: none;
                font-size: 18px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #e0f7f7;
            }}
        """

    def launch_main_app(self):
        print("Launching main app...")  # Replace with actual transition
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.toggle_window_mode()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec_())