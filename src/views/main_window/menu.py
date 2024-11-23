from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence
import os
import platform
import subprocess
from .pip_dialogs import RequirementsEditor, PipExecutorDialog

class MenuManager:
    def __init__(self, window):
        self.window = window

    def create_menu_bar(self):
        menubar = self.window.menuBar()

        # File Menu
        file_menu = menubar.addMenu('&File')
        self.create_file_menu(file_menu)

        # Edit Menu
        edit_menu = menubar.addMenu('&Edit')
        self.create_edit_menu(edit_menu)

        # Run Menu
        run_menu = menubar.addMenu('&Run')
        self.create_run_menu(run_menu)

        # Pip Menu
        pip_menu = menubar.addMenu('&Pip')
        self.create_pip_menu(pip_menu)

    def create_file_menu(self, menu):
        actions = [
            ('&New', QKeySequence.New, self.window.tab_manager.new_tab),
            ('&Open...', QKeySequence.Open, self.window.tab_manager.open_script),
            ('&Save', QKeySequence.Save, self.window.tab_manager.save_current),
            ('Save &As...', QKeySequence.SaveAs, self.window.tab_manager.save_as),
            (None, None, None),
            ('Open Scripts &Folder', None, self.open_scripts_folder),
            (None, None, None),
            ('&Exit', QKeySequence.Quit, self.window.close)
        ]

        self.add_actions(menu, actions)

    def create_edit_menu(self, menu):
        rename_action = QAction('Rename Tab', self.window)
        rename_action.setShortcut('F2')
        rename_action.triggered.connect(self.window.tab_manager.rename_current_tab)
        menu.addAction(rename_action)

    def create_run_menu(self, menu):
        actions = [
            ('&Run', 'F5', self.window.tab_manager.run_code),
            ('Run with &Sudo', 'F6', self.window.tab_manager.run_code_with_sudo)
        ]

        self.add_actions(menu, actions)

    def create_pip_menu(self, menu):
        # Requirements editor action
        req_action = QAction('Edit Requirements...', self.window)
        req_action.triggered.connect(self.show_requirements_editor)
        menu.addAction(req_action)

        # Pip executor action
        pip_action = QAction('Pip Command...', self.window)
        pip_action.triggered.connect(self.show_pip_executor)
        menu.addAction(pip_action)

    def show_requirements_editor(self):
        dialog = RequirementsEditor(self.window)
        dialog.exec_()

    def show_pip_executor(self):
        dialog = PipExecutorDialog(self.window)
        dialog.exec_()

    def add_actions(self, menu, actions):
        for name, shortcut, handler in actions:
            if name is None:
                menu.addSeparator()
                continue
            action = QAction(name, self.window)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(handler)
            menu.addAction(action)

    def open_scripts_folder(self):
        """Open the scripts folder in the system's default file explorer"""
        scripts_path = str(self.window.script_manager.scripts_dir)

        if platform.system() == 'Windows':
            os.startfile(scripts_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', scripts_path])
        else:  # Linux and other Unix-like
            subprocess.run(['xdg-open', scripts_path])