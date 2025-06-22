import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QDateEdit,
    QComboBox, QSpinBox, QPushButton, QFormLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox, QToolButton,
    QSizePolicy, QFrame, QGraphicsDropShadowEffect,
    QApplication
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QDate

from db_manager import (
    get_all_species, add_species,
    get_colors_by_species, add_color,
    get_owner_by_phone, add_owner,
    get_pets_by_owner, add_pet,
    find_pet, update_pet
)

class AddPatientPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()

    def paintEvent(self, event):
        # Draw top gradient
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

        # Back button
        top = QHBoxLayout()
        top.setContentsMargins(10, 10, 10, 5)
        back = QToolButton()
        back.setText("←")
        back.setFont(QFont("Segoe UI", 20))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            "QToolButton { color: white; background: transparent; border: none; }"
            "QToolButton:hover { color: #e0e0e0; }"
        )
        back.clicked.connect(self.on_back)
        top.addWidget(back, Qt.AlignLeft)
        top.addStretch()
        main.addLayout(top)

        # Header
        hdr = QHBoxLayout()
        hdr.addStretch()
        plus = QLabel("➕")
        plus.setFont(QFont("Segoe UI", 26))
        plus.setStyleSheet("color: white; background: transparent;")
        title = QLabel("Add New Patient")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        hdr.addWidget(plus)
        hdr.addWidget(title)
        hdr.addStretch()
        main.addLayout(hdr)

        # Form panel
        panel = QFrame()
        panel.setStyleSheet("QFrame { background: #e0e0e0; border-radius: 8px; }")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        form = QFormLayout(panel)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(18)
        form.setContentsMargins(20, 20, 20, 20)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        def mk(widget):
            widget.setFont(QFont("Segoe UI", 18))
            widget.setStyleSheet(
                "background: white; border: 1px solid #ccc;"
                "border-radius: 4px; padding: 8px;"
            )
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return widget

        def lbl(text):
            l = QLabel(text)
            l.setFont(QFont("Segoe UI", 18))
            l.setStyleSheet("color: #333;")
            return l

        # Fields
        self.phone_input = mk(QLineEdit())
        self.phone_input.setPlaceholderText("Contact phone")
        self.phone_input.editingFinished.connect(self._lookup_owner)

        self.owner_name = mk(QLineEdit())
        self.owner_name.setPlaceholderText("Owner full name")

        self.pet_name = mk(QLineEdit())
        self.pet_name.setPlaceholderText("Pet name")

        self.species = mk(QComboBox())
        self.species.setEditable(True)
        self.species.addItems(get_all_species())
        self.species.lineEdit().setPlaceholderText("Select or type species")
        self.species.currentTextChanged.connect(self._on_species_changed)

        self.color = mk(QComboBox())
        self.color.setEditable(True)
        self.color.addItems(get_colors_by_species(self.species.currentText()))
        self.color.lineEdit().setPlaceholderText("Select or type color")

        self.first_visit = mk(QDateEdit())
        self.first_visit.setCalendarPopup(True)
        self.first_visit.setDate(QDate.currentDate())

        self.gender = mk(QComboBox())
        self.gender.addItems(["Male", "Female"])

        self.age = mk(QSpinBox())
        self.age.setRange(0, 100)
        self.age.setValue(0)

        # Add rows
        for label, widget in [
            ("Phone*:",       self.phone_input),
            ("Owner Name*:",  self.owner_name),
            ("Pet Name*:",    self.pet_name),
            ("Species*:",     self.species),
            ("Color*:",       self.color),
            ("First Visit*:", self.first_visit),
            ("Gender*:",      self.gender),
            ("Age*:",         self.age),
        ]:
            form.addRow(lbl(label), widget)

        # Center panel
        ph = QHBoxLayout()
        ph.setContentsMargins(20, 10, 20, 10)
        ph.addStretch()
        ph.addWidget(panel)
        ph.addStretch()
        main.addLayout(ph)

        # Save / Cancel buttons
        bh = QHBoxLayout()
        bh.setContentsMargins(20, 10, 20, 20)
        bh.addStretch()
        save = QPushButton("💾 Save")
        save.setFont(QFont("Segoe UI", 16))
        save.setCursor(Qt.PointingHandCursor)
        save.setFixedSize(120, 40)
        save.setStyleSheet(
            "QPushButton { background: #009999; color: white; border-radius: 4px; }"
            "QPushButton:hover { background: #008080; }"
        )
        save.clicked.connect(self._save)

        cancel = QPushButton("✖ Cancel")
        cancel.setFont(QFont("Segoe UI", 16))
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setFixedSize(120, 40)
        cancel.setStyleSheet(
            "QPushButton { background: #b40000; color: white; border-radius: 4px; }"
            "QPushButton:hover { background: #8a0000; }"
        )
        cancel.clicked.connect(self._handle_cancel)

        bh.addWidget(save)
        bh.addWidget(cancel)
        main.addLayout(bh)

    def _lookup_owner(self):
        phone = self.phone_input.text().strip()
        if not phone:
            return
        owner = get_owner_by_phone(phone)
        if owner:
            self.owner_name.setText(owner['name'])
        else:
            self.owner_name.clear()

    def _on_species_changed(self, species):
        self.color.clear()
        self.color.addItems(get_colors_by_species(species))

    def _clear_form(self):
        self.phone_input.clear()
        self.owner_name.clear()
        self.pet_name.clear()

        self.species.blockSignals(True)
        self.species.clear()
        self.species.addItems(get_all_species())
        self.species.lineEdit().clear()
        self.species.blockSignals(False)

        self.color.blockSignals(True)
        self.color.clear()
        self.color.addItems(get_colors_by_species(self.species.currentText()))
        self.color.lineEdit().clear()
        self.color.blockSignals(False)

        self.first_visit.setDate(QDate.currentDate())
        self.gender.setCurrentText("Male")
        self.age.setValue(0)

    def _handle_cancel(self):
        self._clear_form()
        self.on_back()

    def _save(self):
        phone       = self.phone_input.text().strip()
        owner       = self.owner_name.text().strip()
        pet         = self.pet_name.text().strip()
        species     = self.species.currentText().strip()
        color       = self.color.currentText().strip()
        first_visit = self.first_visit.date().toPyDate().isoformat()
        gender      = self.gender.currentText().strip()
        age         = self.age.value()

        # Validate required
        if not all([phone, owner, pet, species, color, first_visit]):
            QMessageBox.warning(
                self, "Validation Error",
                "Please fill in all required fields."
            )
            return

        # Ensure species & color exist
        if species not in get_all_species():
            add_species(species)
        if color not in get_colors_by_species(species):
            add_color(color)

        # Upsert owner
        owner_id = add_owner({'name': owner, 'phone': phone})

        # Check for existing pet
        existing = find_pet(owner_id, species, pet)
        if existing:
            resp = QMessageBox.question(
                self,
                "Pet Already Exists",
                f"A {species} named {pet} already exists for this owner.\n"
                "Update that record?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                pet_data = {
                    'owner_id':    owner_id,
                    'pet_name':    pet,
                    'species':     species,
                    'color':       color,
                    'first_visit': first_visit,
                    'gender':      gender,
                    'age':         age
                }
                update_pet(existing['id'], pet_data)
                QMessageBox.information(self, "Updated", "Pet record updated.")
                self._clear_form()
                self.on_back()
                return
            else:
                return  # user chose not to update

        # No existing → insert new
        pet_data = {
            'owner_id':    owner_id,
            'pet_name':    pet,
            'species':     species,
            'color':       color,
            'first_visit': first_visit,
            'gender':      gender,
            'age':         age
        }
        try:
            add_pet(pet_data)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return

        QMessageBox.information(self, "Success", "Patient added successfully.")
        self._clear_form()
        self.on_back()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    page = AddPatientPage(on_back=app.quit)
    page.resize(900, 650)
    page.show()
    sys.exit(app.exec_())
