# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: utils\responsive.py
"""
Responsive Utils - Utilities for responsive UI layout
Handles different screen resolutions and DPI scaling
"""
import sys
import re
import weakref
from typing import Tuple, List
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QScreen
from PyQt5.QtCore import QSize, QRect

class ScreenInfo:
    __doc__ = "\n    Screen information and responsive layout utilities\n    "
    COMPACT_WIDTH = 1024
    STANDARD_WIDTH = 1440
    WIDE_WIDTH = 1920

    def __init__(self):
        self._app = QApplication.instance()
        self._screen = self._app.primaryScreen() if self._app else None
        self._dpi_scale = 1.0
        self._update_dpi()

    def _update_dpi(self):
        """Update DPI scale factor"""
        if self._screen:
            logical_dpi = self._screen.logicalDotsPerInch()
            self._dpi_scale = logical_dpi / 96.0

    @property
    def dpi_scale(self) -> float:
        """Get DPI scale factor"""
        return self._dpi_scale

    @property
    def screen_geometry(self) -> QRect:
        """Get available screen geometry"""
        if self._screen:
            return self._screen.availableGeometry()
        return QRect(0, 0, 1920, 1080)

    @property
    def screen_size(self) -> Tuple[(int, int)]:
        """Get screen size (width, height)"""
        geometry = self.screen_geometry
        return (geometry.width(), geometry.height())

    @property
    def is_compact(self) -> bool:
        """Check if screen is compact (small)"""
        width, _ = self.screen_size
        return width < self.COMPACT_WIDTH

    @property
    def is_standard(self) -> bool:
        """Check if screen is standard size"""
        width, _ = self.screen_size
        return self.COMPACT_WIDTH <= width < self.WIDE_WIDTH

    @property
    def is_wide(self) -> bool:
        """Check if screen is wide (large)"""
        width, _ = self.screen_size
        return width >= self.WIDE_WIDTH

    def scaled_size(self, base_width: int, base_height: int) -> Tuple[(int, int)]:
        """
        Scale a base size according to DPI

        Args:
            base_width: Base width in pixels (at 96 DPI)
            base_height: Base height in pixels (at 96 DPI)

        Returns:
            Tuple of scaled (width, height)
        """
        return (
         int(base_width * self._dpi_scale), int(base_height * self._dpi_scale))

    def scaled_font_size(self, base_size: int) -> int:
        """
        Scale a base font size according to DPI

        Args:
            base_size: Base font size in points

        Returns:
            Scaled font size
        """
        return max(8, int(base_size * self._dpi_scale))

    def get_layout_mode(self) -> str:
        """
        Get recommended layout mode

        Returns:
            'compact', 'standard', or 'wide'
        """
        if self.is_compact:
            return "compact"
        if self.is_wide:
            return "wide"
        return "standard"

    def get_panel_widths(self) -> Tuple[(int, int, int)]:
        """
        Get recommended panel widths for three-column layout

        Returns:
            Tuple of (left_panel, middle_panel, right_panel) widths
        """
        total_width, _ = self.screen_size
        if self.is_compact:
            left = min(220, int(total_width * 0.18))
            middle = int(total_width * 0.82)
            right = 0
        else:
            if self.is_wide:
                left = int(total_width * 0.15)
                middle = int(total_width * 0.7)
                right = int(total_width * 0.15)
            else:
                left = int(total_width * 0.18)
                middle = int(total_width * 0.64)
                right = int(total_width * 0.18)
        return (
         left, middle, right)

    def get_margins(self) -> Tuple[(int, int, int, int)]:
        """
        Get recommended margins (left, top, right, bottom)

        Returns:
            Tuple of margin values
        """
        if self.is_compact:
            return (4, 4, 4, 4)
        if self.is_wide:
            return (12, 12, 12, 12)
        return (8, 8, 8, 8)

    def get_spacing(self) -> int:
        """Get recommended spacing between elements"""
        if self.is_compact:
            return 4
        if self.is_wide:
            return 12
        return 8

    def center_window(self, window, width: int, height: int):
        """
        Center a window on screen

        Args:
            window: QMainWindow or QWidget to center
            width: Window width
            height: Window height
        """
        screen_width, screen_height = self.screen_size
        width = min(width, int(screen_width * 0.9))
        height = min(height, int(screen_height * 0.9))
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.setGeometry(x, y, width, height)

    def get_default_window_size(self) -> Tuple[(int, int)]:
        """
        Get default window size based on screen

        Returns:
            Tuple of (width, height)
        """
        screen_width, screen_height = self.screen_size
        if self.is_compact:
            return (
             int(screen_width * 0.9), int(screen_height * 0.85))
        if self.is_wide:
            return (1600, 1000)
        return (1400, 900)


