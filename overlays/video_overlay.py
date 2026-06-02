from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QFrame, QPushButton, QApplication
from PySide6.QtCore import Qt, QTimer, QUrl, QSizeF, QSize
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem

class VideoOverlay(QWidget):
    """
    Manages a hardware-accelerated video player.
    Uses QGraphicsView to maintain alpha transparency channels on Linux desktop environments.
    """
    # TRACKER REGISTRY FOR ALL ACTIVE VIDEO WIDGETS ACROSS ALL WINDOWS
    _instances = []

    def __init__(self, asset_service):
        super().__init__()
        self.asset_service = asset_service
        self.current_video = ""
        VideoOverlay._instances.append(self)

        # BASE LAYOUT SETUP
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # GRAPHICS PIPELINE
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        # ALLOW MOUSE INTERACTION ONLY FOR FLOATING BUTTON INTERACTION
        self.view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
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

        # EXCLUSIVE FOCUS
        self.audio_output.setMuted(True)

        # VISUAL AUDIO TOGGLE BUTTON
        self.audio_btn = QPushButton(self)
        self.audio_btn.setCheckable(True)
        self.audio_btn.resize(32, 32)
        self.update_button_style()
        self.audio_btn.clicked.connect(self.toggle_audio_state)
        self.audio_btn.hide()

        # RUNTIME STATES
        self.current_idx = 0
        self.local_playlist = []
        self.current_orientation = ""

        # CONECTION BETWEEN ENGINE AND VIDEO/AUDIO OUTPUT
        self.media_player.setVideoOutput(self.video_item)
        self.media_player.setAudioOutput(self.audio_output)

        # WATCH THE VIDEO STATE, SO WHEN IT ENDS THE LOOP STARTS AGAIN
        self.media_player.mediaStatusChanged.connect(self.handle_loop)

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
        if self in VideoOverlay._instances:
            VideoOverlay._instances.remove(self)

    def load_best_video(self):
        is_landscape = self.width() >= self.height()
        orientation = "horizontal" if is_landscape else "vertical"

        if orientation != self.current_orientation or not self.local_playlist:
            self.current_orientation = orientation
            self.local_playlist = self.asset_service.get_video_playlist(orientation)
            self.current_idx = 0

        if not self.local_playlist:
            return

        safe_idx = self.current_idx % len(self.local_playlist)
        target_video = self.local_playlist[safe_idx]

        if target_video != self.current_video:
            self.current_video = target_video
            self.media_player.setSource(QUrl.fromLocalFile(target_video))
            self.media_player.play()

        self.update_video_size()

    def update_video_size(self):
        current_size = self.size()
        self.video_item.setSize(QSizeF(current_size.width(), current_size.height()))
        self.view.setSceneRect(0, 0, current_size.width(), current_size.height())

        btn_w = self.audio_btn.width()
        btn_h = self.audio_btn.height()
        center_x = (current_size.width() - btn_w) // 2
        center_y = (current_size.height() - btn_h) // 2

        self.audio_btn.move(center_x, center_y)
        self.audio_btn.raise_()

    def enterEvent(self, event):
        self.audio_btn.show()
        self.audio_btn.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.audio_btn.hide()
        super().leaveEvent(event)

    def toggle_audio_state(self, checked):
        if checked:
            self.claim_audio_focus()
        else:
            self.audio_output.setMuted(True)
            self.update_button_style()

    def claim_audio_focus(self):
        for overlay in VideoOverlay._instances:
            if overlay != self:
                overlay.audio_output.setMuted(True)
                overlay.audio_btn.setChecked(False)
                overlay.update_button_style()

        self.audio_output.setMuted(False)
        self.update_button_style()

    def update_button_style(self):
        if self.audio_btn.isChecked():
            icon_path = self.asset_service.get_asset_path("volume_on.svg")
            bg_color = "rgba(5, 110, 155, 0.85)"
            border_color = "#056e9b"
        else:
            icon_path = self.asset_service.get_asset_path("volume_muted.svg")
            bg_color = "rgba(31, 40, 51, 0.6)"
            border_color = "rgba(255, 255, 255, 30)"

        self.audio_btn.setIcon(QIcon(icon_path))
        self.audio_btn.setIconSize(QSize(32, 32))
        self.audio_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(69, 156, 214, 0.9);
                border: 1px solid #459cd6;
            }}
        """)

    def handle_loop(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.current_video != "":
            if not self.local_playlist:
                return
            
            self.current_idx = (self.current_idx + 1) % len(self.local_playlist)
            QTimer.singleShot(100, self.load_best_video)

    def resizeEvent(self, event):
        self.update_video_size()
        self.resize_timer.start(300)
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.stop_media()
        super().closeEvent(event)

