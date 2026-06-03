import platform
from PySide6.QtWidgets import QWidget, QSizeGrip, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QEvent

if platform.system() == "Windows":
    import ctypes
    from os import winmode

class BaseWindow(QWidget):
    """
    Window lifecycle, frameless movement, resizing grip, and the right-click global context menu frame.
    """
    def __init__(self, asset_service):
        super().__init__()
        self.asset_service = asset_service
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

        self.setStyleSheet("""
            !BaseWindow {
                background-color: rgba(0, 0, 0, 1);
                border: none;
            }
        """)

        # BASE LAYOUT
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # RESIZING ELEMENT SETUP (GRIP)
        self.grip_size = 16
        self.grip = QSizeGrip(self)
        self.grip.resize(self.grip_size, self.grip_size)

        asset_path = self.asset_service.get_asset_path("grip_chevron.svg").replace("\\", "/")
        self.grip.setStyleSheet(f"""
            QSizeGrip {{
                image: url("{asset_path}");
                background-position: center;
                background-repeat: no-repeat;
                background-color: transparent;
            }}
        """)
    def register_child_events(self, child_widget):
        if child_widget:
            child_widget.installEventFilter(self)

    def nativeEvent(self, eventType, message):
        if platform.system() == "Windows" and eventType == b"windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == 0x0084:
                result, data = super().nativeEvent(eventType, message)
                
                if data == 17:
                    return result, data
                    
                return True, 2
        return super().nativeEvent(eventType, message)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_anchor = event.globalPosition().toPoint() - self.pos()
            elif event.button() == Qt.MouseButton.RightButton:
                self.show_context_options(event.globalPosition().toPoint())
                return True
                
        elif event.type() == QEvent.Type.MouseMove:
            if platform.system() != "Windows":
                if event.buttons() & Qt.MouseButton.LeftButton and self.drag_anchor:
                    global_pos = event.globalPosition().toPoint()
                    self.execute_clamped_move(global_pos)
                    return True
                
        elif event.type() == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_anchor = None

        return super().eventFilter(watched, event)
    
    def execute_clamped_move(self, global_pos_pixel):
        target_pos = global_pos_pixel - self.drag_anchor
        current_screen = QApplication.screenAt(global_pos_pixel)

        if current_screen:
            screen_geo = current_screen.geometry()
            clamped_x = max(screen_geo.left(), min(target_pos.x(), screen_geo.right() - self.width()))
            clamped_y = max(screen_geo.top(), min(target_pos.y(), screen_geo.bottom() - self.height()))
            self.move(clamped_x, clamped_y)
        else:
            self.move(target_pos)

    def show_context_options(self, global_pos):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_anchor = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_options(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_anchor:
            global_pos_pixel = event.globalPosition().toPoint()
            target_pos = global_pos_pixel - self.drag_anchor

            current_screen = QApplication.screenAt(global_pos_pixel)
            
            if current_screen:
                screen_geo = current_screen.geometry()
                clamped_x = max(screen_geo.left(), min(target_pos.x(), screen_geo.right() - self.width()))
                clamped_y = max(screen_geo.top(), min(target_pos.y(), screen_geo.bottom() - self.height()))
                self.move(clamped_x, clamped_y)
            else:
                self.move(target_pos)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        self.grip.move(rect.width() - self.grip_size, rect.height() - self.grip_size)
        self.grip.raise_()

    def closeEvent(self, event):
        if hasattr(self, 'main_layout') and self.main_layout:
            for i in range(self.main_layout.count()):
                widget = self.main_layout.itemAt(i).widget()
                if widget and hasattr(widget, 'stop_media'):
                    widget.stop_media()

        event.accept()

