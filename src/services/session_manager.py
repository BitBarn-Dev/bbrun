import os
import json
from pathlib import Path
from PyQt5.QtCore import QSettings  # Change from PySide2 to PyQt5

class SessionManager:
    def __init__(self, window=None):
        self.window = window
        self.settings = QSettings('PythonExecutor', 'CodeEditor')
        self.session_file = Path.home() / '.python_executor' / 'current_session.json'
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self._unsaved_marker = " *"

    def save_session(self, tab_widget):
        """
        Save the current session state including all tabs and their contents
        """
        session_data = []
        valid_files = []

        for i in range(tab_widget.count()):
            tab = tab_widget.widget(i)
            # Get the clean tab name without the unsaved marker
            display_name = tab.display_name  # Use the clean display name from the tab

            tab_data = {
                'filepath': tab.filepath,
                'content': tab.editor.toPlainText(),
                'metadata': tab.metadata,
                'is_saved': not tab.get_unsaved_changes(),
                'display_name': display_name
            }
            session_data.append(tab_data)

            # Track valid files for settings
            if tab.filepath and os.path.isfile(tab.filepath):
                valid_files.append(tab.filepath)

        try:
            # Save detailed session data
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            # Save file list to settings
            self.settings.setValue('open_files', valid_files)
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self):
        """
        Load the previous session state
        Returns a list of tab data dictionaries or None if no session exists
        """
        if not self.session_file.exists():
            # Try to load from settings as fallback
            files = self.settings.value('open_files', [])
            if files:
                return [{'filepath': f, 'content': '', 'metadata': {},
                        'is_saved': True, 'display_name': os.path.basename(f)}
                       for f in files if f and os.path.isfile(f)]
            return None

        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

                # Validate and clean the session data
                valid_data = []
                for tab_data in session_data:
                    filepath = tab_data.get('filepath')
                    if filepath is None or (filepath and os.path.isfile(filepath)):
                        valid_data.append(tab_data)

                # Update settings with valid files
                valid_files = [tab['filepath'] for tab in valid_data
                             if tab['filepath'] and os.path.isfile(tab['filepath'])]
                self.settings.setValue('open_files', valid_files)

                return valid_data
        except Exception as e:
            print(f"Error loading session: {e}")
            # Try to load from settings as fallback
            return self.load_fallback_session()

    def load_fallback_session(self):
        """Load session from settings if json file fails"""
        files = self.settings.value('open_files', [])
        if files:
            return [{'filepath': f, 'content': '', 'metadata': {},
                    'is_saved': True, 'display_name': os.path.basename(f)}
                   for f in files if f and os.path.isfile(f)]
        return None

    def clean_name(self, name):
        """Remove the unsaved marker from a tab name"""
        if name.endswith(self._unsaved_marker):
            return name[:-len(self._unsaved_marker)]
        return name

    def autosave(self):
        """Automatically save the current session state"""
        if self.window and hasattr(self.window, 'tab_manager'):
            self.save_session(self.window.tab_manager.tab_widget)
