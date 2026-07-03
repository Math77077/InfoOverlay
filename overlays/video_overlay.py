"""
Module implementing hardware-accelerated video playlist loops with singleton audio tracking.
"""

from typing import TYPE_CHECKING, ClassVar
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout,  QGraphicsScene, QGraphicsView, QFrame, QPushButton, QSlider
from PySide6.QtCore import Qt, QTimer, QUrl, QSizeF, QSize, QEvent
from PySide6.QtGui import QIcon, QResizeEvent, QCloseEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem

if TYPE_CHECKING:
    from asset_service import AssetService

class VideoOverlay(QWidget):
    """
    Hardware-accelerated rendering container managing localized video rotation loops.

    Leverages an optimized QGraphicsView pipeline to guarantee cross-platform alpha channel
    transparency blending. Manages a static tracking registry to orchestrate mutual audio
    exclusion states across multi-monitor clinic layouts.

    Attributes:
        _instances (list[VideoOverlay]): Class-level registry tracking active players.
        asset_service (AssetService): Injected core filesystem mapping framework.
        current_video (str): Path to the absolute filesystem route currently loaded.
        layout (QVBoxLayout): Main vertical engine positioning graphic structures.
        scene (QGraphicsScene): Core vector graphic manager holding video elements.
        view (QGraphicsView): Transparent viewport displaying hardware frames.
        video_item (QGraphicsVideoItem): Surface layer accepting raw hardware frames.
        media_player (QMediaPlayer): Core multimedia playback decoding engine.
        audio_output (QAudioOutput): Audio stream routing engine.
        control_panel (QWidget): Interactive floating control hub container.
        panel_layout (QHBoxLayout): Horizontal item alignment mapping control widgets.
        audio_btn (QPushButton): Graphical toggle button manipulating volume states.
        volume_slider (QSlider): Horizon input selector handling volume percentages.
        current_idx (int): Structural index mapping the running playlist position.
        local_playlist (list[str]): Current absolute media paths allocated to RAM.
        current_orientation (str): Layout descriptor string ("horizontal" or "vertical").
        resize_timer (QTimer): Single-shot debounce timer cooling down aspect recalculations.
    """

    # Track all active instances globally to ensure single-source audio focus
    _instances: ClassVar[list["VideoOverlay"]] = []

    def __init__(self, asset_service: "AssetService") -> None:
        """Initializes acceleration graphs, audio pipelines, and interaction trackers."""
        super().__init__()
        self.asset_service = asset_service
        self.current_video: str = ""
        VideoOverlay._instances.append(self)

        # Base Layout Setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Graphics Pipeline
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        # Allow Mouse Interaction Only for Overlapping Buttons
        self.view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.view.setFrameShape(QFrame.Shape.NoFrame)
        self.view.setStyleSheet("background: transparent;")
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Graphical Surface Item That Accepts Raw Video Frames
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        self.layout.addWidget(self.view)

        # Media Core Engine
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)

        # Exclusive Audio Focus Defaults (Start Muted)
        self.audio_output.setMuted(True)
        self.audio_output.setVolume(0.5)

        # Audio Control - Container For Button + Slider
        self.control_panel = QWidget(self)
        self.control_panel.setObjectName("control_panel")
        self.panel_layout = QHBoxLayout(self.control_panel)
        self.panel_layout.setContentsMargins(6, 4, 10, 4)
        self.panel_layout.setSpacing(8)

        # Visual Audio Toggle Button
        self.audio_btn = QPushButton(self.control_panel)
        self.audio_btn.setCheckable(True)
        self.audio_btn.setFixedSize(32, 32)
        self.audio_btn.clicked.connect(self.toggle_audio_state)
        self.panel_layout.addWidget(self.audio_btn)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self.control_panel)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self.handle_volume_change)
        self.panel_layout.addWidget(self.volume_slider)

        # Initial Styling Layout Application
        self.update_button_style()
        self.control_panel.hide()

        # Runtime States
        self.current_idx: int = 0
        self.local_playlist: list[str] = []
        self.current_orientation: str = ""

        # Connection Between Engine and Video/Audio Output
        self.media_player.setVideoOutput(self.video_item)
        self.media_player.setAudioOutput(self.audio_output)

        # Watch the Video State to Handle Continous Looping
        self.media_player.mediaStatusChanged.connect(self.handle_loop)

        # Resize Management
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.load_best_video)

        # Queue Up the Initial File Selection Asynchronously After App Attaches
        QTimer.singleShot(200, self.load_best_video)

    def apply_settings(self, parent_window: QWidget) -> None:
        """Strips out border wrappers and enforces structural backdrop transparency."""
        parent_window.setStyleSheet("background: transparent; border: none;")
        parent_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def stop_media(self) -> None:
        """Safely tears down background hardware hooks and unregisters the active tracking instance."""
        self.media_player.stop()
        self.media_player.setSource(QUrl(""))
        if self in VideoOverlay._instances:
            VideoOverlay._instances.remove(self)

    def load_best_video(self) -> None:
        """Analyzes canvas aspect ratios to fetch, parse, and spin up matching video assets."""
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

    def update_video_size(self) -> None:
        """Re-scales hardware drawing canvas items and realigns floating controls centrally."""
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

    def enterEvent(self, event: QEvent) -> None:
        """Surfaces interactive floating configuration layers when cursor entries hit windows."""
        self.control_panel.show()
        self.control_panel.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Conceals overlay panels when mouse pointers transition out of boundaries."""
        self.control_panel.hide()
        super().leaveEvent(event)

    def toggle_audio_state(self, checked: bool) -> None:
        """
        Routes hardware audio toggles based on interactive checkbox states.

        Args:
            checked: Current selection state assigned to the button interaction.
        """
        if checked:
            self.claim_audio_focus()
        else:
            self.audio_output.setMuted(True)
            self.update_button_style()

    def handle_volume_change(self, value: int) -> None:
        """
        Normalizes slider integer positions to decimal floating gain percentages.

        Args:
            value: Integer value mapped straight from slider components.
        """
        float_volume = value / 100.0
        self.audio_output.setVolume(float_volume)

        if float_volume > 0.0 and self.audio_output.isMuted():
            self.audio_btn.setChecked(True)
            self.claim_audio_focus()
        elif float_volume == 0.0:
            self.audio_btn.setChecked(False)
            self.audio_output.setMuted(True)
            self.update_button_style()

    def claim_audio_focus(self) -> None:
        """Iterates down tracking instances to isolate sound feeds to this component."""
        for overlay in VideoOverlay._instances:
            if overlay != self:
                overlay.audio_output.setMuted(True)
                overlay.audio_btn.setChecked(False)
                overlay.update_button_style()

        self.audio_output.setMuted(False)
        self.audio_output.setVolume(self.volume_slider.value() / 100.0)
        self.update_button_style()

    def update_button_style(self) -> None:
        """Re-evaluates player states to load corresponding UI vectors and CSS themes."""
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

    def handle_loop(self, status: QMediaPlayer.MediaStatus) -> None:
        """
        Intercepts end-of-file broadcast status flags to cycle playheads smoothly.

        Implements a deliberate 100ms async single-shot timer delay to flush
        hardware decoding thread allocations and protect low-spec CPUs from lock spikes.

        Args:
            status: Hardware code dispatched straight from native pipelines.
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.current_video != "":
            if not self.local_playlist:
                return
            
            self.current_idx = (self.current_idx + 1) % len(self.local_playlist)
            QTimer.singleShot(100, self.load_best_video)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Pushes current dimensional mutations to buffers to scale video pipelines smoothly."""
        self.update_video_size()
        self.resize_timer.start(300)
        super().resizeEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Intercepts system termination events to ensure media processes are safely dropped."""
        self.stop_media()
        super().closeEvent(event)

