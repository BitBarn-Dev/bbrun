from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QPainter, QColor

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.line_number_area_paint_event(event)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))

        block = self.code_editor.firstVisibleBlock()  # Assuming this method is defined in your code editor
        block_number = block.blockNumber()
        offset = self.code_editor.contentOffset()
        top = int(self.code_editor.blockBoundingGeometry(block).translated(offset).top())  # Convert to int
        bottom = top + int(self.code_editor.blockBoundingRect(block).height())  # Convert to int

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))

                # Use QPoint for the position with integer coordinates
                painter.drawText(QPoint(0, top), number)

            block = block.next()
            top = bottom
            bottom = top + int(self.code_editor.blockBoundingRect(block).height())  # Convert to int
            block_number += 1
