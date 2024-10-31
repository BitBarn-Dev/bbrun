from PySide2.QtCore import QRegularExpression
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Define formats for different syntax elements
        formats = {
            'keyword': self.create_format("#569CD6", bold=True),
            'builtin': self.create_format("#4EC9B0"),
            'operator': self.create_format("#D4D4D4"),
            'brace': self.create_format("#D4D4D4"),
            'defclass': self.create_format("#4EC9B0", bold=True),
            'string': self.create_format("#CE9178"),
            'string2': self.create_format("#CE9178"),
            'comment': self.create_format("#6A9955", italic=True),
            'self': self.create_format("#569CD6", italic=True),
            'numbers': self.create_format("#B5CEA8"),
            'decorators': self.create_format("#DCDCAA"),
        }

        # Keyword patterns
        keywords = [
            'and', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'exec', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in',
            'is', 'lambda', 'not', 'or', 'pass', 'print',
            'raise', 'return', 'try', 'while', 'yield',
            'None', 'True', 'False'
        ]

        # Add rule for keywords
        self.add_rules((r'\b%s\b' % keyword for keyword in keywords), formats['keyword'])

        # Operators
        self.add_rule(r'[~!@#$%^&*()_+{}|:"<>?,./;\'\\-=]', formats['operator'])

        # Numbers
        self.add_rule(r'\b[+-]?[0-9]+[lL]?\b', formats['numbers'])
        self.add_rule(r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', formats['numbers'])
        self.add_rule(r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', formats['numbers'])

        # String handling
        self.add_rule(r'"[^"\\]*(\\.[^"\\]*)*"', formats['string'])
        self.add_rule(r"'[^'\\]*(\\.[^'\\]*)*'", formats['string'])
        self.add_rule(r'"[^"\\]*(\\.[^"\\]*)*"', formats['string2'])
        self.add_rule(r"'[^'\\]*(\\.[^'\\]*)*'", formats['string2'])

        # Comments
        self.add_rule(r'#[^\n]*', formats['comment'])

        # Self parameter
        self.add_rule(r'\bself\b', formats['self'])

        # Decorators
        self.add_rule(r'@\w+', formats['decorators'])

        # Class and function definitions
        self.add_rule(r'\bclass\b\s*(\w+)', formats['defclass'])
        self.add_rule(r'\bdef\b\s*(\w+)', formats['defclass'])

        # Braces, brackets, and parentheses
        self.add_rule(r'[\{\}\[\]\(\)]', formats['brace'])

        # Multi-line strings
        self.multiline_string_format = formats['string']
        self.triple_single = QRegularExpression("'''")
        self.triple_double = QRegularExpression('"""')

    def create_format(self, color, bold=False, italic=False):
        """Create a QTextCharFormat with the given attributes."""
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        if bold:
            text_format.setFontWeight(QFont.Bold)
        if italic:
            text_format.setFontItalic(True)
        return text_format

    def add_rule(self, pattern, format):
        """Add a rule with the given pattern and format."""
        # Ensure the pattern starts with a raw string
        if not pattern.startswith('r"') and not pattern.startswith("r'"):
            pattern = 'r"' + pattern.replace('"', '\\"') + '"'
        try:
            expr = QRegularExpression(eval(pattern))
            self.highlighting_rules.append((expr, format))
        except Exception as e:
            print(f"Error adding syntax rule for pattern {pattern}: {e}")

    def add_rules(self, patterns, format):
        """Add multiple rules with the same format."""
        for pattern in patterns:
            self.add_rule(pattern, format)

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        # Do multi-line strings first
        self.highlight_multiline_strings(text)

        # Do all other syntax highlighting
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

    def highlight_multiline_strings(self, text):
        """Handle multi-line string highlighting."""
        start_index = 0
        if self.previousBlockState() == 1:
            match = self.triple_single.match(text, start_index)
            if match is None:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_string_format)
                return
            start_index = match.capturedEnd()
            self.setFormat(0, start_index, self.multiline_string_format)
        else:
            match = self.triple_single.match(text)
            if match is not None:
                start_index = match.capturedEnd()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.multiline_string_format)

        while start_index >= 0:
            match = self.triple_single.match(text, start_index)
            if match is None:
                self.setCurrentBlockState(1)
                self.setFormat(start_index, len(text) - start_index, self.multiline_string_format)
                break
            self.setFormat(start_index, match.capturedEnd() - start_index, self.multiline_string_format)
            start_index = match.capturedEnd()

        # Handle triple double quotes the same way
        start_index = 0
        if self.previousBlockState() == 2:
            match = self.triple_double.match(text, start_index)
            if match is None:
                self.setCurrentBlockState(2)
                self.setFormat(0, len(text), self.multiline_string_format)
                return
            start_index = match.capturedEnd()
            self.setFormat(0, start_index, self.multiline_string_format)
        else:
            match = self.triple_double.match(text)
            if match is not None:
                start_index = match.capturedEnd()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.multiline_string_format)

        while start_index >= 0:
            match = self.triple_double.match(text, start_index)
            if match is None:
                self.setCurrentBlockState(2)
                self.setFormat(start_index, len(text) - start_index, self.multiline_string_format)
                break
            self.setFormat(start_index, match.capturedEnd() - start_index, self.multiline_string_format)
            start_index = match.capturedEnd()