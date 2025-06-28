# ui/inventory_list.py

import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QToolButton, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout,
    QSizePolicy, QGraphicsDropShadowEffect, QApplication,
    QAbstractItemView, QInputDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt

from db_manager import (
    get_all_inventory,
    delete_inventory_item,
    update_inventory_item
)

class InventoryListPage(QWidget):
    def __init__(self, on_back, on_add):
        super().__init__()
        self.setMinimumSize(900, 600)
        self.on_back = on_back
        self.on_add  = on_add
        self._build_ui()
        self._load_data()

    def showEvent(self, event):
        self._load_data()
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor("#009999"))
        grad.setColorAt(1.0, QColor("#006666"))
        painter.fillRect(self.rect(), grad)
        super().paintEvent(event)

    def _build_ui(self):
        # overall background
        self.setStyleSheet("background-color: #f2f2f2;")
        main = QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)

        # header bar
        hdr = QHBoxLayout(); hdr.setContentsMargins(10,10,10,10)
        back = QToolButton()
        back.setText("←"); back.setFont(QFont("Segoe UI",20))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            "QToolButton{color:white;background:transparent;border:none;}"
            "QToolButton:hover{color:#e0e0e0}"
        )
        back.clicked.connect(self.on_back)
        hdr.addWidget(back)

        title = QLabel("Manage Inventory")
        title.setFont(QFont("Segoe UI",24,QFont.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        title.setAlignment(Qt.AlignCenter)
        hdr.addWidget(title, stretch=1)

        add_btn = QPushButton("➕ Add")
        add_btn.setFont(QFont("Segoe UI",14))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(
            "QPushButton{background-color:#00b0a0;color:white;"
            "border:none;padding:6px 12px;border-radius:6px;}"
            "QPushButton:hover{background-color:#008f80}"
        )
        add_btn.clicked.connect(self.on_add)
        hdr.addWidget(add_btn)

        main.addLayout(hdr)

        # table panel
        panel = QFrame()
        panel.setStyleSheet("QFrame{background:#e0e0e0;border-radius:8px;}")
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(12); shadow.setOffset(0,2); shadow.setColor(QColor(0,0,0,50))
        panel.setGraphicsEffect(shadow)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        container = QVBoxLayout(panel)
        container.setContentsMargins(20,20,20,20)
        container.setSpacing(10)

        # table
        self.tbl = QTableWidget(0, 8)
        self.tbl.setHorizontalHeaderLabels([
            "Name", "Category", "Qty", "Unit",
            "Reorder", "Expiry", "Edit", "Delete"
        ])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setShowGrid(False)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.verticalHeader().setDefaultSectionSize(40)
        self.tbl.setColumnWidth(6, 60)
        self.tbl.setColumnWidth(7, 70)

        # blue-themed backgrounds
        self.tbl.setStyleSheet("""
            QHeaderView::section {
                background: #009999;
                color: white;
                padding: 8px;
                font-size: 16px;
                border: none;
            }
            QTableWidget {
                background-color: #e3f2fd;               /* pale blue */
                alternate-background-color: #bbdefb;     /* light blue */
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #ccc;
            }
            QTableWidget::item:selected {
                background-color: #90caf9;
            }
            QTableWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        container.addWidget(self.tbl)
        main.addWidget(panel)

    def _load_data(self):
        self.tbl.setRowCount(0)
        for item in get_all_inventory():
            if item['quantity'] == 0:
                continue

            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            # populate columns
            self.tbl.setItem(r, 0, QTableWidgetItem(item['name']))
            self.tbl.setItem(r, 1, QTableWidgetItem(item['category']))
            self.tbl.setItem(r, 2, QTableWidgetItem(str(item['quantity'])))
            self.tbl.setItem(r, 3, QTableWidgetItem(item['unit']))
            self.tbl.setItem(r, 4, QTableWidgetItem(str(item['reorder_level'])))
            self.tbl.setItem(r, 5, QTableWidgetItem(item['expiration_date']))

            # Edit reorder
            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet(
                "QPushButton{background:#007f7f;color:white;border:none;"
                "padding:4px;border-radius:4px;}"
                "QPushButton:hover{background:#005f5f}"
            )
            edit_btn.clicked.connect(lambda _, it=item: self._edit_reorder(it))
            self.tbl.setCellWidget(r, 6, edit_btn)

            # Delete
            del_btn = QPushButton("Delete")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet(
                "QPushButton{background:#b40000;color:white;border:none;"
                "padding:4px;border-radius:4px;}"
                "QPushButton:hover{background:#8a0000}"
            )
            del_btn.clicked.connect(lambda _, iid=item['id']: self._remove(iid))
            self.tbl.setCellWidget(r, 7, del_btn)

    def _edit_reorder(self, item):
        new_val, ok = QInputDialog.getInt(
            self,
            "Edit Reorder Level",
            f"New reorder for '{item['name']}' (exp {item['expiration_date']}):",
            item['reorder_level'], 0, 100000
        )
        if not ok:
            return
        update_inventory_item(item['id'], {
            'name':               item['name'],
            'category':           item['category'],
            'quantity':           item['quantity'],
            'unit':               item['unit'],
            'reorder_level':      new_val,
            'expiration_date':    item['expiration_date'],
            'default_sell_price': item['default_sell_price']
        })
        QMessageBox.information(self, "Updated", "Reorder level updated.")
        self._load_data()

    def _remove(self, item_id):
        delete_inventory_item(item_id)
        self._load_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = InventoryListPage(on_back=app.quit, on_add=app.quit)
    w.show()
    sys.exit(app.exec_())
