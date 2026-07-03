"""
Module managing the interactive system placement guide and vector grid presentation layer.
"""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStyleOption
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPaintEvent
from PySide6.QtSvg import QSvgRenderer

if TYPE_CHECKING:
    from asset_service import AssetService

class PreviewOverlay(QWidget):
    """
    Interactive placement framework serving as a sizing blueprint for clinic personnel.

    Acts as a visual placeholder and renders a semi-transparent, stylish geometric 
    guide box so the user can position and resize the window cleanly across monitors.

    Attributes:
        asset_service (AssetService): Injected core filesystem mapping framework.
        logo_renderer (QSvgRenderer): SVG vector asset painter avoiding pixelation.
        grid_spacing (int): Pixel intervals separating background blueprint lines.
        layout (QVBoxLayout): Container manager centering child layout items.
    """

    def __init__(self, asset_service: "AssetService") -> None:
        """Initializes structural canvas layers, layout grids, and loads vector resources."""
        super().__init__()
        self.asset_service = asset_service
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        logo_path: str = self.asset_service.get_asset_path("logo.svg")
        self.logo_renderer = QSvgRenderer(logo_path)
        self.grid_spacing: int = 40

        # Layout Setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def apply_settings(self, parent_window: QWidget) -> None:
        """
        Applies a dashed blueprint layout theme directly to the view instance.

        Args:
            parent_window (QWidget): The underlying window instance hosting this layout layer.
        """
        parent_window.setStyleSheet("""
            PreviewOverlay {
                background-color: rgba(69, 156, 214, 0.65); 
                border: 2px dashed #056e9b;             
                border-radius: 6px;
            }
        """)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Renders native styling primitives, an alignment grid, and a scaled central SVG asset.

        Executes layout presentation in three stages:
        1. Invokes primitive drawing engines to preserve background CSS rules.
        2. Iterates across window width and height to construct a subtle background alignment grid.
        3. Computes a localized aspect ratio constraint factor to paint the vector logo cleanly.

        Args:
            event (QPaintEvent): System layout rendering instruction loop parameter.
        """
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
