import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from welcome import WelcomeWidget
from dashboard import DashboardWidget

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("𝐂ure Vet Clinic")
        self.showFullScreen()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome = WelcomeWidget(on_start=self.show_dashboard)
        self.dashboard = DashboardWidget(on_back=self.show_welcome)

        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.welcome)

    def keyPressEvent(self, event):
        # ESC toggles full-screen/windowed for the entire app
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            # pass other keys down to default handler
            super().keyPressEvent(event)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def show_welcome(self):
        self.stack.setCurrentWidget(self.welcome)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())
