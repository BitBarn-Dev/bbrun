# views/main_window/dialogs.py
from PySide2.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                              QDialogButtonBox, QInputDialog, QMessageBox)
from PySide2.QtCore import Qt
import datetime

class TabNameDialog(QDialog):
    def __init__(self, current_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Tab")
        self.setup_ui(current_name)

    def setup_ui(self, current_name):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(current_name, self)
        self.name_input.setMinimumWidth(250)
        layout.addRow("Tab Name:", self.name_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_name(self):
        return self.name_input.text()