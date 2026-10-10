# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\data_preview.py
"""
Data Preview Widget - Preview and statistics for data files
"""
import os, numpy as np
from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QGroupBox, QHeaderView
from PyQt5.QtCore import Qt
from utils.i18n import tr
from utils.responsive import get_ui_scale

class DataPreviewWidget(QWidget):
    __doc__ = "\n    Widget for previewing data files with:\n    - Table view of raw data\n    - Statistical summary\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file = ""
        self._current_data = None
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.file_label = QLabel(tr("No file loaded", "DataPreview"))
        self.file_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(self.file_label)
        self.tabs = QTabWidget()
        self.table = QTableWidget()
        self.tabs.addTab(self.table, tr("Table", "DataPreview"))
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        self.stats_label.setAlignment(Qt.AlignTop)
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        self.tabs.addTab(self.stats_widget, tr("Statistics", "DataPreview"))
        layout.addWidget(self.tabs)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.close_btn = QPushButton(tr("Close", "DataPreview"))
        self.close_btn.setMinimumWidth(get_ui_scale().scaled(80))
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

    def load_data(self, file_path: str, data: np.ndarray):
        """
        Load data into the preview widget

        Args:
            file_path: Path to the data file
            data: Numpy array with data columns
        """
        self._current_file = file_path
        self._current_data = data
        filename = os.path.basename(file_path)
        rows, cols = data.shape if len(data.shape) > 1 else (len(data), 1)
        self.file_label.setText(f"📄 {filename} ({rows} rows × {cols} cols)")
        self._populate_table(data)
        self._calculate_stats(data)
        self.tabs.setCurrentIndex(0)

    def _populate_table(self, data: np.ndarray):
        """Populate the table widget with data"""
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        rows, cols = data.shape
        max_rows = min(100, rows)
        self.table.setRowCount(max_rows)
        self.table.setColumnCount(cols)
        headers = [
         "Time", "Stress", "Strain", "Strain Rate"]
        self.table.setHorizontalHeaderLabels(headers[:cols])
        for row in range(max_rows):
            for col in range(cols):
                item = QTableWidgetItem((f"{data[(row, col)]:.6g}"))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
            else:
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                if rows > max_rows:
                    self.table.setMaximumHeight(300)

    def _calculate_stats(self, data: np.ndarray):
        """Calculate and display statistics"""
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        columns = [
         ('Time', 0),
         ('Stress', 1),
         ('Strain', 2),
         ('Strain Rate', 3)]
        stats_parts = []
        for name, col_idx in columns:
            if col_idx >= data.shape[1]:
                pass
            else:
                col_data = data[:, col_idx]
                min_val = np.min(col_data)
                max_val = np.max(col_data)
                mean_val = np.mean(col_data)
                std_val = np.std(col_data)
                median_val = np.median(col_data)
                stats_parts.append(f'\n<b>{name}</b>\n<table style="margin-left: 10px;">\n<tr><td>Min:</td><td style="text-align: right;">{min_val:.6g}</td></tr>\n<tr><td>Max:</td><td style="text-align: right;">{max_val:.6g}</td></tr>\n<tr><td>Mean:</td><td style="text-align: right;">{mean_val:.6g}</td></tr>\n<tr><td>Median:</td><td style="text-align: right;">{median_val:.6g}</td></tr>\n<tr><td>Std Dev:</td><td style="text-align: right;">{std_val:.6g}</td></tr>\n</table>\n')
        else:
            self.stats_label.setText("<hr>".join(stats_parts))

    def clear(self):
        """Clear the preview"""
        self._current_file = ""
        self._current_data = None
        self.file_label.setText(tr("No file loaded", "DataPreview"))
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.stats_label.clear()

    def get_current_file(self) -> str:
        """Get the currently loaded file path"""
        return self._current_file

    def get_current_data(self) -> Optional[np.ndarray]:
        """Get the currently loaded data"""
        return self._current_data


class DataPreviewDialog(QWidget):
    __doc__ = "\n    Standalone dialog-style widget for data preview\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Data Preview", "DataPreview"))
        self.setMinimumSize(get_ui_scale().scaled(500), get_ui_scale().scaled(400))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        self.preview_widget = DataPreviewWidget()
        layout.addWidget(self.preview_widget)
        self.preview_widget.close_btn.clicked.connect(self.hide)

    def show_data(self, file_path: str, data: np.ndarray):
        """
        Show data preview

        Args:
            file_path: Path to the data file
            data: Numpy array with data
        """
        self.preview_widget.load_data(file_path, data)
        self.show()
        self.raise_()
        self.activateWindow()
