from PySide6.QtWidgets import QWidget, QVBoxLayout, QStyleOption
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

class PreviewOverlay(QWidget):
    """
    Acts as a visual placeholder.
    Renders a semi-transparent, stylish geometric guide box so the user can reposition/resize the window cleanly.
    """
    def __init__(self):
        super().__init__()

        # LAYOUT SETUP
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("""
            PreviewOverlay {
                background-color: rgba(44, 62, 80, 0.85); 
                border: 2px dashed #3498db;             
                border-radius: 6px;
            }
        """)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)