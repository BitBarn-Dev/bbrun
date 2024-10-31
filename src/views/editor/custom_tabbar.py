from PySide2.QtWidgets import QTabBar, QInputDialog
from PySide2.QtCore import Qt

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)  # Enable tab reordering
        self.setTabsClosable(True)  # Enable close buttons
        self.setElideMode(Qt.ElideRight)  # Show ... when text is too long
        
    def mouseDoubleClickEvent(self, event):
        # Get the tab index at the mouse position
        index = self.tabAt(event.pos())
        if index >= 0:
            current_text = self.tabText(index)
            new_text, ok = QInputDialog.getText(
                self,
                "Rename Tab",
                "Enter new name:",
                text=current_text
            )
            if ok and new_text:
                self.setTabText(index, new_text)
                # Update the metadata in the tab widget
                if hasattr(self.parent(), 'widget'):
                    tab = self.parent().widget(index)
                    if hasattr(tab, 'metadata'):
                        tab.metadata['display_name'] = new_text
        super().mouseDoubleClickEvent(event)