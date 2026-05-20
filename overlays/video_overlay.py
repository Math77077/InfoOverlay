import os
import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QFrame
from PySide6.QtCore import Qt, QTimer, QUrl, QSizeF
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem

class VideoOverlay(QWidget):
    """
    Manages a hardware-accelerated video player.
    Uses QGraphicsView to maintain alpha transparency channels on Linux desktop environments.
    """
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.current_video = ""

        # BASE LAYOUT SETUP
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # GRAPHICS PIPELINE
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        # IGNORE MOUSE INTERACTIONS AS SO IT REACHES THE BASEWINDOW
        self.view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.view.setFrameShape(QFrame.Shape.NoFrame)
        self.view.setStyleSheet("background: transparent;")
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # GRAPHICAL SURFACE ITEM THAT ACCEPTS RAW VIDEO FRAMES
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        self.layout.addWidget(self.view)

        # MEDIA CORE ENGINE
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)

        # MEMORY STRUCTURES
        self.landscape_playlist = []
        self.portrait_playlist = []
        self.current_idx = 0
        self.current_video = ""

        # CACHE FILE PATHS
        self.scan_resources()

        # RANDOM STARTING POINT
        total_items = max(len(self.landscape_playlist), len(self.portrait_playlist))
        if total_items > 0:
            self.current_idx = random.randint(0, total_items - 1)
        else:
            self.current_idx = 0

        # CONECTION BETWEEN ENGINE AND VIDEO/AUDIO OUTPUT
        self.media_player.setVideoOutput(self.video_item)
        self.media_player.setAudioOutput(self.audio_output)

        # WATCH THE VIDEO STATE, SO WHEN IT ENDS THE LOOP STARTS AGAIN
        self.media_player.playbackStateChanged.connect(self.handle_loop)

        # RESIZE MANAGEMENT
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.load_best_video)

        # QUEUE UP THE INITIAL FILE SELECTION
        QTimer.singleShot(200, self.load_best_video)

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("background: transparent; border: none;")
        parent_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def stop_media(self):
        self.media_player.stop()
        self.media_player.setSource(QUrl(""))

    def scan_resources(self):
        if not os.path.exists(self.folder_path):
            return
        
        self.landscape_playlist = [
            os.path.abspath(os.path.join(self.folder_path, f))
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(('.mp4', '.mov')) and '_h' in f.lower()
        ]

        self.portrait_playlist = [
            os.path.abspath(os.path.join(self.folder_path, f))
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(('.mp4', '.mov')) and '_v' in f.lower()
        ]

        random.shuffle(self.landscape_playlist)
        random.shuffle(self.portrait_playlist)

    def load_best_video(self):
        is_landscape = self.width() >= self.height()
        current_playlist = self.landscape_playlist if is_landscape else self.portrait_playlist

        if not current_playlist:
            return

        safe_idx = self.current_idx % len(current_playlist)
        target_video = current_playlist[safe_idx]

        if target_video != self.current_video:
            self.current_video = target_video
            self.media_player.setSource(QUrl.fromLocalFile(target_video))
            self.media_player.play()

        self.update_video_size()

    def update_video_size(self):
        current_size = self.size()
        self.video_item.setSize(QSizeF(current_size.width(), current_size.height()))
        self.view.setSceneRect(0, 0, current_size.width(), current_size.height())

    def handle_loop(self, current_state):
        if current_state == QMediaPlayer.PlaybackState.StoppedState and self.current_video != "":
            is_landscape = self.width() >= self.height()
            current_playlist = self.landscape_playlist if is_landscape else self.portrait_playlist

            if not current_playlist:
                return
            
            self.current_idx = (self.current_idx + 1) % len(current_playlist)

            self.load_best_video()

    def resizeEvent(self, event):
        self.update_video_size()
        self.resize_timer.start(300)
        super().resizeEvent(event)

