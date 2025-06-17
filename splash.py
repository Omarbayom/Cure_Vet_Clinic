import sys
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap

class SplashScreen(QWidget):
    # Signal emitted when loading completes
    finished = pyqtSignal()

    def __init__(self, logo_path="assets/logo.png", duration_ms=2000):
        super().__init__()
        self.duration = duration_ms
        self.progress = 0
        self._build_ui(logo_path)

        # Make window frameless, always on top, and transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Center on screen
        self.resize(400, 400)
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center.x() - self.width() // 2,
                  screen_center.y() - self.height() // 2)

        # Timer to advance the progress bar in 100 steps
        interval = max(1, duration_ms // 100)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(interval)

    def _build_ui(self, logo_path):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Logo in the middle
        logo = QLabel(self)
        pix = QPixmap(logo_path).scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Thin progress bar underneath
        self._bar = QProgressBar(self)
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedWidth(250)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                background-color: rgba(255,255,255,30);
            }
            QProgressBar::chunk {
                background-color: white;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self._bar)

    def _update_progress(self):
        self.progress += 1
        self._bar.setValue(self.progress)
        if self.progress >= 100:
            self._timer.stop()
            self.finished.emit()
            self.close()

    def keyPressEvent(self, event):
        # Ignore all key presses during the splash
        event.ignore()
