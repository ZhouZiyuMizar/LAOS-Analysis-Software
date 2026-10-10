# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\file_selector.py
"""
FileSelector Widget - Responsive file selection widget
"""
import os
from typing import List, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QGroupBox, QCheckBox, QMessageBox, QMenu, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QKeyEvent, QColor
from utils.i18n import tr
from utils.responsive import get_ui_scale

class FileListWidget(QListWidget):
    __doc__ = "Custom QListWidget with keyboard navigation signals"
    navigate = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_emitted_row = -1
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown,
         Qt.Key_Home, Qt.Key_End):
            current_row = self.currentRow()
            if current_row != self._last_emitted_row:
                self._last_emitted_row = current_row
                self.navigate.emit(current_row)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        current_row = self.currentRow()
        if current_row != self._last_emitted_row:
            self._last_emitted_row = current_row
            self.navigate.emit(current_row)


class FileSelector(QWidget):
    __doc__ = "\n    Responsive file selection widget with adaptive layout\n    "
    STATUS_RAW = "raw"
    STATUS_PROCESSED = "processed"
    STATUS_ERROR = "error"
    STATUS_ICONS = {STATUS_RAW: "○", STATUS_PROCESSED: "✓", STATUS_ERROR: "⚠"}
    STATUS_COLORS = {STATUS_RAW: "#9E9E9E", STATUS_PROCESSED: "#4CAF50", STATUS_ERROR: "#F44336"}
    folder_changed = pyqtSignal(str)
    file_selected = pyqtSignal(int)
    files_selected = pyqtSignal(list)
    plot_requested = pyqtSignal(list)
    preview_requested = pyqtSignal(int)
    double_click_plot = pyqtSignal(int)
    batch_plot_requested = pyqtSignal(str, list)
    keyboard_navigate = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._folder_path = ""
        self._file_list = []
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._init_ui()
        get_ui_scale().register(self)

    def apply_ui_scale(self):
        """Re-apply UI scale after a font change."""
        if hasattr(self, 'info_label'):
            color = getattr(self, '_info_color', 'gray')
            self.info_label.setStyleSheet(f"color: {color};")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if os.path.isdir(url.toLocalFile()):
                    event.acceptProposedAction()
                    return None

        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.set_folder_path(path)
                event.acceptProposedAction()
                return None
        else:
            event.ignore()

    def _init_ui(self):
        """Initialize responsive UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)
        folder_group = QGroupBox(tr("Folder", "FileSelector"))
        folder_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        folder_layout = QHBoxLayout(folder_group)
        folder_layout.setSpacing(3)
        self.path_edit = QLineEdit()
        self.path_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.path_edit.setPlaceholderText(tr("Select...", "FileSelector"))
        self.path_edit.setReadOnly(True)
        folder_layout.addWidget(self.path_edit)
        self.browse_btn = QPushButton("...")
        self.browse_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.browse_btn.setToolTip(tr("Browse folder", "FileSelector"))
        self.browse_btn.clicked.connect(self._on_browse)
        folder_layout.addWidget(self.browse_btn)
        layout.addWidget(folder_group)
        list_group = QGroupBox(tr("Files", "FileSelector"))
        list_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list_layout = QVBoxLayout(list_group)
        list_layout.setSpacing(3)
        self.file_list = FileListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.file_list.itemDoubleClicked.connect(self._on_double_click)
        self.file_list.navigate.connect(self._on_keyboard_navigate)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_context_menu)
        list_layout.addWidget((self.file_list), stretch=1)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(2)
        self.select_all_btn = QPushButton(tr("All", "FileSelector"))
        self.select_all_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.select_all_btn.setToolTip(tr("Select all", "FileSelector"))
        self.select_all_btn.clicked.connect(self._select_all)
        control_layout.addWidget(self.select_all_btn)
        self.deselect_all_btn = QPushButton(tr("None", "FileSelector"))
        self.deselect_all_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.deselect_all_btn.setToolTip(tr("Deselect all", "FileSelector"))
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        control_layout.addWidget(self.deselect_all_btn)
        control_layout.addStretch()
        list_layout.addLayout(control_layout)
        self.info_label = QLabel(tr("No files", "FileSelector"))
        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._info_color = "gray"
        self.info_label.setStyleSheet("color: gray;")
        list_layout.addWidget(self.info_label)
        layout.addWidget(list_group, stretch=1)

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, tr("Select Folder", "FileSelector"), self._folder_path or os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
        if folder:
            self.set_folder_path(folder)

    def set_folder_path(self, folder_path: str):
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", f"Folder does not exist:\n{folder_path}")
            return
        self._folder_path = folder_path
        self.path_edit.setText(folder_path)
        self._load_files()
        self.folder_changed.emit(folder_path)

    def _load_files(self):
        self.file_list.clear()
        self._file_list = []
        if not self._folder_path:
            return
        processed_dir = os.path.join(self._folder_path, "fourier_coefficients")
        has_processed_data = os.path.exists(processed_dir)
        numbered_files = []
        for filename in os.listdir(self._folder_path):
            if filename.endswith(".txt") and filename.replace(".txt", "").isdigit():
                numbered_files.append(filename)
        else:
            numbered_files.sort(key=(lambda x: int(x.replace(".txt", ""))))

        for filename in numbered_files:
            file_path = os.path.join(self._folder_path, filename)
            try:
                file_size = os.path.getsize(file_path)
                size_str = self._format_file_size(file_size)
            except OSError:
                size_str = "?"
            else:
                status = self._get_file_status(filename, has_processed_data)
                icon = self.STATUS_ICONS.get(status, "○")
                color = self.STATUS_COLORS.get(status, "#9E9E9E")
                item = QListWidgetItem(f"{icon} {filename} ({size_str})")
                item.setData(Qt.UserRole, filename)
                item.setData(Qt.UserRole + 1, file_path)
                item.setData(Qt.UserRole + 2, status)
                item.setForeground(QColor(color))
                status_text = {(self.STATUS_RAW): (tr("Raw", "FileSelector")), 
                 (self.STATUS_PROCESSED): (tr("Processed", "FileSelector")), 
                 (self.STATUS_ERROR): (tr("Error", "FileSelector"))}.get(status, "")
                item.setToolTip(f"{filename}\n{size_str}\n{status_text}")
                self.file_list.addItem(item)
                self._file_list.append(file_path)
        else:
            file_count = len(numbered_files)
            if file_count > 0:
                processed_count = sum((1 for i in range(self.file_list.count()) if self.file_list.item(i).data(Qt.UserRole + 2) == self.STATUS_PROCESSED))
                self.info_label.setText(f"{file_count} files ({processed_count} done)")
                self._info_color = "#4CAF50"
                self.info_label.setStyleSheet("color: #4CAF50;")
            else:
                self.info_label.setText(tr("No numbered txt files", "FileSelector"))
                self._info_color = "#F44336"
                self.info_label.setStyleSheet("color: #F44336;")

    def _get_file_status(self, filename: str, has_processed_data: bool) -> str:
        if not has_processed_data:
            return self.STATUS_RAW
        fourier_path = os.path.join(self._folder_path, "fourier_coefficients", filename)
        if os.path.exists(fourier_path):
            return self.STATUS_PROCESSED
        return self.STATUS_RAW

    @staticmethod
    def _format_file_size(size: int) -> str:
        for unit in ('B', 'KB', 'MB'):
            if size < 1024:
                return f"{size:.0f}{unit}"
            size /= 1024
        else:
            return f"{size:.1f}GB"

    def _on_selection_changed(self):
        selected_items = self.file_list.selectedItems()
        indices = [self.file_list.row(item) for item in selected_items]
        if len(indices) == 1:
            self.file_selected.emit(indices[0])
        else:
            if len(indices) > 1:
                self.files_selected.emit(indices)

    def _on_double_click(self, item: QListWidgetItem):
        self.double_click_plot.emit(self.file_list.row(item))

    def _on_keyboard_navigate(self, index: int):
        self.keyboard_navigate.emit(index)

    def _select_all(self):
        self.file_list.selectAll()

    def _deselect_all(self):
        self.file_list.clearSelection()

    def _show_context_menu(self, position):
        menu = QMenu(self)
        selected_items = self.file_list.selectedItems()
        selected_count = len(selected_items)
        if selected_count > 0:
            if selected_count == 1:
                plot_action = menu.addAction(tr("Plot", "FileSelector"))
                plot_action.triggered.connect(self._on_plot_selected)
                preview_action = menu.addAction(tr("Preview", "FileSelector"))
                preview_action.triggered.connect(self._on_preview_file)
            else:
                plot_submenu = menu.addMenu(tr("Batch", "FileSelector"))
                overlay_action = plot_submenu.addAction(tr("Overlay", "FileSelector"))
                overlay_action.triggered.connect(lambda: self._on_batch_plot("3"))
                individual_action = plot_submenu.addAction(tr("Individual", "FileSelector"))
                individual_action.triggered.connect(lambda: self._on_batch_plot("individual"))
            menu.addSeparator()
        select_all_action = menu.addAction(tr("All", "FileSelector"))
        select_all_action.triggered.connect(self._select_all)
        deselect_action = menu.addAction(tr("None", "FileSelector"))
        deselect_action.triggered.connect(self._deselect_all)
        menu.addSeparator()
        refresh_action = menu.addAction(tr("Refresh", "FileSelector"))
        refresh_action.triggered.connect(self._refresh_file_list)
        menu.exec_(self.file_list.viewport().mapToGlobal(position))

    def _on_batch_plot(self, plot_type: str):
        indices = self.get_selected_indices()
        if indices:
            self.batch_plot_requested.emit(plot_type, indices)

    def _on_plot_selected(self):
        indices = self.get_selected_indices()
        if indices:
            self.plot_requested.emit(indices)

    def _on_preview_file(self):
        indices = self.get_selected_indices()
        if len(indices) == 1:
            self.preview_requested.emit(indices[0])

    def _refresh_file_list(self):
        if self._folder_path:
            self._load_files()

    def get_folder_path(self) -> str:
        return self._folder_path

    def get_selected_indices(self) -> List[int]:
        return [self.file_list.row(item) for item in self.file_list.selectedItems()]

    def get_selected_files(self) -> List[str]:
        return [self._file_list[i] for i in self.get_selected_indices() if i < len(self._file_list)]

    def get_file_count(self) -> int:
        return len(self._file_list)

    def get_file_path(self, index: int) -> Optional[str]:
        if 0 <= index < len(self._file_list):
            return self._file_list[index]

    def clear(self):
        self.file_list.clear()
        self._file_list = []
        self._folder_path = ""
        self.path_edit.clear()
        self.info_label.setText(tr("No files", "FileSelector"))
        self._info_color = "gray"
        self.info_label.setStyleSheet("color: gray;")

    def _refresh_ui(self):
        """Refresh UI elements with new language"""
        for child in self.children():
            if isinstance(child, QGroupBox):
                title = child.title()
                if "Folder" in title or "文件夹" in title:
                    child.setTitle(tr("Folder", "FileSelector"))
                elif "Files" in title or "文件" in title:
                    child.setTitle(tr("Files", "FileSelector"))
        
        self.browse_btn.setToolTip(tr("Browse folder", "FileSelector"))
        self.select_all_btn.setText(tr("All", "FileSelector"))
        self.select_all_btn.setToolTip(tr("Select all", "FileSelector"))
        self.deselect_all_btn.setText(tr("None", "FileSelector"))
        self.deselect_all_btn.setToolTip(tr("Deselect all", "FileSelector"))
        if not self._file_list:
            self.info_label.setText(tr("No files", "FileSelector"))
