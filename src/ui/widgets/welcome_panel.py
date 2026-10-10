# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\welcome_panel.py
"""
Welcome Panel - Empty state guidance for ChemicalStrain GUI
"""
import os, sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from utils.i18n import tr
from utils.responsive import get_ui_scale

def get_app_path():
    """Get application path (works for both source and packaged exe)"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WelcomePanel(QWidget):
    __doc__ = "\n    Welcome panel shown when no folder is loaded\n    Provides quick start guidance for new users\n    "
    open_folder_clicked = pyqtSignal()
    tutorial_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        get_ui_scale().register(self)

    def apply_ui_scale(self):
        """Re-apply UI scale to fixed-size elements after a font change."""
        scale = get_ui_scale()
        if hasattr(self, 'quick_start_frame'):
            self.quick_start_frame.setMinimumWidth(scale.scaled(500))
        if hasattr(self, 'num_labels'):
            for label in self.num_labels:
                label.setFixedWidth(scale.scaled(20))
        for attr in ('open_btn', 'tutorial_btn'):
            btn = getattr(self, attr, None)
            if btn is not None:
                btn.setFixedHeight(scale.scaled(36))
                btn.setMinimumWidth(scale.scaled(130))

    def _init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setSpacing(get_ui_scale().scaled(10))
        logo_path_png = os.path.join(get_app_path(), "resources", "icons", "logo1.png")
        logo_path_svg = os.path.join(get_app_path(), "resources", "icons", "logo.svg")
        print(f"[DEBUG WelcomePanel] App path: {get_app_path()}")
        print(f"[DEBUG WelcomePanel] Logo PNG path: {logo_path_png}")
        print(f"[DEBUG WelcomePanel] Logo PNG exists: {os.path.exists(logo_path_png)}")
        logo_label = QLabel()
        logo_size = get_ui_scale().scaled(200)
        if os.path.exists(logo_path_png):
            pixmap = QPixmap(logo_path_png)
            print(f"[DEBUG WelcomePanel] PNG pixmap size: {pixmap.width()}x{pixmap.height()}, null: {pixmap.isNull()}")
            pixmap = pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
            layout.addSpacing(get_ui_scale().scaled(10))
        else:
            if os.path.exists(logo_path_svg):
                pixmap = QPixmap(logo_path_svg)
                pixmap = pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_label)
                layout.addSpacing(get_ui_scale().scaled(10))
            else:
                print("[DEBUG WelcomePanel] No logo found!")
                placeholder = QLabel("LAOS Analysis")
                placeholder.setStyleSheet(f"font-size: {get_ui_scale().scaled(36)}px; font-weight: bold; color: #2196F3;")
                placeholder.setAlignment(Qt.AlignCenter)
                layout.addWidget(placeholder)
                layout.addSpacing(get_ui_scale().scaled(10))
        title_label = QLabel("LAOS Analysis")
        title_font = QFont()
        title_font.setPointSize(get_ui_scale().scaled(24))
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(title_label)
        self.subtitle = QLabel(tr("LAOS Data Analysis Tool", "WelcomePanel"))
        subtitle_font = QFont()
        subtitle_font.setPointSize(get_ui_scale().scaled(12))
        self.subtitle.setFont(subtitle_font)
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: #757575;")
        layout.addWidget(self.subtitle)
        layout.addSpacing(get_ui_scale().scaled(15))
        quick_start_frame = QFrame()
        quick_start_frame.setStyleSheet("\n            QFrame {\n                background-color: #FAFAFA;\n                border: 1px solid #E0E0E0;\n                border-radius: 8px;\n                padding: 15px;\n            }\n        ")
        quick_start_frame.setMinimumWidth(get_ui_scale().scaled(500))
        self.quick_start_frame = quick_start_frame
        quick_start_layout = QVBoxLayout(quick_start_frame)
        quick_start_layout.setSpacing(get_ui_scale().scaled(8))
        self.qs_title = QLabel(tr("Quick Start", "WelcomePanel"))
        self.qs_title.setStyleSheet(f"font-weight: bold; font-size: {get_ui_scale().scaled(14)}px; color: #424242;")
        quick_start_layout.addWidget(self.qs_title)
        self.step_labels = []
        self.num_labels = []
        steps = [
         (
          "1.", tr("Open a data folder containing numbered .txt files", "WelcomePanel"), "Ctrl+O"),
         (
          "2.", tr("Run preprocessing to prepare data for analysis", "WelcomePanel"), "F5"),
         (
          "3.", tr("Select a file and choose plot type to visualize", "WelcomePanel"), "Double-click")]
        for num, text, shortcut in steps:
            step_layout = QHBoxLayout()
            step_layout.setSpacing(get_ui_scale().scaled(10))
            num_label = QLabel(num)
            num_label.setStyleSheet(f"color: #2196F3; font-weight: bold; font-size: {get_ui_scale().scaled(13)}px;")
            num_label.setFixedWidth(get_ui_scale().scaled(20))
            self.num_labels.append(num_label)
            step_layout.addWidget(num_label)
            text_label = QLabel(text)
            text_label.setStyleSheet(f"color: #424242; font-size: {get_ui_scale().scaled(13)}px;")
            text_label.setWordWrap(True)
            step_layout.addWidget(text_label, 1)
            self.step_labels.append(text_label)
            shortcut_label = QLabel(shortcut)
            shortcut_label.setStyleSheet(f"color: #9E9E9E; font-size: {get_ui_scale().scaled(10)}px;")
            step_layout.addWidget(shortcut_label)
            quick_start_layout.addLayout(step_layout)
        layout.addWidget(quick_start_frame)
        layout.addSpacing(get_ui_scale().scaled(15))
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(get_ui_scale().scaled(10))
        self.open_btn = QPushButton(tr("Open Folder", "WelcomePanel"))
        self.open_btn.setFixedHeight(get_ui_scale().scaled(36))
        self.open_btn.setMinimumWidth(get_ui_scale().scaled(130))
        self.open_btn.setStyleSheet(f"\n            QPushButton {{\n                background-color: #2196F3;\n                color: white;\n                border: none;\n                border-radius: 4px;\n                font-size: {get_ui_scale().scaled(13)}px;\n                font-weight: bold;\n            }}\n            QPushButton:hover {{\n                background-color: #1976D2;\n            }}\n        ")
        self.open_btn.clicked.connect(self.open_folder_clicked.emit)
        btn_layout.addWidget(self.open_btn)
        self.tutorial_btn = QPushButton(tr("View Tutorial", "WelcomePanel"))
        self.tutorial_btn.setFixedHeight(get_ui_scale().scaled(36))
        self.tutorial_btn.setMinimumWidth(get_ui_scale().scaled(130))
        self.tutorial_btn.setStyleSheet(f"\n            QPushButton {{\n                background-color: white;\n                color: #2196F3;\n                border: 2px solid #2196F3;\n                border-radius: 4px;\n                font-size: {get_ui_scale().scaled(13)}px;\n            }}\n            QPushButton:hover {{\n                background-color: #E3F2FD;\n            }}\n        ")
        self.tutorial_btn.clicked.connect(self.tutorial_clicked.emit)
        btn_layout.addWidget(self.tutorial_btn)
        layout.addLayout(btn_layout)
        layout.addSpacing(get_ui_scale().scaled(10))
        self.formats_label = QLabel(tr("Supported data formats: Numbered .txt files (0.txt, 1.txt, ...)", "WelcomePanel"))
        self.formats_label.setStyleSheet(f"color: #9E9E9E; font-size: {get_ui_scale().scaled(10)}px;")
        self.formats_label.setAlignment(Qt.AlignCenter)
        self.formats_label.setWordWrap(True)
        layout.addWidget(self.formats_label)
        layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _refresh_ui(self):
        """Refresh UI elements with new language translations"""
        self.subtitle.setText(tr("LAOS Data Analysis Tool", "WelcomePanel"))
        self.qs_title.setText(tr("Quick Start", "WelcomePanel"))
        step_texts = [
            tr("Open a data folder containing numbered .txt files", "WelcomePanel"),
            tr("Run preprocessing to prepare data for analysis", "WelcomePanel"),
            tr("Select a file and choose plot type to visualize", "WelcomePanel")
        ]
        for i, label in enumerate(self.step_labels):
            if i < len(step_texts):
                label.setText(step_texts[i])
        self.open_btn.setText(tr("Open Folder", "WelcomePanel"))
        self.tutorial_btn.setText(tr("View Tutorial", "WelcomePanel"))
        self.formats_label.setText(tr("Supported data formats: Numbered .txt files (0.txt, 1.txt, ...)", "WelcomePanel"))


class EmptyStateWidget(QWidget):
    __doc__ = "\n    Widget that shows different states based on application state\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.welcome_panel = WelcomePanel()
        layout.addWidget(self.welcome_panel)

    def show_welcome(self):
        """Show the welcome panel"""
        self.welcome_panel.show()

    def hide_welcome(self):
        """Hide the welcome panel"""
        self.welcome_panel.hide()