class UIScale:
    """
    Central UI scale manager.

    Keeps a single ``scale`` factor derived from the user's *Interface Font*
    choice and the current screen DPI.  All hard-coded pixel metrics in the
    stylesheet, fixed widget heights and panel widths are multiplied by this
    factor so that text never overflows its container when the font grows.

    The scale is applied two ways so that it also works for widgets whose
    font is overridden by a stylesheet (``font-size: Npx``):
      * metrics are scaled in QSS before it is handed to Qt, and
      * an application-wide font of ``UI_BASE_PT * scale`` points is set.
    """

    #: Interface font (pt) that the fixed pixel metrics were designed for.
    BASE_FONT_PT = 10.0
    MIN_SCALE = 0.7
    MAX_SCALE = 2.2
    #: Hard ceiling for the scaled interface font; the QSS metrics keep
    #: scaling beyond this so text still fits even at extreme sizes.
    FONT_MAX_SCALE = 1.8

    _PIXEL_RE = re.compile(r'(-?\d+(?:\.\d+)?)px')

    def __init__(self):
        self._scale = 1.0
        self._registry: List[weakref.ReferenceType] = []

    @property
    def scale(self) -> float:
        return self._scale

    def set_from_font_point_size(self, point_size: float) -> float:
        """Set the scale from an interface font point size."""
        try:
            value = point_size if point_size and point_size > 0 else self.BASE_FONT_PT
        except TypeError:
            value = self.BASE_FONT_PT
        return self.set_scale(value / self.BASE_FONT_PT)

    def set_scale(self, scale: float) -> float:
        """Set an explicit scale factor (clamped to a sane range)."""
        try:
            scale = float(scale)
        except (TypeError, ValueError):
            scale = 1.0
        self._scale = max(self.MIN_SCALE, min(self.MAX_SCALE, scale))
        return self._scale

    def register(self, widget) -> None:
        """Register a widget whose fixed size must be rescaled.

        ``widget`` must expose a zero-argument ``apply_ui_scale()`` method.
        """
        try:
            ref = weakref.ref(widget)
        except TypeError:
            return
        if not any(r() is widget for r in self._registry):
            self._registry.append(ref)

    def unregister(self, widget) -> None:
        self._registry = [r for r in self._registry if r() not in (None, widget)]

    def refresh(self) -> None:
        """Re-apply the current scale to every registered widget."""
        alive = []
        for ref in self._registry:
            widget = ref()
            if widget is None:
                continue
            alive.append(ref)
            try:
                widget.apply_ui_scale()
            except Exception:
                pass
        self._registry = alive

    def scaled(self, value: float) -> int:
        """Return ``value`` multiplied by the scale (rounded down)."""
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0
        return int(round(value * self._scale))

    def scaled_float(self, value: float) -> float:
        return float(value) * self._scale

    def font_point_size(self) -> float:
        """Point size to feed ``QFont`` so Qt-native widgets scale too."""
        scale = min(self._scale, self.FONT_MAX_SCALE)
        return round(self.BASE_FONT_PT * scale, 1)

    def scale_stylesheet(self, stylesheet: str) -> str:
        """Scale every ``Npx`` metric found in a Qt stylesheet."""
        if not stylesheet:
            return stylesheet
        scale = self._scale
        if abs(scale - 1.0) < 1e-6:
            return stylesheet

        def _replace(match):
            value = float(match.group(1)) * scale
            rounded = int(round(value))
            return f"{rounded}px"

        return self._PIXEL_RE.sub(_replace, stylesheet)


_ui_scale: UIScale = None

def get_ui_scale() -> UIScale:
    """Get the global UIScale instance."""
    global _ui_scale
    if _ui_scale is None:
        _ui_scale = UIScale()
    return _ui_scale


_screen_info: ScreenInfo = None

def get_screen_info() -> ScreenInfo:
    """Get the global ScreenInfo instance"""
    global _screen_info
    if _screen_info is None:
        _screen_info = ScreenInfo()
    return _screen_info


def scaled_font(base_size: int) -> int:
    """Convenience function to get scaled font size"""
    return get_screen_info().scaled_font_size(base_size)


def scaled_size(base_width: int, base_height: int) -> Tuple[(int, int)]:
    """Convenience function to get scaled size"""
    return get_screen_info().scaled_size(base_width, base_height)


def ui_scale() -> float:
    """Convenience function to get the current UI scale factor."""
    return get_ui_scale().scale


def ui(value: float) -> int:
    """Convenience function to scale a pixel metric."""
    return get_ui_scale().scaled(value)
