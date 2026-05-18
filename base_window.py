import os
from PySide6.QtWidgets import QWidget, QSizeGrip, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, QSize

class BaseWindow(QWidget):
    """
    Window lifecycle, frameless movement, resizing grip, and the right-click global context menu frame.
    """
    def __init__(self):
        super().__init__()
        self.child_windows = []
        self.drag_anchor = None

        # WINDOW STYLING TRAITS
        
        ## Windows settings to stay on top and without its title bar
        self.setWindowFlags( 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        ## Transparent Background and Window's Geometry
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(1000, 300)
        self.setMinimumSize(50, 50)

        # BASE LAYOUT
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # RESIZING ELEMENT SETUP (GRIP)
        self.grip_size = 16
        self.grip = QSizeGrip(self)
        self.grip.resize(self.grip_size, self.grip_size)
        self.grip.setStyleSheet("background-color: rgba(255, 255, 255, 30); border-radius: 8px;")

        # INIT CONTEXT MENU PLACEHOLDER
        self.context_menu = QMenu(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_anchor = event.position().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_anchor:
            new_pos = event.globalPosition().toPoint() - self.drag_anchor
            self.move(new_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        self.grip.move(rect.width() - self.grip_size, rect.height() - self.grip_size)

    def closeEvent(self, event):
        for window in self.child_windows:
            window.close()
        event.accept()

