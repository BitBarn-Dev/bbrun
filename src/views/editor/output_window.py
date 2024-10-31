from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QFont

class OutputWindow(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setup_output_window()

    def setup_output_window(self):
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #9CDCFE;
                border: none;
                border-top: 1px solid #333333;
            }
        """)
        self.setMinimumHeight(100)
