import os
import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QTextEdit, QComboBox,
                             QPushButton, QDialogButtonBox, QListWidget,
                             QWidget, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt

class SaveScriptDialog(QDialog):
    def __init__(self, script_manager, current_metadata=None, parent=None):
        super().__init__(parent)
        self.script_manager = script_manager
        self.current_metadata = current_metadata or {}
        self.setup_ui()
        self.setWindowTitle("Save Script")
        self.setMinimumWidth(400)

    def setup_ui(self):
        layout = QFormLayout(self)

        # Script name
        self.name_input = QLineEdit(self.current_metadata.get('name', ''))
        self.name_input.setPlaceholderText("Enter script name")
        layout.addRow("Name:", self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter script description")
        self.description_input.setMaximumHeight(100)
        self.description_input.setText(self.current_metadata.get('description', ''))
        layout.addRow("Description:", self.description_input)

        # Category with custom input
        self.category_layout = QVBoxLayout()
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(self.script_manager.categories)

        if 'category' in self.current_metadata:
            self.category_input.setCurrentText(self.current_metadata['category'])

        self.category_input.currentTextChanged.connect(self.handle_category_change)
        layout.addRow("Category:", self.category_input)

        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def handle_category_change(self, text):
        if text and text not in self.script_manager.categories:
            reply = QMessageBox.question(
                self,
                "New Category",
                f"Create new category '{text}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.script_manager.add_category(text)
            else:
                self.category_input.setCurrentText(self.script_manager.categories[0])

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Script name is required")
            return

        self.accept()

    def get_metadata(self):
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'category': self.category_input.currentText().strip(),
            'created': self.current_metadata.get('created'),
            'display_name': self.name_input.text().strip()
        }

class LoadScriptDialog(QDialog):
    def __init__(self, script_manager, parent=None):
        super().__init__(parent)
        self.script_manager = script_manager
        self.selected_script = None
        self.selected_version = None
        self.setup_ui()
        self.setWindowTitle("Load Script")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Left side - Script selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(self.script_manager.categories)
        self.category_filter.currentTextChanged.connect(self.filter_scripts)
        left_layout.addWidget(QLabel("Category:"))
        left_layout.addWidget(self.category_filter)

        # Script list
        self.script_list = QListWidget()
        self.script_list.currentItemChanged.connect(self.update_script_details)
        left_layout.addWidget(QLabel("Scripts:"))
        left_layout.addWidget(self.script_list)

        layout.addWidget(left_panel)

        # Right side - Script details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Metadata display
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        self.metadata_display.setMaximumHeight(200)
        right_layout.addWidget(QLabel("Script Details:"))
        right_layout.addWidget(self.metadata_display)

        # Version selection
        self.version_combo = QComboBox()
        self.version_combo.currentIndexChanged.connect(self.update_version_details)
        right_layout.addWidget(QLabel("Version:"))
        right_layout.addWidget(self.version_combo)

        # Version details
        self.version_details = QTextEdit()
        self.version_details.setReadOnly(True)
        right_layout.addWidget(QLabel("Version Details:"))
        right_layout.addWidget(self.version_details)

        layout.addWidget(right_panel)

        # Buttons at bottom
        buttons = QDialogButtonBox(
            QDialogButtonBox.Open | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        button_layout = QVBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(buttons)
        right_layout.addLayout(button_layout)

        # Set panel sizes
        layout.setStretch(0, 1)  # Left panel
        layout.setStretch(1, 2)  # Right panel

        # Initial load
        self.load_scripts()

    def load_scripts(self):
        self.script_list.clear()
        self.scripts = self.script_manager.list_scripts()
        self.filter_scripts()

    def filter_scripts(self):
        self.script_list.clear()
        category = self.category_filter.currentText()

        for filepath, metadata in self.scripts:
            if category != "All Categories" and metadata.get('category') != category:
                continue

            display_name = metadata.get('display_name', metadata.get('name', 'Untitled'))
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, (filepath, metadata))
            self.script_list.addItem(item)

    def update_script_details(self, current, previous):
        self.version_combo.clear()
        self.metadata_display.clear()
        self.version_details.clear()

        if not current:
            return

        filepath, metadata = current.data(Qt.UserRole)
        content, metadata, versions = self.script_manager.load_script(filepath)

        # Display metadata
        metadata_text = f"""
Name: {metadata.get('name', 'Untitled')}
Category: {metadata.get('category', 'Uncategorized')}
Description: {metadata.get('description', 'No description')}
Created: {metadata.get('created', 'Unknown')}
Last Modified: {metadata.get('last_modified', 'Unknown')}
        """
        self.metadata_display.setText(metadata_text)

        # Populate versions
        if versions:
            for version in versions:
                version_name = f"Version {version['version_number']} - {version['timestamp']}"
                self.version_combo.addItem(version_name, version)

            # Select the most recent version
            self.version_combo.setCurrentIndex(len(versions) - 1)

    def update_version_details(self, index):
        if index < 0:
            return

        version = self.version_combo.itemData(index)
        if version:
            details = f"""
Version: {version['version_number']}
Created: {version['timestamp']}
Content Preview:
----------------
{version['content'][:200]}{'...' if len(version['content']) > 200 else ''}"""
            self.version_details.setText(details)

    def get_selected_script(self):
        current_item = self.script_list.currentItem()
        if not current_item:
            return None

        filepath, metadata = current_item.data(Qt.UserRole)
        version_idx = self.version_combo.currentIndex() + 1

        return filepath, version_idx
