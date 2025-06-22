import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt

from ui.splash      import SplashScreen
from ui.welcome     import WelcomeWidget
from ui.dashboard   import DashboardWidget
from ui.add_patient import AddPatientPage      # ← NEW

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cure Vet Clinic")

        # Stacked widget holds all pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.welcome     = WelcomeWidget(on_start=self.show_dashboard)
        self.dashboard   = DashboardWidget(
            on_back=self.show_welcome,
            on_add_patient=self.show_add_patient   # ← NEW
        )
        self.add_patient = AddPatientPage(on_back=self.show_dashboard)  # ← NEW

        # Add pages to the stack
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.add_patient)     # ← NEW
        self.stack.setCurrentWidget(self.welcome)

    def keyPressEvent(self, event):
        # ESC toggles full-screen/windowed
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


    def show_add_patient(self):                     # ← NEW
        self.stack.setCurrentWidget(self.add_patient)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainApp()

    # Splash
    splash = SplashScreen(duration_ms=1500)
    splash.finished.connect(main_win.showFullScreen)
    splash.finished.connect(splash.close)
    splash.show()

    sys.exit(app.exec_())
