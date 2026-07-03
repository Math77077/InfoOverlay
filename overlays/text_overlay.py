"""
Module implementing high-frequency text ticker layers and interactive edit overlays.
"""

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QColorDialog, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPaintEvent, QResizeEvent, QMouseEvent

class TextEditHUB(QWidget):
    """
    Dedicated transaction configuration HUD drawer layered above the text ticker.

    The HUD allows the staff to change the displayed message on the window, and also its text color.

    Attributes:
        parent_overlay (ScrollingTextOverlay): Reference to the underlying ticker manager.
        hud_layout (QVBoxLayout): Main vertical layout engine holding user interface rows.
        header_label (QLabel): Section header guiding text input.
        input_row_layout (QHBoxLayout): Horizontal field alignment mapping text inputs alongside color triggers.
        text_input (QLineEdit): Interactive text entry box mapping current announcements.
        color_btn (QPushButton): Graphical button launching native desktop color selection fields.
    """

    def __init__(self, parent_overlay: QWidget) -> None:
        """Initializes structural inputs, fields, and custom element design properties."""
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

    def change_text_color(self) -> None:
        """
        Launches the color picker dialog while temporarily disabling the parent 
        window's always-on-top behavior to prevent permanent OS-level stacking locks.
        """
        root_window = self.window()
        
        if root_window:
            root_window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            root_window.show() 

        dialog = QColorDialog(self)
        dialog.setWindowTitle("Selecione a Cor do Letreiro")
        dialog.setCurrentColor(QColor(self.parent_overlay.current_color))
        
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        if dialog.exec() == QColorDialog.DialogCode.Accepted:
            chosen_color = dialog.selectedColor()
            if chosen_color.isValid():
                self.parent_overlay.current_color = chosen_color.name()
                self.parent_overlay.update_label_style()

        if root_window:
            root_window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            root_window.show()

    def save_and_close(self) -> None:
        """Applies updated text inputs back to the parent canvas and safely drops the HUD context."""
        self.parent_overlay.label.setText(self.text_input.text())
        self.parent_overlay.close_edit_hud()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Renders an isolated translucent backdrop panel blocking out distraction shapes."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 15, 20, 200))

class ScrollingTextOverlay(QWidget):
    """
    High-Frequency Presentation Engine.
    
    Handles continuous ticker translations, bounds detection wrapping, and responsive sizing layers.

    Attributes:
        x_pos (int): Horizontal pixel tracking coordinate mapping text position offsets.
        current_color (str): Current hex color configuration mapping text display fills.
        active_hud (TextEditHUB | None): Active overlay tracking configuration menu states.
        label (QLabel): Underlying presentation graphic object displaying the string.
        timer (QTimer): Micro-interval trigger loop maintaning smooth animation ticks.
    """

    def __init__(self, initial_width: int) -> None:
        """Initializes internal variables, positions labels, and runs ticker clocks."""
        super().__init__()
        self.x_pos: int = initial_width
        self.current_color: str = "white"
        self.active_hud: TextEditHUB | None = None

        # Display Text Element Placeholder
        self.label = QLabel("Texto de Exemplo Informativo", self)
        self.update_label_style()

        # Animation Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(20)

    def apply_settings(self, parent_window: QWidget) -> None:
        """Strips out border parameters from structural wrappers."""
        parent_window.setStyleSheet("background: transparent; border: none;")

    def update_label_style(self) -> None:
        """Synchronizes color variables with the current active style sheets."""
        self.label.setStyleSheet(f"color: {self.current_color}; background: transparent;")

    def update_position(self) -> None:
        """
        Updates rendering positions and manages continuous coordinate wrap cycles.
        
        Every 20 milliseconds, the QTimer updates. While it updates if decrements the self.x_pos coordinate by 2 pixels.
        Once the text has scrolled completely past the screen's left edge (-self.label.width()), it snaps back to the absolute
        right side (self.width()), resetting the continuous broadcast loop.
        """
        self.x_pos -= 2
        if self.x_pos < -self.label.width():
            self.x_pos = self.width()

        vertical_center = (self.height() - self.label.height()) // 2
        self.label.move(self.x_pos, vertical_center)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Recalculates proportional structural components during frame transformations."""
        super().resizeEvent(event)
        self.adjust_font_size()

        if self.active_hud:
            self.active_hud.setGeometry(self.rect())

    def adjust_font_size(self) -> None:
        """
        Adjusts the layout typography dynamically based on window proportions.

        Everytime a resizeEvent hits the application, the engine samples the running widget height,
        then scales the pixel size of the font to exactly 70% of the view window. Right after, it recalculates
        bounding boxes using self.label.adjustSize()
        """
        font = QFont("Arial")
        font.setPixelSize(int(self.height() * 0.7))
        self.label.setFont(font)
        self.label.adjustSize()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Captures mouse double clicks to activate configuration layers."""
        if not self.active_hud:
            self.open_edit_hud()

    def open_edit_hud(self) -> None:
        """Halts running ticker engines and surfaces configuration management inputs."""
        self.timer.stop()
        self.label.hide()

        self.active_hud = TextEditHUB(self)
        self.active_hud.show()

    def close_edit_hud(self) -> None:
        """Flushes temporary configuration frames out of memory and resumes ticker updates."""
        if self.active_hud:
            self.active_hud.deleteLater()
            self.active_hud = None

        self.label.show()
        self.adjust_font_size()
        self.timer.start(20)
