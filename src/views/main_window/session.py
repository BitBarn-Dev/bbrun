from PySide2.QtCore import QSettings
import os

class SessionManager:
    def __init__(self):
        self.settings = QSettings('PythonExecutor', 'CodeEditor')

    def save_session(self, open_files):
        # Only save valid file paths
        valid_files = [f for f in open_files if f and os.path.isfile(f)]
        self.settings.setValue('open_files', valid_files)

    def load_session(self):
        files = self.settings.value('open_files', [])
        if files is None:
            return []
        # Filter out invalid paths
        return [f for f in files if f and os.path.isfile(f)]