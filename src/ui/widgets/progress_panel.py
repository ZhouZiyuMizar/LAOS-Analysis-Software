# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\progress_panel.py
"""
Progress Panel - Compact progress display with time estimation
"""
from datetime import datetime, timedelta
from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from utils.i18n import tr
from utils.responsive import get_ui_scale

class EnhancedProgressPanel(QWidget):
    __doc__ = "\n    Compact progress panel with:\n    - Progress bar\n    - Time estimation\n    - Status message\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self._start_time = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._init_ui()
        get_ui_scale().register(self)
        self.apply_ui_scale()

    def apply_ui_scale(self):
        """Re-apply UI scale to fixed-size elements after a font change."""
        scale = get_ui_scale()
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setMinimumHeight(scale.scaled(14))
        if hasattr(self, 'file_label'):
            self.file_label.setMaximumHeight(scale.scaled(20))

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        self.progress_bar = QProgressBar()
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(get_ui_scale().scaled(14))
        self.progress_bar.setStyleSheet("\n            QProgressBar {\n                background-color: #E0E0E0;\n                border: none;\n                border-radius: 3px;\n                text-align: center;\n                color: #212121;\n            }\n            QProgressBar::chunk {\n                background: #2196F3;\n                border-radius: 3px;\n            }\n        ")
        layout.addWidget(self.progress_bar)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(4)
        self.status_label = QLabel(tr("Ready", "ProgressPanel"))
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setStyleSheet("color: gray;")
        info_layout.addWidget(self.status_label)
        self.time_label = QLabel("")
        self.time_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.time_label.setStyleSheet("color: gray;")
        info_layout.addWidget(self.time_label)
        layout.addLayout(info_layout)
        self.file_label = QLabel("")
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.file_label.setStyleSheet("color: #757575;")
        self.file_label.setWordWrap(True)
        self.file_label.setMaximumHeight(get_ui_scale().scaled(20))
        layout.addWidget(self.file_label)

    def start(self, message: str=''):
        self._start_time = datetime.now()
        self.progress_bar.setValue(0)
        self.time_label.setText(tr("Estimating...", "ProgressPanel"))
        if message:
            self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")

    def update(self, value: int, message: str='', filename: str=''):
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
        elif filename:
            self.file_label.setText(f"📄 {filename}")
        else:
            self.file_label.clear()
        if self._start_time and value > 0 and value < 100:
            elapsed = datetime.now() - self._start_time
            try:
                remaining = elapsed * (100 - value) / value
                self.time_label.setText(tr("ETA:", "ProgressPanel") + " " + self._format_time(remaining))
            except:
                self.time_label.setText(tr("Estimating...", "ProgressPanel"))

        else:
            if value >= 100:
                self.time_label.clear()
                self.file_label.clear()

    def finish(self, success: bool=True, message: str=''):
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText(message or tr("Done", "ProgressPanel"))
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.status_label.setText(message or tr("Failed", "ProgressPanel"))
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        self.time_label.clear()
        self.file_label.clear()
        self._start_time = None

    def reset(self):
        self.progress_bar.setValue(0)
        self.status_label.setText(tr("Ready", "ProgressPanel"))
        self.status_label.setStyleSheet("color: gray;")
        self.time_label.clear()
        self.file_label.clear()
        self._start_time = None

    def get_elapsed_time(self) -> Optional[timedelta]:
        if self._start_time:
            return datetime.now() - self._start_time
        return

    @staticmethod
    def _format_time(delta: timedelta) -> str:
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            return "--"
        if total_seconds < 60:
            return f"{total_seconds}s"
        if total_seconds < 3600:
            return f"{total_seconds // 60}m {total_seconds % 60}s"
        return f"{total_seconds // 3600}h {total_seconds % 3600 // 60}m"

    def _refresh_ui(self):
        """Refresh UI elements with new language"""
        self.status_label.setText(tr("Ready", "ProgressPanel"))
