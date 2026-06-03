import sys
import os
import platform
if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from asset_service import AssetService
from base_window import BaseWindow
from overlays.text_overlay import ScrollingTextOverlay
from overlays.image_overlay import ImageOverlay
from overlays.video_overlay import VideoOverlay
from overlays.preview_overlay import PreviewOverlay

class AppController(BaseWindow):
    """
    Inherits from BaseWindow.
    Injects the specific context menu and wires up the switching of layout content.
    """

    def __init__(self):
        self.asset_service = AssetService()
        super().__init__(self.asset_service)
        self.current_content = None
        self.asset_service = AssetService()

        # BUILD CONTROLLER INTERFACE
        self.main_menu = QMenu(self)
        self.main_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setup_context_menu()

        self.main_menu.setStyleSheet("""
        QMenu {
            background-color: rgba(31, 40, 51, 0.95);  
            border: 1px solid rgba(69, 156, 214, 0.5); 
            border-radius: 8px;                       
            padding: 5px 0px;
        }
        QMenu::item {
            color: #c5a3a3; 
            padding: 8px 24px;                       
            background-color: transparent;
        }
        QMenu::item:selected {
            background-color: rgb(5, 110, 155);       
            color: white;                             
        }
        QMenu::separator {
            height: 1px;
            background-color: rgba(255, 255, 255, 30);
            margin: 4px 10px;                        
        }    
        """)

        # DEFAULT PREVIEW MODE
        self.switch_mode(PreviewOverlay, self.asset_service)
    
    def show_context_options(self, global_pos):
        self.main_menu.exec(global_pos)

    def setup_context_menu(self):
        new_window_action = QAction("Nova Janela", self)
        new_window_action.triggered.connect(self.spawn_new_window)
        self.main_menu.addAction(new_window_action)

        self.main_menu.addSeparator()

        text_action = QAction("Letreiro", self)
        text_action.triggered.connect(lambda: self.switch_mode(ScrollingTextOverlay, self.width()))
        self.main_menu.addAction(text_action)

        image_action = QAction("Modo Imagem", self)
        image_action.triggered.connect(lambda: self.switch_mode(ImageOverlay, self.asset_service))
        self.main_menu.addAction(image_action)

        video_action = QAction("Modo Vídeo", self)
        video_action.triggered.connect(lambda: self.switch_mode(VideoOverlay, self.asset_service))
        self.main_menu.addAction(video_action)

        self.main_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        self.main_menu.addAction(exit_action)

    def clear_current_content(self):
        if self.current_content:
            if hasattr(self.current_content, 'stop_media'):
                self.current_content.stop_media()

            self.main_layout.removeWidget(self.current_content)
            self.current_content.deleteLater()
            self.current_content = None

    def switch_mode(self, overlay_class, *args):
        self.clear_current_content()
        self.current_content = overlay_class(*args)
        self.main_layout.addWidget(self.current_content)
        self.current_content.apply_settings(self)

        self.register_child_events(self.current_content)

        if hasattr(self.current_content, 'view') and self.current_content.view:
            self.register_child_events(self.current_content.view.viewport())

        self.layout().activate()

        self.grip.raise_()
        self.grip.update()

    def spawn_new_window(self):
        new_window = AppController()
        new_window.asset_service = self.asset_service
        self.child_windows.append(new_window)
        new_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = AppController()
    main_window.show()

    sys.exit(app.exec())