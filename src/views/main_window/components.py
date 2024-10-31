from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QStatusBar)
from PyQt5.QtCore import Qt, QSettings

class WindowComponents:
    def __init__(self, window):
        self.window = window
        self.setup_status_bar()

    def setup_run_buttons(self):
        run_container = QWidget()
        run_layout = QHBoxLayout(run_container)
        run_layout.setContentsMargins(10, 5, 10, 5)
        run_layout.addStretch()

        button_style = """
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3275E4;
            }
            QPushButton:pressed {
                background-color: #2265D4;
            }
        """

        self.window.run_button = QPushButton('Run (F5)')
        self.window.run_sudo_button = QPushButton('Run with Sudo (F6)')

        self.window.run_button.setStyleSheet(button_style)
        self.window.run_sudo_button.setStyleSheet(
            button_style.replace('#4285F4', '#F4B400')
            .replace('#3275E4', '#E4A400')
            .replace('#2265D4', '#D49300')
        )

        self.window.run_button.clicked.connect(self.window.tab_manager.run_code)
        self.window.run_sudo_button.clicked.connect(self.window.tab_manager.run_code_with_sudo)

        run_layout.addWidget(self.window.run_button)
        run_layout.addWidget(self.window.run_sudo_button)

        self.window.main_layout.addWidget(run_container)

    def setup_status_bar(self):
        self.window.status_bar = QStatusBar()
        self.window.setStatusBar(self.window.status_bar)

    def save_geometry(self):
        settings = QSettings('PythonExecutor', 'MainWindow')
        settings.setValue('geometry', self.window.saveGeometry())
        settings.setValue('windowState', self.window.saveState())

    def restore_geometry(self):
        settings = QSettings('PythonExecutor', 'MainWindow')
        if settings.value('geometry'):
            self.window.restoreGeometry(settings.value('geometry'))
        if settings.value('windowState'):
            self.window.restoreState(settings.value('windowState'))
