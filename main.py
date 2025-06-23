import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt

from ui.splash            import SplashScreen
from ui.welcome           import WelcomeWidget
from ui.dashboard         import DashboardWidget
from ui.add_patient       import AddPatientPage
from ui.add_inventory     import AddInventoryPage
from ui.inventory_list    import InventoryListPage

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cure Vet Clinic")

        # Stacked widget holds all pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.welcome          = WelcomeWidget(on_start=self.show_dashboard)
        self.dashboard        = DashboardWidget(
            on_back=self.show_welcome,
            on_add_patient=self.show_add_patient,
            on_manage_inventory=self.show_inventory_list

        )


        self.add_patient      = AddPatientPage(on_back=self.show_dashboard)
        self.inventory_list   = InventoryListPage(on_back=self.show_dashboard,
                                                  on_add=self.show_add_inventory)
        self.add_inventory    = AddInventoryPage(on_back=self.show_inventory_list)


        # Add pages to the stack
        for w in (
            self.welcome,
            self.dashboard,
            self.add_patient,
            self.inventory_list,
            self.add_inventory
        ):
            self.stack.addWidget(w)

        # start on welcome
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

    # ─── Navigation Callbacks ─────────────────────────────────────────────────

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def show_welcome(self):
        self.stack.setCurrentWidget(self.welcome)

    def show_add_patient(self):
        self.stack.setCurrentWidget(self.add_patient)

    def show_inventory_list(self):
        self.stack.setCurrentWidget(self.inventory_list)

    def show_add_inventory(self):
        self.stack.setCurrentWidget(self.add_inventory)
    def show_remove_inventory(self):
        self.stack.setCurrentWidget(self.remove_inventory)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainApp()

    # Splash
    splash = SplashScreen(duration_ms=1500)
    splash.finished.connect(main_win.showFullScreen)
    splash.finished.connect(splash.close)
    splash.show()

    sys.exit(app.exec_())
