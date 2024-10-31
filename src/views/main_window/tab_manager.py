from PySide2.QtWidgets import (QTabWidget, QMessageBox, QInputDialog, 
                              QLineEdit)
from ..editor import CodeEditorTab
from ..editor.custom_tabbar import CustomTabBar
from ..dialogs import SaveScriptDialog, LoadScriptDialog
from .dialogs import TabNameDialog
import os
import datetime

class TabManager:
    def __init__(self, window):
        self.window = window
        self._unsaved_marker = " *"
        self._ignore_text_changed = False  # Flag to prevent initial load from triggering unsaved
        self.setup_tab_widget()

    def setup_tab_widget(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(CustomTabBar())
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.tabBar().tabMoved.connect(self.on_tab_moved)
        
        # Add this line to connect to the textChanged signal when tabs change
        self.tab_widget.currentChanged.connect(self.setup_text_changed_handler)
        
        self.window.main_layout.addWidget(self.tab_widget)

    def setup_text_changed_handler(self, index):
        """Setup the text changed handler for the current tab"""
        if index >= 0:
            current_tab = self.tab_widget.widget(index)
            if hasattr(current_tab, 'editor'):
                # Disconnect any existing connection first to prevent duplicates
                try:
                    current_tab.editor.textChanged.disconnect()
                except:
                    pass
                current_tab.editor.textChanged.connect(
                    lambda: self.handle_text_changed(current_tab)
                )

    def handle_text_changed(self, tab):
        """Handle text changes in the editor"""
        if self._ignore_text_changed:  # Skip if we're loading content
            return
            
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.update_tab_unsaved_status(index)


    def update_tab_unsaved_status(self, index):
        """Update the visual status of a tab to show unsaved changes"""
        tab = self.tab_widget.widget(index)
        current_text = self.get_clean_tab_name(index)
        has_changes = tab.get_unsaved_changes()
        
        print(f"Debug - Tab status update:")  # Debug logging
        print(f"  Current text: {current_text}")
        print(f"  Has changes: {has_changes}")
        print(f"  Current content: {tab.editor.toPlainText()[:50]}...")
        print(f"  Last saved content: {tab.last_saved_content[:50]}...")
        
        if has_changes:
            if not current_text.endswith(self._unsaved_marker):
                self.tab_widget.setTabText(index, current_text + self._unsaved_marker)
        else:
            self.tab_widget.setTabText(index, current_text)

    def get_clean_tab_name(self, index):
        """Get the tab name without the unsaved marker"""
        name = self.tab_widget.tabText(index)
        if name.endswith(self._unsaved_marker):
            return name[:-len(self._unsaved_marker)]
        return name

    def save_tab(self, tab):
        """Save the tab's content and metadata"""
        if not tab.filepath:
            return False
            
        content = tab.editor.toPlainText()
        metadata = tab.metadata
        metadata['display_name'] = self.get_clean_tab_name(self.tab_widget.indexOf(tab))
        metadata['last_modified'] = datetime.datetime.now().isoformat()
        
        try:
            self.window.script_manager.save_script(tab.filepath, content, metadata)
            tab.last_saved_content = content  # Update the saved content reference
            self.update_tab_unsaved_status(self.tab_widget.indexOf(tab))
            return True
        except Exception as e:
            QMessageBox.warning(self.window, "Save Error", f"Failed to save file: {str(e)}")
            return False

    def new_tab(self):
        """Create a new empty tab"""
        tab = CodeEditorTab()
        self.tab_widget.addTab(tab, "Untitled")
        self.tab_widget.setCurrentWidget(tab)
        self.setup_text_changed_handler(self.tab_widget.indexOf(tab))
        return tab

    def save_current(self):
        """Handle File -> Save"""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return
            
        if not current_tab.filepath:
            # No existing file - redirect to Save As
            self.save_as()
        else:
            # Update existing file
            content = current_tab.editor.toPlainText()
            if self.window.script_manager.add_version(current_tab.filepath, content, current_tab.metadata):
                self._ignore_text_changed = True  # Prevent text change event from triggering
                current_tab.last_saved_content = content  # Update the saved content reference
                current_tab.editor.setPlainText(content)  # Ensure content is set
                self.window.status_bar.showMessage('File saved', 2000)
                self.update_tab_unsaved_status(self.tab_widget.currentIndex())
                self._ignore_text_changed = False  # Re-enable text change detection
            else:
                QMessageBox.warning(self.window, "Save Error", "Failed to save file")

    def save_as(self):
        """Handle File -> Save As"""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return

        current_metadata = current_tab.metadata if hasattr(current_tab, 'metadata') else {}
        
        while True:  # Loop until we get a valid save or user cancels
            dialog = SaveScriptDialog(self.window.script_manager, current_metadata, self.window)
            if dialog.exec_():
                metadata = dialog.get_metadata()
                
                # Check if script already exists
                if self.window.script_manager.script_exists(metadata['name'], metadata['category']):
                    reply = QMessageBox.question(
                        self.window,
                        "Script Exists",
                        f"A script named '{metadata['name']}' already exists in category '{metadata['category']}'.\n\n"
                        "Do you want to choose a different name?",
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                    )
                    
                    if reply == QMessageBox.Cancel:
                        return
                    elif reply == QMessageBox.Yes:
                        continue
                    else:  # No - update existing script
                        existing_path = self.window.script_manager.scripts_dir / metadata['category'] / f"{self.window.script_manager._make_safe_filename(metadata['name'])}.json"
                        content = current_tab.editor.toPlainText()
                        if self.window.script_manager.add_version(str(existing_path), content, metadata):
                            current_tab.filepath = str(existing_path)
                            current_tab.metadata = metadata
                            current_tab.last_saved_content = content  # Update the saved content reference
                            self.tab_widget.setTabText(
                                self.tab_widget.currentIndex(),
                                metadata['display_name']
                            )
                            self.update_tab_unsaved_status(self.tab_widget.currentIndex())  # This will remove the asterisk
                            self.window.status_bar.showMessage('File saved', 2000)
                        else:
                            QMessageBox.warning(self.window, "Save Error", "Failed to save file")
                        return
                
                # Save new script
                content = current_tab.editor.toPlainText()
                filepath = self.window.script_manager.save_script(
                    metadata['name'],
                    content,
                    metadata
                )
                
                if filepath:
                    current_tab.filepath = filepath
                    current_tab.metadata = metadata
                    current_tab.last_saved_content = content  # Update the saved content reference
                    self.tab_widget.setTabText(
                        self.tab_widget.currentIndex(),
                        metadata['display_name']
                    )
                    self.update_tab_unsaved_status(self.tab_widget.currentIndex())  # This will remove the asterisk
                    self.window.status_bar.showMessage('File saved', 2000)
                    return
                else:
                    QMessageBox.warning(self.window, "Save Error", "Failed to save file")
                    continue
            else:
                return

    def open_script(self):
        """Handle File -> Open"""
        dialog = LoadScriptDialog(self.window.script_manager, self.window)
        if dialog.exec_():
            result = dialog.get_selected_script()
            if result:
                filepath, version = result
                
                # Check if already open
                for i in range(self.tab_widget.count()):
                    tab = self.tab_widget.widget(i)
                    if tab.filepath == filepath:
                        self.tab_widget.setCurrentIndex(i)
                        return

                # Load the script with the selected version
                content, metadata, _ = self.window.script_manager.load_script(filepath, version)
                if content is not None:
                    self._ignore_text_changed = True  # Prevent change detection during load
                    tab = CodeEditorTab(filepath, metadata)
                    tab.editor.setPlainText(content)
                    tab.last_saved_content = content  # Set initial saved content
                    display_name = metadata.get('display_name', metadata.get('name', 'Untitled'))
                    self.tab_widget.addTab(tab, display_name)
                    self.tab_widget.setCurrentWidget(tab)
                    self.setup_text_changed_handler(self.tab_widget.indexOf(tab))
                    self._ignore_text_changed = False  # Re-enable change detection

    def close_tab(self, index):
        """Handle tab close request"""
        tab = self.tab_widget.widget(index)
        
        if tab.get_unsaved_changes():
            reply = QMessageBox.question(
                self.window,
                "Unsaved Changes",
                "This tab has unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                if tab.filepath:
                    if not self.save_tab(tab):
                        return
                else:
                    self.save_as()
                    if tab.get_unsaved_changes():  # If save was cancelled or failed
                        return
            elif reply == QMessageBox.Cancel:
                return

        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # If it's the last tab, clear it instead of closing
            tab.editor.clear()
            tab.filepath = None
            tab.metadata = {}
            tab.last_saved_content = ""
            self.tab_widget.setTabText(index, "Untitled")
            self.update_tab_unsaved_status(index)

    def rename_current_tab(self):
        """Handle tab rename request"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            current_text = self.get_clean_tab_name(current_index)
            dialog = TabNameDialog(current_text, self.window)
            if dialog.exec_():
                new_name = dialog.get_name()
                current_tab = self.tab_widget.currentWidget()
                if current_tab and current_tab.filepath:
                    current_tab.metadata['display_name'] = new_name
                    self.save_tab(current_tab)
                self.tab_widget.setTabText(current_index, new_name)
                self.update_tab_unsaved_status(current_index)

    def run_code(self):
        """Execute current tab's code"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            code = current_tab.editor.toPlainText()
            current_tab.output_window.clear()
            self.window.script_executor.run_script(
                code,
                current_tab.output_window.append
            )

    def run_code_with_sudo(self):
        """Execute current tab's code with sudo privileges"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            password, ok = QInputDialog.getText(
                self.window, 'Sudo Password',
                'Enter your sudo password:',
                QLineEdit.Password)
                
            if ok:
                code = current_tab.editor.toPlainText()
                current_tab.output_window.clear()
                self.window.script_executor.run_script(
                    code,
                    current_tab.output_window.append,
                    sudo=True,
                    password=password
                )

    def on_tab_changed(self, index):
        """Handle tab selection change"""
        if index >= 0:
            current_tab = self.tab_widget.widget(index)
            filepath = current_tab.filepath or "Untitled"
            self.window.status_bar.showMessage(f"Current file: {filepath}")

    def on_tab_moved(self, from_index, to_index):
        """Handle tab reordering"""
        self.window.status_bar.showMessage(
            f"Tab moved from position {from_index + 1} to {to_index + 1}", 
            2000
        )
