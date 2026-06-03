from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout,  QGraphicsScene, QGraphicsView, QFrame, QPushButton, QSlider
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
        self.view.setStyleSheet("background: transparent; background-color: transparent;")
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
        self.audio_output.setVolume(0.5)

        # AUDIO CONTROL - CONTAINER FOR BUTTON + SLIDER
        self.control_panel = QWidget(self)
        self.control_panel.setObjectName("control_panel")
        self.panel_layout = QHBoxLayout(self.control_panel)
        self.panel_layout.setContentsMargins(6, 4, 10, 4)
        self.panel_layout.setSpacing(8)

        # VISUAL AUDIO TOGGLE BUTTON
        self.audio_btn = QPushButton(self.control_panel)
        self.audio_btn.setCheckable(True)
        self.audio_btn.setFixedSize(32, 32)
        self.audio_btn.clicked.connect(self.toggle_audio_state)
        self.panel_layout.addWidget(self.audio_btn)

        # VOLUME SLIDER
        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self.control_panel)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self.handle_volume_change)
        self.panel_layout.addWidget(self.volume_slider)

        # INITIAL PANEL STYLING AND STATE
        self.update_button_style()
        self.control_panel.hide()

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
        parent_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        parent_window.setStyleSheet("BaseWindow { background-color: rgba(0, 0, 0, 1); border: none; }")

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

        self.control_panel.adjustSize()
        panel_w = self.control_panel.width()
        panel_h = self.control_panel.height()

        center_x = (current_size.width() - panel_w) // 2
        center_y = (current_size.height() - panel_h) // 2

        self.control_panel.move(center_x, center_y)
        self.control_panel.raise_()

    def enterEvent(self, event):
        self.control_panel.show()
        self.control_panel.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.control_panel.hide()
        super().leaveEvent(event)

    def toggle_audio_state(self, checked):
        if checked:
            self.claim_audio_focus()
        else:
            self.audio_output.setMuted(True)
            self.update_button_style()

    def handle_volume_change(self, value):
        float_volume = value / 100.0
        self.audio_output.setVolume(float_volume)

        if float_volume > 0.0 and self.audio_output.isMuted():
            self.audio_btn.setChecked(True)
            self.claim_audio_focus()
        elif float_volume == 0.0:
            self.audio_btn.setChecked(False)
            self.audio_output.setMuted(True)
            self.update_button_style()

    def claim_audio_focus(self):
        for overlay in VideoOverlay._instances:
            if overlay != self:
                overlay.audio_output.setMuted(True)
                overlay.audio_btn.setChecked(False)
                overlay.update_button_style()

        self.audio_output.setMuted(False)
        self.audio_output.setVolume(self.volume_slider.value() / 100.0)
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
        self.audio_btn.setIconSize(QSize(24, 24))

        self.control_panel.setStyleSheet(f"""
            QWidget#control_panel {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QPushButton {{
                border: none;
                background-color: transparent;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: rgba(69, 156, 214, 0.4);
                border-radius: 4px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid rgba(255, 255, 255, 50);
                height: 4px;
                background: rgba(255, 255, 255, 20);
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: #459cd6;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #ffffff;
                border: 1px solid #056e9b;
                width: 12px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 6px;
            }}
        """)

    def handle_loop(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.current_video != "":
            if not self.local_playlist:
                return
            
            if len(self.local_playlist) == 1:
                self.media_player.setPosition(0)
                self.media_player.play()
            else:
                self.current_idx = (self.current_idx + 1) % len(self.local_playlist)
                QTimer.singleShot(100, self.load_best_video)

    def resizeEvent(self, event):
        self.update_video_size()
        self.resize_timer.start(300)
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.stop_media()
        super().closeEvent(event)

