from PySide6.QtWidgets import QWidget, QVBoxLayout, QStyleOption
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor
from PySide6.QtSvg import QSvgRenderer

class PreviewOverlay(QWidget):
    """
    Acts as a visual placeholder.
    Renders a semi-transparent, stylish geometric guide box so the user can reposition/resize the window cleanly.
    """
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.logo_renderer = QSvgRenderer("app_assets/logo.svg")
        self.grid_spacing = 40

        # LAYOUT SETUP
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def apply_settings(self, parent_window):
        parent_window.setStyleSheet("""
            PreviewOverlay {
                background-color: rgba(69, 156, 214, 0.65); 
                border: 2px dashed #056e9b;             
                border-radius: 6px;
            }
        """)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(self.style().PrimitiveElement.PE_Widget, opt, p, self)
        
        grid_color = QColor(255, 255, 255, 30)
        p.setPen(grid_color)

        for x in range(0, self.width(), self.grid_spacing):
            p.drawLine(x, 0, x, self.height())

        for y in range(0, self.height(), self.grid_spacing):
            p.drawLine(0, y, self.width(), y)

        max_allowed_w = self.width() * 0.70
        max_allowed_h = self.height() * 0.75

        default_size = self.logo_renderer.defaultSize()

        scale_factor = min(max_allowed_w / default_size.width(), max_allowed_h / default_size.height())
        
        target_width = int(default_size.width() * scale_factor)
        target_height = int(default_size.height() * scale_factor)

        target_x = (self.width() - target_width) // 2
        target_y = (self.height() - target_height) // 2

        target_rect = QRect(target_x, target_y, target_width, target_height)
        self.logo_renderer.render(p, target_rect)
