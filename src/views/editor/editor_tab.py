import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from .code_editor import CodeEditor
from .output_window import OutputWindow

class CodeEditorTab(QWidget):
    def __init__(self, filepath=None, metadata=None, initial_content=''):
        super().__init__()
        self.filepath = filepath
        self.metadata = metadata if metadata is not None else {}
        self.display_name = self.metadata.get('display_name', 'Untitled')
        self.initial_content = initial_content
        self.last_saved_content = initial_content
        self.setup_ui()
        self.load_content()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #333333;
                height: 1px;
            }
            QSplitter {
                border: none;
            }
        """)

        self.editor = CodeEditor()
        self.output_window = OutputWindow()

        splitter.addWidget(self.editor)
        splitter.addWidget(self.output_window)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

    def load_content(self):
        if self.filepath and os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    content = data.get('content', '')
                    self.editor.setPlainText(content)
                    self.metadata = data.get('metadata', self.metadata)
                    self.display_name = self.metadata.get('display_name', 'Untitled')
                    self.last_saved_content = content
            except Exception as e:
                self.output_window.append(f"Error loading file: {str(e)}")
        else:
            self.editor.setPlainText(self.initial_content)
            self.last_saved_content = self.initial_content

    def save_content(self):
        """Save the content and update the last saved state"""
        if not self.filepath:
            return False

        try:
            data = {
                'content': self.editor.toPlainText(),
                'metadata': self.metadata
            }

            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2)

            self.last_saved_content = self.editor.toPlainText()
            return True
        except Exception as e:
            self.output_window.append(f"Error saving file: {str(e)}")
            return False

    def get_unsaved_changes(self):
        """Check if there are unsaved changes in the editor"""
        current_content = self.editor.toPlainText()
        result = current_content != self.last_saved_content

        print(f"Debug - Checking unsaved changes:")  # Debug logging
        print(f"  Has filepath: {bool(self.filepath)}")
        print(f"  Current content length: {len(current_content)}")
        print(f"  Last saved content length: {len(self.last_saved_content)}")
        print(f"  Content matches: {not result}")

        return result

    def get_content(self):
        """Get the current content of the editor"""
        return self.editor.toPlainText()

    def set_content(self, content):
        """Set the content of the editor"""
        self.editor.setPlainText(content)

    def clear_output(self):
        """Clear the output window"""
        self.output_window.clear()

    def append_output(self, text):
        """Append text to the output window"""
        self.output_window.append(text)

    def set_filepath(self, filepath):
        """Set the filepath and update display name"""
        self.filepath = filepath
        if filepath:
            self.display_name = os.path.basename(filepath)
        else:
            self.display_name = 'Untitled'

    def update_metadata(self, metadata):
        """Update metadata and display name"""
        self.metadata.update(metadata)
        self.display_name = self.metadata.get('display_name', 'Untitled')

    def handle_save(self):
        """Handle save operation"""
        if not self.filepath:
            return False
        return self.save_content()

    def get_cursor_position(self):
        """Get the current cursor position"""
        cursor = self.editor.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber() + 1

    def goto_line(self, line_number):
        """Move cursor to specified line number"""
        if line_number < 1:
            return

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number - 1)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()

    def insert_text(self, text):
        """Insert text at current cursor position"""
        self.editor.insertPlainText(text)

    def get_selected_text(self):
        """Get currently selected text"""
        return self.editor.textCursor().selectedText()

    def set_focus(self):
        """Set focus to the editor"""
        self.editor.setFocus()

    def refresh_highlights(self):
        """Refresh syntax highlighting"""
        self.editor.highlighter.rehighlight()
