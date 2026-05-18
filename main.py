import sys
import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem

try:
    import resources_rc
except ImportError:
    print("Warning: resources_rc not found.")

class BaseOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.windows = []
        self.curr_content = None 

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.resize(1000, 300)
        self.setMinimumSize(50, 50)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: #2c3e50;")

        # MENU
        self.menu = QMenu(self)
        
        new_window_btn = QAction("Nova Janela", self)
        new_window_btn.triggered.connect(self.createWindow)
        self.menu.addAction(new_window_btn)

        self.menu.addSeparator()

        self.menu.addAction("Letreiro", self.swapFrameContent)
        self.menu.addAction("Modo Imagem", self.switchToImageMode)
        self.menu.addAction("Modo Vídeo", self.switchToVideoMode)
        
        self.menu.addSeparator()
        
        leave_btn = QAction("Sair", self)
        leave_btn.triggered.connect(self.close)
        self.menu.addAction(leave_btn)

        # GRIP
        self.grip_size = 16
        self.grip = QSizeGrip(self)
        self.grip.resize(self.grip_size, self.grip_size) 
        self.grip.setStyleSheet("background-color: rgba(255, 255, 255, 30); border-radius: 8px;")

        # LAYOUT
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # INITIAL CONTENT
        self.curr_content = QWidget()
        self.layout.addWidget(self.curr_content)
        self.grip.raise_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_anchor = event.position().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_anchor
            self.move(new_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        self.grip.move(rect.width() - self.grip_size, rect.height() - self.grip_size)

    def createWindow(self):
        new_window = BaseOverlay()
        self.windows.append(new_window)
        new_window.show()

    def clearLayout(self):
        if self.curr_content:
            self.layout.removeWidget(self.curr_content)
            self.curr_content.deleteLater()
            self.curr_content = None

    def swapFrameContent(self):
        self.clearLayout()
        self.curr_content = ScrollingTextOverlay(self.width())
        self.layout.addWidget(self.curr_content)
        self.curr_content.apply_settings(self)
        self.grip.raise_()

    def switchToImageMode(self):
        self.clearLayout()
        self.curr_content = ImageOverlay("resources") 
        self.layout.addWidget(self.curr_content)
        self.curr_content.apply_settings(self) 
        self.grip.raise_()

    def switchToVideoMode(self):
        self.clearLayout()
        self.curr_content = VideoOverlay("resources") 
        self.layout.addWidget(self.curr_content)
        self.curr_content.apply_settings(self)
        self.grip.raise_()

    def closeEvent(self, event):
        try:
            if hasattr(self.curr_content, 'stop_media'):
                self.curr_content.stop_media()
        except Exception as e:
            print(f"Erro ao parar mídia: {e}")
        
        for window in self.windows:
            window.close()
        event.accept()
            

class ScrollingTextOverlay(QWidget):
    def __init__(self, width):
        super().__init__()
        self.is_editing = False
        self.x_pos = width
        
        self.label = QLabel("Texto de exemplo informativo UBS", self)
        self.label.setStyleSheet("color: white; background: transparent;")
        
        self.text_input = QLineEdit(self)
        self.text_input.hide()
        self.text_input.returnPressed.connect(self.edit_mode)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePosition)
        self.timer.start(20)

    def apply_settings(self, parent):
        parent.setStyleSheet("background: transparent; border: none;")

    def updatePosition(self):
        if not self.is_editing:
            self.x_pos -= 2
            if self.x_pos < -self.label.width():
                self.x_pos = self.width()
            self.label.move(self.x_pos, (self.height() - self.label.height()) // 2)

    def paintEvent(self, event):
        if self.is_editing:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustFontSize()

    def adjustFontSize(self):
        font = QFont("Arial")
        font.setPixelSize(int(self.height() * 0.7))
        self.label.setFont(font)
        self.label.adjustSize()

    def mouseDoubleClickEvent(self, event):
        self.edit_mode()

    def edit_mode(self):
        if not self.is_editing:
            self.is_editing = True
            self.timer.stop()
            self.label.hide()
            self.text_input.setText(self.label.text())
            self.text_input.setGeometry(10, (self.height()-40)//2, self.width()-20, 40)
            self.text_input.show()
            self.text_input.setFocus()
            self.update()
        else:
            self.is_editing = False
            self.label.setText(self.text_input.text())
            self.text_input.hide()
            self.label.show()
            self.adjustFontSize()
            self.timer.start(20)
            self.update()

class ImageOverlay(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        self.pixmap = None
        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.load_best_image)
        self.load_best_image()

    def load_best_image(self):
        if not os.path.exists(self.folder_path): return
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.png', '.jpg'))]
        if not files: return
        
        is_landscape = self.width() >= self.height()
        path = os.path.join(self.folder_path, files[0]) # Default
        
        for f in files:
            if is_landscape and "_h" in f.lower(): path = os.path.join(self.folder_path, f); break
            if not is_landscape and "_v" in f.lower(): path = os.path.join(self.folder_path, f); break
            
        self.pixmap = QPixmap(path)
        self.update_display()

    def update_display(self):
        if self.pixmap:
            scaled = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        self.check_timer.start(100)

    def apply_settings(self, parent):
        parent.setStyleSheet("background: transparent;")

class VideoOverlay(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        self.view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.view.setFrameShape(QFrame.Shape.NoFrame)
        self.view.setStyleSheet("background: transparent;") 
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setVideoOutput(self.video_item)
        self.media_player.setAudioOutput(self.audio_output)
        
        self.layout.addWidget(self.view)
        
        self.current_video = ""
        self.media_player.playbackStateChanged.connect(self.handle_loop)
        
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.load_best_video)
        
        QTimer.singleShot(200, self.load_best_video)

    def stop_media(self):
        """Para a mídia de forma limpa"""
        self.media_player.stop()
        self.media_player.setSource(QUrl(""))

    def load_best_video(self):
        if not os.path.exists(self.folder_path): return
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.mp4', '.mov'))]
        if not files: return
        
        is_landscape = self.width() >= self.height()
        target = files[0]
        
        for f in files:
            if is_landscape and "_h" in f.lower(): target = f; break
            if not is_landscape and "_v" in f.lower(): target = f; break
        
        path = os.path.abspath(os.path.join(self.folder_path, target))
        
        if path != self.current_video:
            self.current_video = path
            self.media_player.setSource(QUrl.fromLocalFile(path))
            self.media_player.play()
        
        self.update_video_size()

    def update_video_size(self):
        """Ajusta o tamanho do vídeo para caber na cena sem esticar"""
        size = self.size()
        self.video_item.setSize(QSizeF(size.width(), size.height()))
        self.view.setSceneRect(0, 0, size.width(), size.height())

    def handle_loop(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.media_player.play()

    def resizeEvent(self, event):
        self.update_video_size()
        self.resize_timer.start(300)
        super().resizeEvent(event)

    def apply_settings(self, parent):
        parent.setStyleSheet("background: transparent; border: none;")
        parent.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaseOverlay()
    window.show()
    sys.exit(app.exec())

