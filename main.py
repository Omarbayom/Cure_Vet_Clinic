import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent, Qt, QTimer


from ui.splash            import SplashScreen
from ui.welcome           import WelcomeWidget
from ui.dashboard         import DashboardWidget
from ui.add_patient       import AddPatientPage
from ui.add_inventory     import AddInventoryPage
from ui.inventory_list    import InventoryListPage
from ui.add_visit         import AddVisitPage
from ui.show_history      import ShowHistoryPage
from ui.calendar_page     import CalendarPage
from ui.report            import ReportPage
from notification_manager import NotificationManager,NotificationPage



class MainApp(QMainWindow):
    def __init__(self, notif_manager):
        super().__init__()
        self.setWindowTitle("Cure Vet Clinic")

        # Keep a reference to the notification manager
        self.notif_manager = notif_manager

        # Stacked widget holds all pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.welcome          = WelcomeWidget(on_start=self.show_dashboard)
        self.dashboard = DashboardWidget(
            on_back               = self.show_welcome,
            on_book_appointment   = self.show_add_visit,
            on_show_history       = self.show_history_search,
            on_add_patient        = self.show_add_patient,
            on_manage_inventory   = self.show_inventory_list,
            on_show_calendar      = self.show_calendar_page,
            on_show_report        = self.show_report_page,
            on_show_notifications = self.show_notifications,    # ← new callback
            notif_manager         = self.notif_manager         # ← new manager
        )


        self.report_page      = ReportPage(on_back=self.show_dashboard)
        self.calendar_page    = CalendarPage(
            on_back=self.show_dashboard,
            on_show_history=self.show_history
        )
        self.add_patient      = AddPatientPage(on_back=self.show_dashboard)
        self.inventory_list   = InventoryListPage(
            on_back=self.show_dashboard,
            on_add=self.show_add_inventory
        )
        self.add_inventory    = AddInventoryPage(on_back=self.show_inventory_list)
        self.add_visit        = AddVisitPage(
            on_back=self.show_dashboard,
            on_show_history=self.show_history
        )
        self.show_history_page = ShowHistoryPage(
            on_back      = self.show_dashboard,
            on_add_visit = self.show_add_visit_for_pet
        )

        # ── NEW: Notification settings page ──────────────────────────────
        self.notification_page = NotificationPage(
            parent=self,
            notif_manager=self.notif_manager,
            on_back=self.show_dashboard
        )


        # Add pages to the stack
        for w in (
            self.welcome,
            self.dashboard,
            self.add_patient,
            self.inventory_list,
            self.add_inventory,
            self.add_visit,
            self.show_history_page,
            self.calendar_page,
            self.report_page,
            self.notification_page
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

    def changeEvent(self, event):
        """
        When the user clicks the maximize/restore button, go true full-screen,
        and when they restore out of full-screen, go back to normal.
        """
        if event.type() == QEvent.WindowStateChange:
            # user clicked “maximize”
            if self.windowState() & Qt.WindowMaximized:
                # schedule full-screen so we don’t recurse on state change
                QTimer.singleShot(0, self.showFullScreen)
            # user clicked “restore” while in full-screen
            elif not (self.windowState() & Qt.WindowFullScreen) and self.isFullScreen():
                QTimer.singleShot(0, self.showNormal)

        # always call the base implementation
        super().changeEvent(event)

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

        
    # ─── Add these navigation methods near the others ───────────────────────────

    def show_add_visit(self):
        """Dashboard → AddVisitPage with blank search."""
        self.add_visit.reset_visit_forms()
        self.stack.setCurrentWidget(self.add_visit)

    def show_history_search(self):
        """Dashboard → ShowHistoryPage in search mode."""
        # reset fields
        sh = self.show_history_page
        sh.search_input.clear()
        sh.owner_list.clear()
        sh.pet_list.clear()
        sh.history_list.clear()
        sh.details.clear()
        sh.new_visit_btn.setEnabled(False)
        self.stack.setCurrentWidget(sh)

    def show_history(self, owner, pet):
        """
        Dashboard → ShowHistoryPage for this (owner,pet)
        (without needing a show_history() method on the page itself)
        """
        page = self.show_history_page

        # 1) Bring up the History page
        self.stack.setCurrentWidget(page)

        # 2) Run the owner‐search logic
        page.search_input.setText(owner['name'])          # triggers on_search_owner :contentReference[oaicite:0]{index=0}
        # 3) Find & select the exact owner item
        for i in range(page.owner_list.count()):
            itm = page.owner_list.item(i)
            if itm.data['id'] == owner['id']:
                page.owner_list.setCurrentItem(itm)
                page.on_owner_selected(itm)
                break

        # 4) Find & select the right pet
        for i in range(page.pet_list.count()):
            itm = page.pet_list.item(i)
            # pet_list items store {'species', 'pet_name'} in itm.data :contentReference[oaicite:1]{index=1}
            d = itm.data
            if d['pet_name'] == pet['pet_name'] and d['species'] == pet['species']:
                page.pet_list.setCurrentItem(itm)
                page.on_pet_selected(itm)
                break

        # 5) Now the visit‐list is loaded and you can click through it in the UI


    def show_add_visit_for_pet(self, owner, pet):
        """ShowHistoryPage → AddVisitPage pre-filled for this (owner,pet)."""
        self.add_visit.set_context(owner, pet)
        self.stack.setCurrentWidget(self.add_visit)

    def show_calendar_page(self):
        """
        Switch to the CalendarPage, reloading its data first.
        """
        # reload appointments in case anything changed
        self.calendar_page._load_appointments()
        # show it
        self.stack.setCurrentWidget(self.calendar_page)
    
    def show_report_page(self):
        self.stack.setCurrentWidget(self.report_page)

    def show_notifications(self):
        self.stack.setCurrentWidget(self.notification_page)


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
        # 1) start notifications
    notif_manager = NotificationManager(parent=None)
    main_win = MainApp(notif_manager)

    # Splash
    splash = SplashScreen(duration_ms=1500)
    splash.finished.connect(main_win.showFullScreen)
    splash.finished.connect(splash.close)
    splash.show()

    sys.exit(app.exec_())
