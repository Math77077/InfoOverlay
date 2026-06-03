from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QColorDialog, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QFont, QPainter, QColor

class TextEditHUB(QWidget):
    """
    Dedicated transaction configuration HUD.
    Renders an isolated backdrop and uses layout managers to remain
    completely responsive to window resizing.
    """
    def __init__(self, parent_overlay):
        super().__init__(parent_overlay)
        self.parent_overlay = parent_overlay

        self.setGeometry(self.parent_overlay.rect())

        self.hud_layout = QVBoxLayout(self)
        self.hud_layout.setContentsMargins(30, 0, 30, 0)
        self.hud_layout.setSpacing(6)
        self.hud_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_label = QLabel("Insira seu texto:", self)
        self.header_label.setStyleSheet("""
            QLabel {
                color: rgba(69, 156, 214, 0.9); 
                font-family: 'AlteHaasGrotes';
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                background: transparent;
            }
        """)
        self.hud_layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.input_row_layout = QHBoxLayout()
        self.input_row_layout.setSpacing(15)

        self.text_input = QLineEdit(self)
        self.text_input.setText(self.parent_overlay.label.text())
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 30, 35, 0.85);
                color: #e2e8f0;
                border: 1px solid rgba(69, 156, 214, 0.4);
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Arial';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgb(5, 110, 155);
                background-color: rgba(20, 20, 25, 0.95);
            }
        """)
        self.text_input.returnPressed.connect(self.save_and_close)
        self.input_row_layout.addWidget(self.text_input, stretch=4)

        self.color_btn = QPushButton("Mudar Cor", self)
        self.color_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(5, 110, 155);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Arial';
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgb(7, 134, 189);
            }
            QPushButton:pressed {
                background-color: rgb(3, 85, 120);
            }
        """)
        self.color_btn.clicked.connect(self.change_text_color)
        self.input_row_layout.addWidget(self.color_btn, stretch=1)

        self.hud_layout.addLayout(self.input_row_layout)

        self.text_input.setFocus()

    def change_text_color(self):
        chosen_color = QColorDialog.getColor()
        if chosen_color.isValid():
            self.parent_overlay.current_color = chosen_color.name()
            self.parent_overlay.update_label_style()

    def save_and_close(self):
        self.parent_overlay.label.setText(self.text_input.text())
        self.parent_overlay.close_edit_hud()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 15, 20, 200))

class ScrollingTextOverlay(QWidget):
    """
    High-Frequency Presentation Engine.
    Handles nothing but running the ticker animation and layout geometry tracking.
    """
    def __init__(self, initial_width):
        super().__init__()
        self.x_pos = initial_width
        self.current_color = "white"
        self.active_hud = None

        # DISPLAY TEXT ELEMENT PLACEHOLDER
        self.label = QLabel("Texto de Exemplo Informativo", self)
        self.update_label_style()

        # ANIMATION TIMER
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(20)

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("background: transparent; border: none;")

    def update_label_style(self):
        self.label.setStyleSheet(f"color: {self.current_color}; background: transparent;")

    def update_position(self):
        self.x_pos -= 2
        if self.x_pos < -self.label.width():
            self.x_pos = self.width()

        vertical_center = (self.height() - self.label.height()) // 2
        self.label.move(self.x_pos, vertical_center)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_size()

        if self.active_hud:
            self.active_hud.setGeometry(self.rect())

    def adjust_font_size(self):
        font = QFont("Arial")
        font.setPixelSize(int(self.height() * 0.7))
        self.label.setFont(font)
        self.label.adjustSize()

    def mouseDoubleClickEvent(self, event):
        if not self.active_hud:
            self.open_edit_hud()

    def open_edit_hud(self):
        self.timer.stop()
        self.label.hide()

        self.active_hud = TextEditHUB(self)
        self.active_hud.show()

    def close_edit_hud(self):
        if self.active_hud:
            self.active_hud.deleteLater()
            self.active_hud = None

        self.label.show()
        self.adjust_font_size()
        self.timer.start(20)
