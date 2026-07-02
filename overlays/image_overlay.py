"""
Module handling memory-safe, responsive image layout slideshow presentation layers.
"""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QResizeEvent

if TYPE_CHECKING:
    from asset_service import AssetService

class ImageOverlay(QWidget):
    """
    Memory-safe presentation container handling dynamic campaign image rotation.

    Automatically shifts asset pipelines between landscape (_h) and portrait (_v) orientations
    based on bounding box changes. Implements a debounced timer mechanism to prevent disk-read
    thrashing during active layout transformations.

    Attributes:
        asset_service (AssetService): Injected core filesystem mapping framework.
        layout (QVBoxLayout): Global layout manager centering display elements.
        image_label (QLabel): Graphical container presenting calculated pixmap surfaces.
        pixmap (QPixmap | None): Loaded unscaled graphic asset held in system memory.
        current_idx (int): Absolute structural index identifier mapping the current layout queue track.
        check_timer (QTimer): Single-shot debounce timer isolating file reads from window resizing loops.
        playlist_timer (QTimer): Rotation loop handling timed slideshow transitions.
    """
    def __init__(self, asset_service: "AssetService") -> None:
        """Initializes layouts, structures visual wrappers, and starts rotation clocks."""
        super().__init__()
        self.asset_service = asset_service

        # Setup Vertical Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Visual Components to Hold Pixels on Screen
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Memory Structures
        self.pixmap: QPixmap | None = None
        self.current_idx: int = 0

        # Pre-check initial playlist status safely
        startup_playlist = self.asset_service.get_image_playlist("horizontal")
        if startup_playlist:
            self.current_idx = 0

        # Prevents Heavy Re-reading During an Active Window Resize Drag
        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.load_best_image)

        # Rotation Timer
        self.playlist_timer = QTimer(self)
        self.playlist_timer.timeout.connect(self.advance_playlist)
        self.playlist_timer.start(5000)

        # Trigger the initial asset to load
        self.load_best_image()

    def apply_settings(self, parent_window: QWidget) -> None:
        """Strips structural canvas styles from core background layouts."""
        parent_window.setStyleSheet("background: transparent;")
        self.layout.setContentsMargins(0, 0, 0, 0)

    def load_best_image(self) -> None:
        """Evaluates bounding frames to extract, cache, and draw the matching campaign image."""
        is_landscape = self.width() >= self.height()
        orientation = "horizontal" if is_landscape else "vertical"

        current_playlist = self.asset_service.get_image_playlist(orientation)

        if not current_playlist:
            return

        safe_idx = self.current_idx % len(current_playlist)
        chosen_path = current_playlist[safe_idx]
        
        self.pixmap = QPixmap(chosen_path)
        self.update_display()

    def advance_playlist(self) -> None:
        """Increments index identifiers to process the next asset step across available playlists."""
        is_landscape = self.width() >= self.height()
        orientation = "horizontal" if is_landscape else "vertical"

        current_playlist = self.asset_service.get_image_playlist(orientation)

        if not current_playlist:
            return
        
        self.current_idx = (self.current_idx + 1) % len(current_playlist)
        self.load_best_image()

    def update_display(self) -> None:
        """Scales the master cached pixmap onto the view canvas while retaining exact aspect ratios."""
        if self.pixmap:
            scaled_pixels = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixels)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Intercepts window resize cycles to feed the single-shot debounce timer."""
        self.check_timer.start(100)

