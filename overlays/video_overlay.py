import os
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
        self.view.setVerticalScrollBarPolicy(Qt.ScroolBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBar(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # GRAPHICAL SURFACE ITEM THAT ACCEPTS RAW VIDEO FRAMES
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        self.layout.addWidget(self.view)

        # MEDIA CORE ENGINE
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)

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

    def load_best_video(self):
        if not os.path.exists(self.folder_path):
            return
        
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.mp4', '.mov'))]
        if not files: 
            return
        
        is_landscape = self.width() >= self.height()
        target_file = files[0]

        for file_name in files:
            if is_landscape and "_h" in file_name.lower(): 
                target_file = file_name
                break
            if not is_landscape and "_v" in file_name.lower(): 
                target_file = file_name
                break

        absolute_path = os.path.abspath(os.path.join(self.folder_path, target_file))

        if absolute_path != self.current_video:
            self.current_video = absolute_path
            self.media_player.setSource(QUrl.fromLocalFile(absolute_path))
            self.media_player.play()

        self.update_video_size()

    def update_video_size(self):
        current_size = self.size()
        self.video_item.setSize(QSizeF(current_size.width(), current_size.height()))
        self.view.setSceneRect(0, 0, current_size.width(), current_size.height())

    def handle_loop(self, current_state):
        if current_state == QMediaPlayer.PlaybackState.StoppedState and self.current_video != "":
            self.media_player.play()

    def resizeEvent(self, event):
        self.update_video_size()
        self.resize_timer.start(300)
        super().resizeEvent(event)
        
