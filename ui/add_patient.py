import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QDateEdit,
    QComboBox, QSpinBox, QPushButton, QFormLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox, QToolButton,
    QSizePolicy, QFrame, QGraphicsDropShadowEffect,
    QApplication, QCalendarWidget,QDialog
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor,QIcon
from PyQt5.QtCore import Qt, QDate

from db_manager import (
    get_all_species, add_species,
    get_owner_by_phone, add_owner, add_pet,
    find_pet, update_pet
)

class StyledDialog(QDialog):
    INFO, WARNING, QUESTION = range(3)

    ICONS = {
        INFO:    QIcon.fromTheme("dialog-information"),
        WARNING: QIcon.fromTheme("dialog-warning"),
        QUESTION: QIcon.fromTheme("dialog-question")
    }

    def __init__(
        self,
        title: str,
        message: str,
        dialog_type: int = INFO,
        buttons: list[tuple] = [("OK", True)],
        parent=None
    ):
        super().__init__(parent)
        # ── Frameless window with custom border ──
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #006666;
                border-radius: 8px;
            }
            QLabel#hdr {
                background-color: #006666;
                color: #ffffff;
                padding: 12px 20px;
                font-size: 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QLabel#body {
                background-color: #f9f9f9;
                font-size: 18px;
                padding: 20px;
            }
            QWidget#footer {
                background-color: #ffffff;
                padding: 12px 0;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px 24px;
                border-radius: 6px;
                border: none;
                background-color: #006666;
                color: #ffffff;
            }
            QPushButton:hover { background-color: #008080; }
            QPushButton:pressed { background-color: #005757; }
        """)
        # ── Adjust size based on buttons ──
        self.setFixedSize(420, 220 + 40 * (len(buttons) - 1))

        # ── Main layout with inset margins ──
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        # Header
        hdr = QLabel(f"  {title}", objectName="hdr")
        hdr.setFont(QFont("Segoe UI", 18, QFont.Bold))
        hdr.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        icon = StyledDialog.ICONS.get(dialog_type)
        if icon:
            hdr.setPixmap(icon.pixmap(24, 24))
            hdr.setIndent(30)
        layout.addWidget(hdr)

        # Body message
        body = QLabel(message, objectName="body")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(body)

        # Footer container with buttons
        footer = QWidget(objectName="footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        footer_layout.setSpacing(16)
        footer_layout.addStretch(1)
        for label, is_accept in buttons:
            btn = QPushButton(label)
            btn.clicked.connect(self.accept if is_accept else self.reject)
            footer_layout.addWidget(btn)
        footer_layout.addStretch(1)
        layout.addWidget(footer)

class AddPatientPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()

    def paintEvent(self, event):
        # Top gradient
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, int(self.height() * 0.12))
        grad.setColorAt(0, QColor("#009999"))
        grad.setColorAt(1, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _build_ui(self):
        self.setStyleSheet("background-color: #f2f2f2;")
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Back Arrow ──
        top = QHBoxLayout(); top.setContentsMargins(10, 10, 10, 5)
        back = QToolButton()
        back.setText("←"); back.setFont(QFont("Segoe UI", 20))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            "QToolButton { color:white; background:transparent; border:none; }"
            "QToolButton:hover { color:#e0e0e0; }"
        )
        back.clicked.connect(self.on_back)
        top.addWidget(back, Qt.AlignLeft); top.addStretch()
        main.addLayout(top)

        # ── Header ──
        hdr = QHBoxLayout(); hdr.addStretch()
        plus = QLabel("➕"); plus.setFont(QFont("Segoe UI", 26))
        plus.setStyleSheet("color:white; background:transparent;")
        title = QLabel("Add New Patient")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        hdr.addWidget(plus); hdr.addWidget(title); hdr.addStretch()
        main.addLayout(hdr)

        # ── Form Panel ──
        panel = QFrame()
        panel.setStyleSheet("QFrame{background:#e0e0e0;border-radius:8px;}")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(15); shadow.setOffset(0,3); shadow.setColor(QColor(0,0,0,60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        form = QFormLayout(panel)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft|Qt.AlignTop)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(18)
        form.setContentsMargins(20,20,20,20)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        def mk(widget):
            # big font + sizing
            font = QFont("Segoe UI", 18)
            widget.setFont(font)
            widget.setStyleSheet("""
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                min-height: 40px;
            """)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # extra for combo-popups
            if isinstance(widget, QComboBox):
                view = widget.view()
                view.setFont(font)
                view.setStyleSheet("""
                    QListView {
                        font-family: Segoe UI;
                        font-size: 18pt;
                    }
                    QListView::item {
                        min-height: 40px;
                    }
                """)
            return widget

        def lbl(text):
            l = QLabel(text)
            l.setFont(QFont("Segoe UI", 18))
            l.setStyleSheet("color:#333;")
            return l

        # ── Form Fields ──
        self.phone_input = mk(QLineEdit())
        self.phone_input.setPlaceholderText("Contact phone")
        self.phone_input.editingFinished.connect(self._lookup_owner)

        self.owner_name = mk(QLineEdit())
        self.owner_name.setPlaceholderText("Owner full name")

        self.pet_name = mk(QLineEdit())
        self.pet_name.setPlaceholderText("Pet name")

        self.species = mk(QComboBox()); self.species.setEditable(True)
        self.species.addItems(get_all_species())
        self.species.lineEdit().setPlaceholderText("Select or type species")
        # ── Make the editable combo’s line-edit match the other inputs ──
        le = self.species.lineEdit()
        le.setFont(QFont("Segoe UI", 18))
        le.setStyleSheet("""
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 12px;
            min-height: 40px;
        """)

        self.first_visit = mk(QDateEdit())
        self.first_visit.setCalendarPopup(True)
        self.first_visit.setDisplayFormat("dd MMMM yyyy")

        # create a calendar that always shows the nav‐bar
        cal = QCalendarWidget(self)
        cal.setNavigationBarVisible(True)

        # make the whole calendar bigger
        cal.setMinimumSize(360, 300)
        cal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # bump up the font so day‐numbers and headers are larger
        cal.setFont(QFont("Segoe UI", 14))

        # ── Force the nav‐bar text & combo to be dark and larger ──
        cal.setStyleSheet("""
            /* overall font-size for the calendar view */
            QCalendarWidget {
                font-size: 14pt;
            }
            /* navigation bar background */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: white;
                height: 40px;
            }
            /* prev/next arrows and month/year text */
            QCalendarWidget QToolButton {
                color: black;
                background: transparent;
                border: none;
                font-size: 14pt;
            }
            /* the month/year drop-down */
            QCalendarWidget QComboBox {
                color: black;
                background: white;
                font-size: 14pt;
            }
        """)

        self.first_visit.setCalendarWidget(cal)


        # sync today’s date so month/year header is drawn immediately
        today = QDate.currentDate()
        self.first_visit.setDate(today)
        cal.setSelectedDate(today)
        cal.setCurrentPage(today.year(), today.month())

        self.gender = mk(QComboBox()); self.gender.addItems(["Male","Female"])

        # add rows in order
        for label_text, widget in [
            ("Phone*:",       self.phone_input),
            ("Owner Name*:",  self.owner_name),
            ("Pet Name*:",    self.pet_name),
            ("Species*:",     self.species),
            ("First Visit*:", self.first_visit),
            ("Gender*:",      self.gender),
        ]:
            form.addRow(lbl(label_text), widget)

        # center the panel
        ch = QHBoxLayout(); ch.setContentsMargins(20,10,20,10)
        ch.addStretch(); ch.addWidget(panel); ch.addStretch()
        main.addLayout(ch)

        # ── Save / Cancel Buttons (inside panel) ──
        btn_h = QHBoxLayout()
        btn_h.setContentsMargins(0, 10, 0, 0)

        save = QPushButton("💾 Save")
        save.setFont(QFont("Segoe UI", 18))
        save.setCursor(Qt.PointingHandCursor)
        save.setFixedSize(140, 45)
        save.setStyleSheet(
            "QPushButton{background:#009999;color:white;border-radius:4px;}"
            "QPushButton:hover{background:#008080}"
        )
        save.clicked.connect(self._save)

        cancel = QPushButton("✖ Cancel")
        cancel.setFont(QFont("Segoe UI", 18))
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setFixedSize(140, 45)
        cancel.setStyleSheet(
            "QPushButton{background:#b40000;color:white;border-radius:4px;}"
            "QPushButton:hover{background:#8a0000}"
        )
        cancel.clicked.connect(self._handle_cancel)

        btn_h.addStretch()
        btn_h.addWidget(save)
        btn_h.addWidget(cancel)
        form.addRow(btn_h)

    def _lookup_owner(self):
        phone = self.phone_input.text().strip()
        if not phone:
            return
        owner = get_owner_by_phone(phone)
        if owner:
            self.owner_name.setText(owner['name'])
        else:
            self.owner_name.clear()  # silent if new

    def _clear_form(self):
        # only clear the editable fields — don’t call clear() on gender
        for w in [
            self.phone_input, self.owner_name, self.pet_name,
            self.species, self.first_visit
        ]:
            if hasattr(w, 'clear'):
                w.clear()
            elif isinstance(w, QDateEdit):
                w.setDate(QDate.currentDate())

        # reset species dropdown
        self.species.blockSignals(True)
        self.species.clear()
        self.species.addItems(get_all_species())
        self.species.lineEdit().clear()
        self.species.blockSignals(False)

        # reset gender combobox to its default first option
        self.gender.setCurrentIndex(0)


    def _handle_cancel(self):
        self._clear_form()
        self.on_back()

    def _save(self):
        phone       = self.phone_input.text().strip()
        owner       = self.owner_name.text().strip()
        pet         = self.pet_name.text().strip()
        species     = self.species.currentText().strip()
        first_visit = self.first_visit.date().toPyDate().isoformat()
        gender      = self.gender.currentText().strip()

        if not all([phone, owner, pet, species, first_visit]):
            dlg = StyledDialog(
                title="Validation Error",
                message="Please fill all required fields.",
                dialog_type=StyledDialog.WARNING,
                buttons=[("OK", True)],
                parent=self
            )
            dlg.exec_()
            return

        # ensure species/color exist
        if species not in get_all_species():
            add_species(species)


        owner_id = add_owner({'name': owner, 'phone': phone})

        # duplicate?
        existing = find_pet(owner_id, species, pet)
        if existing:
            dlg = StyledDialog(
                title="Pet Already Exists",
                message=f"A {species} named {pet} already exists.\nUpdate it?",
                dialog_type=StyledDialog.QUESTION,
                buttons=[("Yes", True), ("No", False)],
                parent=self
            )
            if dlg.exec_() == QDialog.Accepted:
                pet_data = {
                    'owner_id': owner_id,
                    'pet_name': pet,
                    'species': species,
                    'first_visit': first_visit,
                    'gender': gender
                }
                update_pet(existing['id'], pet_data)
                dlg = StyledDialog(
                    title="Updated",
                    message="Pet record updated.",
                    dialog_type=StyledDialog.INFO,
                    buttons=[("OK", True)],
                    parent=self
                )
                dlg.exec_()
                self._clear_form()
                self.on_back()
                return

            else:
                return

        # insert new
        pet_data = {
            'owner_id': owner_id,
            'pet_name': pet,
            'species': species,
            'first_visit': first_visit,
            'gender': gender
        }
        try:
            add_pet(pet_data)
        except Exception as e:
            dlg = StyledDialog(
                title="Database Error",
                message=str(e),
                dialog_type=StyledDialog.WARNING,
                buttons=[("OK", True)],
                parent=self
            )
            dlg.exec_()
            return

        dlg = StyledDialog(
            title="Success",
            message="Patient added.",
            dialog_type=StyledDialog.INFO,
            buttons=[("OK", True)],
            parent=self
        )
        dlg.exec_()
        self._clear_form()
        self.on_back()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    page = AddPatientPage(on_back=app.quit)
    page.resize(980, 700)
    page.show()
    sys.exit(app.exec_())
