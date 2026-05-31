import os
import random
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

        # MEMORY STRUCTURES
        self.pixmap = None
        self.landscape_playlist = []
        self.portrait_playlist = []
        self.current_idx = 0

        # CACHE FILE PATHS
        self.scan_resources()

        # RANDOM STARTING POINT
        total_items = max(len(self.landscape_playlist), len(self.portrait_playlist))
        if total_items > 0:
            self.current_idx = random.randint(0, total_items - 1)
        else:
            self.current_idx = 0

        # PREVENTS HEAVY RE-READING DURING AN ACTIVE WINDOW RESIZE DRAG
        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.load_best_image)

        # ROTATION TIMER
        self.playlist_timer = QTimer(self)
        self.playlist_timer.timeout.connect(self.advance_playlist)
        self.playlist_timer.start(5000)

        # TRIGGER THE INITIAL ASSET TO LOAD
        self.load_best_image()

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("background: transparent;")
        self.layout.setContentsMargins(0, 0, 0, 0)

    def scan_resources(self):
        if not os.path.exists(self.folder_path):
            return
        
        self.landscape_playlist = [
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "_h" in f.lower()
        ]

        self.portrait_playlist = [
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and "_v" in f.lower()
        ]

        random.shuffle(self.landscape_playlist)
        random.shuffle(self.portrait_playlist)

    def load_best_image(self):
        is_landscape = self.width() >= self.height()
        current_playlist = self.landscape_playlist if is_landscape else self.portrait_playlist

        if not current_playlist:
            return
        
        safe_idx = self.current_idx % len(current_playlist)
        chosen_path = current_playlist[safe_idx]
        
        self.pixmap = QPixmap(chosen_path)
        self.update_display()

    def advance_playlist(self):
        is_landscape = self.width() >= self.height()
        current_playlist = self.landscape_playlist if is_landscape else self.portrait_playlist

        if not current_playlist:
            return
        
        self.current_idx = (self.current_idx + 1) % len(current_playlist)
        self.load_best_image()

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

