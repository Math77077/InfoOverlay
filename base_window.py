"""
Module establishing the frameless, multi-monitor clamped base window geometry.
"""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QSizeGrip, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QEvent, QPoint, QObject
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent, QResizeEvent, QCloseEvent, QPaintEvent

if TYPE_CHECKING:
    from asset_service import AssetService

class BaseWindow(QWidget):
    """
    Base architectural frame for managing frameless windows in a healthcare clinic layout.

    Manages Window Lifecycle, Frameless Attribute and Movement, Adds a Resizeable Grip and Make the Window to be Always on Top of other Windows.

    Attributes:
        asset_service (AssetService): Injected core filesystem mapping framework.
        child_windows (list): Tracks associated sub-window objects.
        drag_anchor (QPoint): Real-time offset vector mapping mouse click relative positions.
        main_layout (QVBoxLayout): Global vertical item stack layout manager.
        grip_size (int): Structural dimensions assigned to the custom resize corner.
        grip (QSizeGrip): Visual corner handle allowing interactive structural expansion.
    """

    def __init__(self, asset_service: "AssetService") -> None:
        """Initializes frameless styling layers, custom sizes, and style sheets."""
        super().__init__()
        self.asset_service = asset_service
        self.child_windows: list[QWidget] = []
        self.drag_anchor: QPoint | None = None
        
        # Window Settings to Make it Frameless and Always on Top of other Windows
        self.setWindowFlags( 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Window's Attribute to Make the Background Transparent, Define the Initial Window Geometry and The Minimum Geometry Permited
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(1000, 300)
        self.setMinimumSize(50, 50)

        # Base Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Grip Resizing Element
        self.grip_size = 16
        self.grip = QSizeGrip(self)
        self.grip.resize(self.grip_size, self.grip_size)

        # On Windows, absolute filesystem routes use backwards path decorators (e.g., C:\resources\assets)
        # As so, it is needed to change the standard approach of Qts internal CSS engines
        asset_path: str = self.asset_service.get_asset_path("grip_chevron.svg").replace("\\", "/")
        self.grip.setStyleSheet(f"""
            QSizeGrip {{
                image: url("{asset_path}");
                background-position: center;
                background-repeat: no-repeat;
                background-color: transparent;
            }}
        """)
    def paintEvent(self, event: QPaintEvent):
        """
        Provides a solid mouse tracking platform for Windows DWM while remaining completely colorless.
        
        Forces a near-invisible 1-alpha backdrop fill to ensure the operating system registers mouse inputs
        across transparent UI canvas elements.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

    def register_child_events(self, child_widget: QWidget) -> None:
        """
        Attaches an event monitor to a child element to track its mouse gestures.

        Args:
            child_widget (QWidget): Sub-view or layout whose events need to be intercepted.
        """
        if child_widget:
            child_widget.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """
        Intercepts internal child interactions before they reach the nested layers.

        Since the components are layered into our container, they actually swallow mouse presses, as so the focus from the BaseWindow
        is stealed and we can't drag the window properly anymore.

        Args:
            watched: The underlying QObject dispatching this structural state.
            event (QEvent): The pending window system interaction.

        Returns:
            bool: True if the operation was caught and resolve; otherwise False.
        """
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_anchor = event.globalPosition().toPoint() - self.pos()
                return False  
            elif event.button() == Qt.MouseButton.RightButton:
                self.show_context_options(event.globalPosition().toPoint())
                return True
            
        elif event.type() == QEvent.Type.MouseMove:
            if event.buttons() & Qt.MouseButton.LeftButton and self.drag_anchor:
                global_pos = event.globalPosition().toPoint()
                self.execute_clamped_move(global_pos)
                return True
            
        elif event.type() == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_anchor = None

        return super().eventFilter(watched, event)
    
    def execute_clamped_move(self, global_pos_pixel: QPoint) -> None:
        """
        Calculates window positioning and restricts coordinates to the active monitor bounds.

        The attribute FramelessWindowHint actually bypasses the operating system's native window boundaries.
        So, what happens is basically: if the user drags the engine window quickly or transitions between multi-monitor
        enviroments, the standard dragging logic fails to drop coordinates properly and put the window in a possible unreachable place.
        Because of this we use algebraic min/max clamping algorithm to clip boundaries. By using it, the window's X-coordinate
        can never drop below the active monitor's leftmost edge (screen_geo.left()), and also never surpass the monitor's rightmost limit minus the 
        window's own running width (screen_geo.right() - self.width())

        Args:
            global_pos_pixel (QPoint): Absolute global cursor coordinate position.
        """
        target_pos = global_pos_pixel - self.drag_anchor
        current_screen = QApplication.screenAt(global_pos_pixel)

        if current_screen:
            screen_geo = current_screen.geometry()
            clamped_x = max(screen_geo.left(), min(target_pos.x(), screen_geo.right() - self.width()))
            clamped_y = max(screen_geo.top(), min(target_pos.y(), screen_geo.bottom() - self.height()))
            self.move(clamped_x, clamped_y)
        else:
            self.move(target_pos)

    def show_context_options(self, global_pos: QPoint) -> None:
        """
        Abstract placeholder interface intended for sub-class context menus.

        Args:
            global_pos (QPoint): Target display coordinates where the menu should surface.
        """
        pass

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Captures initial viewport positions to establish base movement offsets."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_anchor = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_options(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Tracks movement updates directly when dragging over raw root areas."""
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_anchor:
            global_pos_pixel = event.globalPosition().toPoint()
            self.execute_clamped_move(global_pos_pixel)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Closes the active window lifecycle sequence if the Escape key is pressed."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Pushes the custom chevron expansion grip layer to the top of the z-order stack."""
        super().resizeEvent(event)
        rect = self.rect()
        self.grip.move(rect.width() - self.grip_size, rect.height() - self.grip_size)
        self.grip.raise_()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Iterates down the active visual layout to flush video buffers and release handles."""
        if hasattr(self, 'main_layout') and self.main_layout:
            for i in range(self.main_layout.count()):
                widget = self.main_layout.itemAt(i).widget()
                if widget and hasattr(widget, 'stop_media'):
                    widget.stop_media()

        event.accept()

