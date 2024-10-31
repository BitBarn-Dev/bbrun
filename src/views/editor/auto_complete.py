from PySide2.QtWidgets import QPlainTextEdit
from PySide2.QtCore import Qt
from PySide2.QtGui import QTextCursor

class AutoCompleteEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setup_auto_completion()

    def setup_auto_completion(self):
        self.auto_pairs = {
            '"': '"',
            "'": "'",
            '(': ')',
            '[': ']',
            '{': '}',
        }
        self.auto_pairs_close = {v: k for k, v in self.auto_pairs.items()}
        
        self.indent_triggers = {':', 'class', 'def', 'for', 'if', 'elif',
                              'else:', 'try:', 'except:', 'finally:', 'while',
                              'with'}

    def keyPressEvent(self, event):
        if event.text() in self.auto_pairs:
            self.handle_auto_pair(event)
            return
        elif event.key() == Qt.Key_Backspace:
            if self.handle_backspace():
                return
        elif event.key() == Qt.Key_Return:
            if self.handle_return():
                return
        elif event.key() == Qt.Key_Tab:
            self.textCursor().insertText("    ")
            return

        super().keyPressEvent(event)
        
        if event.text() == ':':
            self.handle_post_colon_indent()

    def handle_auto_pair(self, event):
        cursor = self.textCursor()
        pair_char = self.auto_pairs[event.text()]
        
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            text = cursor.selectedText()
            cursor.beginEditBlock()
            cursor.setPosition(start)
            cursor.insertText(event.text())
            cursor.setPosition(end + 1)
            cursor.insertText(pair_char)
            cursor.endEditBlock()
            return
            
        cursor.insertText(event.text() + pair_char)
        cursor.movePosition(QTextCursor.Left)
        self.setTextCursor(cursor)

    def handle_backspace(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            return False
            
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Right)
        next_char = cursor.document().characterAt(cursor.position())
        cursor.movePosition(QTextCursor.Left)
        current_char = cursor.document().characterAt(cursor.position())
        
        if (current_char in self.auto_pairs and 
            next_char == self.auto_pairs[current_char]):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            return True
            
        return False

    def handle_return(self):
        cursor = self.textCursor()
        position = cursor.position()
        block = cursor.block()
        text = block.text()
        
        indentation = ""
        for char in text:
            if char in [' ', '\t']:
                indentation += char
            else:
                break
        
        increase_indent = False
        trimmed_text = text.strip()
        if trimmed_text.endswith(':'):
            increase_indent = True
        elif any(trimmed_text.startswith(word) for word in self.indent_triggers):
            increase_indent = True
        
        doc = cursor.document()
        current_char = doc.characterAt(position - 1)
        next_char = doc.characterAt(position)
        if current_char in '{[(' and next_char in '}])':
            cursor.insertText('\n' + indentation + '    \n' + indentation)
            cursor.movePosition(QTextCursor.Up)
            cursor.movePosition(QTextCursor.EndOfLine)
            self.setTextCursor(cursor)
            return True
        
        new_indent = indentation + '    ' if increase_indent else indentation
        cursor.insertText('\n' + new_indent)
        return True

    def handle_post_colon_indent(self):
        cursor = self.textCursor()
        block = cursor.block()
        text = block.text().strip()
        
        should_indent = False
        for trigger in self.indent_triggers:
            if text.startswith(trigger):
                should_indent = True
                break
