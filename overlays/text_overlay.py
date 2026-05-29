from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QColorDialog, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor

class ScrollingTextOverlay(QWidget):
    """
    Manages the horizontal scrolling text banner.
    Allows double-clicking to edit the text dynamically.
    """
    def __init__(self, initial_width):
        super().__init__()
        self.is_editing = False
        self.x_pos = initial_width
        self.current_color = "white"

        # DISPLAY TEXT ELEMENT PLACEHOLDER
        self.label = QLabel("Texto de Exemplo Informativo", self)
        self.label.setStyleSheet(f"color: {self.current_color}; background: transparent;")

        # HIDDEN INPUT FIELD USED WHEN EDITING
        self.text_input = QLineEdit(self)
        self.text_input.hide()
        self.text_input.returnPressed.connect(self.edit_mode)

        # COLOR BUTTON
        self.color_btn = QPushButton("Mudar Cor", self)
        self.color_btn.hide()
        self.color_btn.clicked.connect(self.change_text_color)

        # ANIMATION TIMER
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(20)

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("background: transparent; border: none;")

    def update_position(self):
        if not self.is_editing:
            self.x_pos -= 2

            if self.x_pos < -self.label.width():
                self.x_pos = self.width()

            vertical_center = (self.height() - self.label.height()) // 2
            self.label.move(self.x_pos, vertical_center)

    def paintEvent(self, event):
        if self.is_editing:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_size()

    def adjust_font_size(self):
        font = QFont("Arial")
        font.setPixelSize(int(self.height() * 0.7))
        self.label.setFont(font)
        self.label.adjustSize()

    def change_text_color(self):
        chosen_color = QColorDialog.getColor()
        if chosen_color.isValid(): 
            self.current_color = chosen_color.name()
            self.label.setStyleSheet(f"color: {self.current_color}; background: transparent;")


    def mouseDoubleClickEvent(self, event):
        self.edit_mode()

    def edit_mode(self):
        if not self.is_editing:
            self.is_editing = True
            self.timer.stop()
            self.label.hide()

            self.text_input.setText(self.label.text())
            self.text_input.setGeometry(10, (self.height() - 40) // 2, self.width() - 120, 40)
            self.text_input.show()
            self.color_btn.setGeometry(self.width() - 110, (self.height() - 40) // 2, 100, 40)
            self.color_btn.show()
            self.text_input.setFocus()
            self.update()
        else:
            self.is_editing = False
            self.label.setText(self.text_input.text())
            self.text_input.hide()
            self.color_btn.hide()
            self.label.show()
            self.adjust_font_size()
            self.timer.start(20)
            self.update()