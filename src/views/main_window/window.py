from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import os
from services.script_manager import ScriptManager
from services.session_manager import SessionManager
from services.executor import ScriptExecutor
from .components import WindowComponents
from .menu import MenuManager
from .tab_manager import TabManager
from ..editor import CodeEditorTab

class PythonExecutor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Python Code Executor')
        self.setMinimumSize(800, 600)

        # Initialize core services
        self.script_manager = ScriptManager()
        self.session_manager = SessionManager(self)
        self.script_executor = ScriptExecutor()

        # Create main layout first
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # Initialize managers in correct order
        self.components = WindowComponents(self)
        self.tab_manager = TabManager(self)
        self.menu_manager = MenuManager(self)

        # Setup the window
        self.menu_manager.create_menu_bar()
        self.components.setup_run_buttons()
        self.components.restore_geometry()

        # Load session and setup autosave
        self.load_session()
        self.setup_autosave()

    def setup_autosave(self):
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.handle_autosave)
        self.autosave_timer.start(60000)  # Autosave every minute

    def handle_autosave(self):
        self.session_manager.save_session(self.tab_manager.tab_widget)
        self.status_bar.showMessage('Session autosaved', 2000)

    def load_session(self):
        session_data = self.session_manager.load_session()

        if session_data:
            self.tab_manager.tab_widget.clear()

            for tab_data in session_data:
                filepath = tab_data.get('filepath')
                content = tab_data.get('content', '')  # This is the unsaved content from the session
                metadata = tab_data.get('metadata', {})
                display_name = tab_data.get('display_name', 'Untitled')
                is_saved = tab_data.get('is_saved', True)

                # Create tab with initial content from session
                self.tab_manager._ignore_text_changed = True
                tab = CodeEditorTab(filepath, metadata, initial_content=content)

                # Important: Set the content and last_saved_content appropriately
                tab.editor.setPlainText(content)
                if filepath and os.path.exists(filepath):
                    # For existing files, load the last saved content for comparison
                    saved_content, _, _ = self.script_manager.load_script(filepath)
                    if saved_content is not None:
                        tab.last_saved_content = saved_content
                else:
                    # For new files or files with unsaved changes
                    tab.last_saved_content = '' if not is_saved else content

                # Add the tab and set up its status
                idx = self.tab_manager.tab_widget.addTab(tab, display_name)

                # Update the unsaved status if needed
                if not is_saved:
                    self.tab_manager.update_tab_unsaved_status(idx)

                # Set up the change handler
                self.tab_manager.setup_text_changed_handler(idx)
                self.tab_manager._ignore_text_changed = False

        if self.tab_manager.tab_widget.count() == 0:
            self.tab_manager.new_tab()

    def closeEvent(self, event):
        # Save the current session state
        self.session_manager.save_session(self.tab_manager.tab_widget)
        self.components.save_geometry()
        event.accept()
