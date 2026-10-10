# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\history_panel.py
"""
History Panel - Operation history and quick redo functionality
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QGroupBox, QMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.i18n import tr
from utils.responsive import get_ui_scale

class HistoryItem:
    __doc__ = "Represents a single operation history item"

    def __init__(self, operation_type: str, params: Dict[(str, Any)], description: str):
        self.operation_type = operation_type
        self.params = params
        self.description = description
        self.timestamp = datetime.now()

    def to_display_string(self) -> str:
        """Generate display string for the history list"""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] {self.description}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {'operation_type':self.operation_type, 
         'params':self.params, 
         'description':self.description, 
         'timestamp':(self.timestamp.isoformat)()}


class OperationHistory:
    __doc__ = "\n    Manages operation history with undo/redo capability\n    "
    MAX_HISTORY = 50

    def __init__(self):
        self._history = []

    def add(self, operation_type: str, params: Dict[(str, Any)], description: str):
        """
        Add an operation to history

        Args:
            operation_type: Type of operation (e.g., 'plot', 'preprocess')
            params: Parameters used for the operation
            description: Human-readable description
        """
        item = HistoryItem(operation_type, params, description)
        self._history.append(item)
        if len(self._history) > self.MAX_HISTORY:
            self._history.pop(0)

    def get_recent(self, count: int=10) -> List[HistoryItem]:
        """Get recent history items"""
        return self._history[(-count)[:None]]

    def get_all(self) -> List[HistoryItem]:
        """Get all history items"""
        return self._history.copy()

    def clear(self):
        """Clear all history"""
        self._history.clear()

    def get_last_plot(self) -> Optional[HistoryItem]:
        """Get the most recent plot operation"""
        for item in reversed(self._history):
            if item.operation_type == "plot":
                return item
            return


class HistoryPanel(QWidget):
    __doc__ = "\n    Panel displaying operation history with quick redo functionality\n    "
    redo_requested = pyqtSignal(str, dict)
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = OperationHistory()
        self._init_ui()
        get_ui_scale().register(self)

    def apply_ui_scale(self):
        """Re-apply UI scale to fixed-size elements after a font change."""
        if hasattr(self, 'redo_btn'):
            self.redo_btn.setMinimumWidth(get_ui_scale().scaled(80))

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        header_layout = QHBoxLayout()
        title_label = QLabel(tr("History", "HistoryPanel"))
        title_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.redo_btn = QPushButton(tr("Redo Last", "HistoryPanel"))
        self.redo_btn.setMinimumWidth(get_ui_scale().scaled(80))
        self.redo_btn.setEnabled(False)
        self.redo_btn.clicked.connect(self._on_redo_last)
        header_layout.addWidget(self.redo_btn)
        layout.addLayout(header_layout)
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self._show_context_menu)
        self.history_list.itemDoubleClicked.connect(self._on_item_double_click)
        layout.addWidget(self.history_list)
        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton(tr("Clear", "HistoryPanel"))
        self.clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def add_operation(self, operation_type: str, params: Dict[(str, Any)], description: str):
        """
        Add an operation to history

        Args:
            operation_type: Type of operation
            params: Operation parameters
            description: Human-readable description
        """
        self._history.add(operation_type, params, description)
        self._refresh_list()
        self.redo_btn.setEnabled(True)

    def _refresh_list(self):
        """Refresh the history list display"""
        self.history_list.clear()
        for item in reversed(self._history.get_all()):
            list_item = QListWidgetItem(item.to_display_string())
            list_item.setData(Qt.UserRole, item)
            if item.operation_type == "plot":
                list_item.setForeground(Qt.blue)
            else:
                if item.operation_type == "preprocess":
                    list_item.setForeground(Qt.darkGreen)
            self.history_list.addItem(list_item)

    def _on_redo_last(self):
        """Redo the last operation"""
        last_plot = self._history.get_last_plot()
        if last_plot:
            self.redo_requested.emit(last_plot.operation_type, last_plot.params)

    def _on_item_double_click(self, item: QListWidgetItem):
        """Handle double-click on history item"""
        history_item = item.data(Qt.UserRole)
        if history_item:
            self.redo_requested.emit(history_item.operation_type, history_item.params)

    def _show_context_menu(self, position):
        """Show context menu for history item"""
        item = self.history_list.itemAt(position)
        if not item:
            return
        menu = QMenu(self)
        redo_action = menu.addAction(tr("Redo", "HistoryPanel"))
        redo_action.triggered.connect(lambda: self._on_item_double_click(item))
        menu.addSeparator()
        copy_params = menu.addAction(tr("Copy Parameters", "HistoryPanel"))
        copy_params.triggered.connect(lambda: self._copy_params(item))
        menu.exec_(self.history_list.viewport().mapToGlobal(position))

    def _copy_params(self, item: QListWidgetItem):
        """Copy parameters to clipboard"""
        history_item = item.data(Qt.UserRole)
        if history_item:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(str(history_item.params))

    def _on_clear(self):
        """Clear history"""
        self._history.clear()
        self.history_list.clear()
        self.redo_btn.setEnabled(False)
        self.clear_requested.emit()

    def get_history(self) -> OperationHistory:
        """Get the history manager"""
        return self._history
