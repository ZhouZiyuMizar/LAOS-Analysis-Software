# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: utils\themes.py
"""
Themes - Theme definitions and management for ChemicalStrain
Optimized for responsive/adaptive layouts
"""
from typing import Dict, Any
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    __doc__ = "\n    Theme manager for application-wide styling\n    "
    theme_changed = pyqtSignal(str)
    LIGHT = {
     'name': '"light"', 
     'background': '"#F5F5F5"', 
     'surface': '"#FFFFFF"', 
     'surface_alt': '"#FAFAFA"', 
     'text': '"#212121"', 
     'text_secondary': '"#757575"', 
     'text_disabled': '"#9E9E9E"', 
     'primary': '"#2196F3"', 
     'primary_light': '"#64B5F6"', 
     'primary_dark': '"#1976D2"', 
     'secondary': '"#FF5722"', 
     'accent': '"#4CAF50"', 
     'error': '"#F44336"', 
     'warning': '"#FF9800"', 
     'success': '"#4CAF50"', 
     'border': '"#E0E0E0"', 
     'border_light': '"#EEEEEE"', 
     'divider': '"#BDBDBD"', 
     'hover': '"#F0F0F0"', 
     'selected': '"#E3F2FD"', 
     'disabled': '"#F5F5F5"', 
     'shadow': '"rgba(0, 0, 0, 0.08)"', 
     'plot_background': '"#FFFFFF"', 
     'plot_grid': '"#E0E0E0"', 
     'plot_axis': '"#424242"', 
     'log_background': '"#1E1E1E"', 
     'log_text': '"#D4D4D4"', 
     'log_info': '"#4EC9B0"', 
     'log_warning': '"#DCDCAA"', 
     'log_error': '"#F44747"'}
    DARK = {
     'name': '"dark"', 
     'background': '"#121212"', 
     'surface': '"#1E1E1E"', 
     'surface_alt': '"#2D2D2D"', 
     'text': '"#E0E0E0"', 
     'text_secondary': '"#9E9E9E"', 
     'text_disabled': '"#616161"', 
     'primary': '"#64B5F6"', 
     'primary_light': '"#90CAF9"', 
     'primary_dark': '"#42A5F5"', 
     'secondary': '"#FF8A65"', 
     'accent': '"#81C784"', 
     'error': '"#EF5350"', 
     'warning': '"#FFB74D"', 
     'success': '"#81C784"', 
     'border': '"#424242"', 
     'border_light': '"#333333"', 
     'divider': '"#616161"', 
     'hover': '"#383838"', 
     'selected': '"#1E3A5F"', 
     'disabled': '"#2D2D2D"', 
     'shadow': '"rgba(0, 0, 0, 0.3)"', 
     'plot_background': '"#2D2D2D"', 
     'plot_grid': '"#424242"', 
     'plot_axis': '"#BDBDBD"', 
     'log_background': '"#1E1E1E"', 
     'log_text': '"#D4D4D4"', 
     'log_info': '"#4EC9B0"', 
     'log_warning': '"#DCDCAA"', 
     'log_error': '"#F44747"'}

    def __init__(self):
        super().__init__()
        self._current_theme = "light"
        self._theme_data = self.LIGHT.copy()

    def get_theme(self) -> str:
        return self._current_theme

    def set_theme(self, theme_name: str) -> bool:
        if theme_name == self._current_theme:
            return False
        elif theme_name == "light":
            self._theme_data = self.LIGHT.copy()
        else:
            if theme_name == "dark":
                self._theme_data = self.DARK.copy()
            else:
                return False
        self._current_theme = theme_name
        self.theme_changed.emit(theme_name)
        return True

    def get_color(self, key: str, default: str='#000000') -> str:
        return self._theme_data.get(key, default)

    def get_theme_data(self) -> Dict[(str, Any)]:
        return self._theme_data.copy()

    def get_stylesheet(self) -> str:
        """Get responsive, UI-scale-aware stylesheet"""
        from utils.responsive import get_ui_scale
        t = self._theme_data
        stylesheet = f'\n            /* ==================== Global ==================== */\n            QMainWindow {{\n                background-color: {t["background"]};\n            }}\n            QWidget {{\n                color: {t["text"]};\n                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;\n                font-size: 11px;\n            }}\n\n            /* ==================== GroupBox - Compact ==================== */\n            QGroupBox {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border_light"]};\n                border-radius: 6px;\n                margin-top: 14px;\n                padding: 6px;\n                padding-top: 16px;\n                font-weight: 500;\n                font-size: 11px;\n            }}\n            QGroupBox::title {{\n                subcontrol-origin: margin;\n                left: 8px;\n                padding: 0 3px;\n                color: {t["text"]};\n                font-size: 10px;\n            }}\n\n            /* ==================== Buttons - Responsive ==================== */\n            QPushButton {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                border-radius: 4px;\n                padding: 4px 8px;\n                color: {t["text"]};\n                font-weight: 500;\n                font-size: 10px;\n                min-height: 16px;\n            }}\n            QPushButton:hover {{\n                background-color: {t["hover"]};\n                border-color: {t["text_secondary"]};\n            }}\n            QPushButton:pressed {{\n                background-color: {t["selected"]};\n            }}\n            QPushButton:disabled {{\n                background-color: {t["disabled"]};\n                color: {t["text_disabled"]};\n            }}\n\n            /* ==================== Inputs ==================== */\n            QLineEdit, QSpinBox, QDoubleSpinBox {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                border-radius: 4px;\n                padding: 3px 6px;\n                color: {t["text"]};\n                font-size: 10px;\n                min-height: 16px;\n            }}\n            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{\n                border-color: {t["text_secondary"]};\n            }}\n            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{\n                border-color: {t["primary"]};\n            }}\n\n            /* ==================== Check / Radio ==================== */\n            QCheckBox, QRadioButton {{\n                font-size: 10px;\n                spacing: 6px;\n            }}\n            QCheckBox::indicator, QRadioButton::indicator {{\n                width: 13px;\n                height: 13px;\n            }}\n\n            QComboBox {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                border-radius: 4px;\n                padding: 3px 6px;\n                padding-right: 20px;\n                color: {t["text"]};\n                font-size: 10px;\n                min-height: 16px;\n            }}\n            QComboBox:hover {{\n                border-color: {t["text_secondary"]};\n            }}\n            QComboBox::drop-down {{\n                border: none;\n                width: 20px;\n            }}\n            QComboBox::down-arrow {{\n                image: none;\n                border-left: 4px solid transparent;\n                border-right: 4px solid transparent;\n                border-top: 5px solid {t["text_secondary"]};\n            }}\n            QComboBox QAbstractItemView {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["primary"]};\n                selection-background-color: {t["selected"]};\n                font-size: 10px;\n            }}\n\n            /* ==================== List Widget ==================== */\n            QListWidget, QListView, QTreeWidget, QTreeView {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                border-radius: 4px;\n                padding: 2px;\n                font-size: 10px;\n            }}\n            QListWidget::item, QListView::item, QTreeWidget::item {{\n                padding: 3px 6px;\n                border-radius: 3px;\n            }}\n            QListWidget::item:selected, QListView::item:selected, QTreeWidget::item:selected {{\n                background-color: {t["selected"]};\n            }}\n            QListWidget::item:hover, QListView::item:hover, QTreeWidget::item:hover {{\n                background-color: {t["hover"]};\n            }}\n\n            /* ==================== Table ==================== */\n            QTableWidget, QTableView {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                gridline-color: {t["border_light"]};\n                font-size: 10px;\n            }}\n            QHeaderView::section {{\n                background-color: {t["surface_alt"]};\n                padding: 3px 6px;\n                border: 1px solid {t["border"]};\n                font-size: 10px;\n            }}\n\n            /* ==================== Text Edit ==================== */\n            QTextEdit, QPlainTextEdit {{\n                border: 1px solid {t["border"]};\n                border-radius: 4px;\n                font-size: 10px;\n            }}\n\n            /* ==================== Tab Widget ==================== */\n            QTabWidget::pane {{\n                border: none;\n                background-color: {t["surface"]};\n            }}\n            QTabBar::tab {{\n                background-color: transparent;\n                border: none;\n                padding: 4px 10px;\n                color: {t["text_secondary"]};\n                font-size: 10px;\n            }}\n            QTabBar::tab:selected {{\n                background-color: {t["surface"]};\n                color: {t["primary"]};\n                font-weight: 500;\n            }}\n            QTabBar::tab:hover {{\n                background-color: {t["hover"]};\n            }}\n\n            /* ==================== Scroll Bars ==================== */\n            QScrollBar:vertical {{\n                background-color: transparent;\n                width: 10px;\n            }}\n            QScrollBar::handle:vertical {{\n                background-color: {t["border"]};\n                border-radius: 5px;\n                min-height: 20px;\n            }}\n            QScrollBar::handle:vertical:hover {{\n                background-color: {t["text_secondary"]};\n            }}\n            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{\n                height: 0px;\n            }}\n            QScrollBar:horizontal {{\n                background-color: transparent;\n                height: 10px;\n            }}\n            QScrollBar::handle:horizontal {{\n                background-color: {t["border"]};\n                border-radius: 5px;\n                min-width: 20px;\n            }}\n            QScrollBar::handle:horizontal:hover {{\n                background-color: {t["text_secondary"]};\n            }}\n            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{\n                width: 0px;\n            }}\n\n            /* ==================== ScrollArea ==================== */\n            QScrollArea {{\n                background-color: transparent;\n                border: none;\n            }}\n\n            /* ==================== Menu ==================== */\n            QMenuBar {{\n                background-color: {t["surface"]};\n                border-bottom: 1px solid {t["border_light"]};\n                padding: 2px 4px;\n                font-size: 11px;\n            }}\n            QMenuBar::item {{\n                padding: 4px 8px;\n                border-radius: 4px;\n            }}\n            QMenuBar::item:selected {{\n                background-color: {t["selected"]};\n            }}\n            QMenu {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                padding: 4px 0;\n                font-size: 10px;\n            }}\n            QMenu::item {{\n                padding: 4px 24px 4px 16px;\n            }}\n            QMenu::item:selected {{\n                background-color: {t["selected"]};\n            }}\n            QMenu::separator {{\n                height: 1px;\n                background-color: {t["border"]};\n                margin: 4px 8px;\n            }}\n\n            /* ==================== Tool Bar ==================== */\n            QToolBar {{\n                background-color: {t["surface"]};\n                border-bottom: 1px solid {t["border_light"]};\n                spacing: 4px;\n                padding: 4px 6px;\n            }}\n            QToolBar QToolButton {{\n                border-radius: 4px;\n                padding: 4px 8px;\n                font-size: 10px;\n            }}\n            QToolBar QToolButton:hover {{\n                background-color: {t["hover"]};\n            }}\n\n            /* ==================== Status Bar ==================== */\n            QStatusBar {{\n                background-color: {t["surface"]};\n                border-top: 1px solid {t["border_light"]};\n                padding: 2px 4px;\n                font-size: 10px;\n            }}\n\n            /* ==================== Progress Bar ==================== */\n            QProgressBar {{\n                background-color: {t["border_light"]};\n                border: none;\n                border-radius: 4px;\n                text-align: center;\n                font-size: 10px;\n                min-height: 14px;\n            }}\n            QProgressBar::chunk {{\n                background-color: {t["primary"]};\n                border-radius: 4px;\n            }}\n\n            /* ==================== Splitter ==================== */\n            QSplitter::handle {{\n                background-color: {t["border_light"]};\n            }}\n            QSplitter::handle:horizontal {{\n                width: 1px;\n            }}\n            QSplitter::handle:hover {{\n                background-color: {t["primary"]};\n            }}\n\n            /* ==================== Tooltip ==================== */\n            QToolTip {{\n                background-color: {t["surface"]};\n                border: 1px solid {t["border"]};\n                border-radius: 4px;\n                padding: 4px 8px;\n                color: {t["text"]};\n                font-size: 10px;\n            }}\n\n            /* ==================== Labels ==================== */\n            QLabel {{\n                font-size: 10px;\n            }}\n        '
        return get_ui_scale().scale_stylesheet(stylesheet)


_theme_manager: ThemeManager = None

def get_theme_manager() -> ThemeManager:
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme(widget: QWidget=None):
    manager = get_theme_manager()
    stylesheet = manager.get_stylesheet()
    if widget is None:
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
    else:
        widget.setStyleSheet(stylesheet)
