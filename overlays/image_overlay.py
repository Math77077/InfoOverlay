import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

class ImageOverlay(QWidget):
    """
    Manages loading and displaying images dynamically.
    Detects window orientation and swaps between horizontal (_h) and vertical (_v) files.
    """
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

        # SETUP VERTICAL LAYOUT
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # VISUAL COMPONENTS TO HOLD PIXELS ON SCREEN
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # MEMORY SLOT TO STORE IMAGE PIXELS
        self.pixmap = None

        # PREVENTS HEAVY RE-READING DURING AN ACTIVE WINDOW RESIZE DRAG
        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.load_best_image)

        # TRIGGER THE INITIAL ASSET TO LOAD
        self.load_best_image()

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("background: transparent;")
        self.layout.setContentsMargins(0, 0, 16, 16)

    def load_best_image(self):
        if not os.path.exists(self.folder_path):
            return
        
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            return

        is_landscape = self.width() >= self.height()

        chosen_path = os.path.join(self.folder_path, files[0])

        for file_name in files:
            if is_landscape and "_h" in file_name.lower():
                chosen_path = os.path.join(self.folder_path, file_name)
                break
            if not is_landscape and "_v" in file_name.lower():
                chosen_path = os.path.join(self.folder_path, file_name)
                break

        self.pixmap = QPixmap(chosen_path)
        self.update_display()

    def update_display(self):
        if self.pixmap:
            scaled_pixels = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixels)

    def resizeEvent(self, event):
        self.check_timer.start(100)

