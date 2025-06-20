import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from ui.splash import SplashScreen
from ui.welcome import WelcomeWidget
from ui.dashboard import DashboardWidget

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cure Vet Clinic")

        # Create a stacked widget to hold pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Instantiate your pages
        self.welcome   = WelcomeWidget(on_start=self.show_dashboard)
        self.dashboard = DashboardWidget(on_back=self.show_welcome)

        # Add pages to the stack
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.welcome)

    def keyPressEvent(self, event):
        # ESC toggles full-screen/windowed for the main window
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def show_welcome(self):
        self.stack.setCurrentWidget(self.welcome)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create but do not show the main window yet
    main_win = MainApp()

    # Create and show the splash screen
    splash = SplashScreen(duration_ms=1500)  # 1.5s duration
    # When splash finishes, show the main window full-screen
    splash.finished.connect(main_win.showFullScreen)
    splash.finished.connect(splash.close)
    splash.show()

    sys.exit(app.exec_())
