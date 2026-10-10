# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\widgets\control_panel.py
"""
ControlPanel Widget - PyQt5 widget for controlling data processing and plotting
"""
from typing import Optional, List, Dict
import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QPushButton, QComboBox, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QProgressBar, QCheckBox, QMessageBox, QFrame, QSplitter, QMenu, QToolButton, QAction, QDialog, QDialogButtonBox, QTextEdit, QScrollArea, QSizePolicy, QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QImage, QPixmap
from utils.config import Config
from utils.i18n import tr
from utils.responsive import get_ui_scale
from ui.widgets.progress_panel import EnhancedProgressPanel
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
PLOT_PARAM_MAP = {
    '1': ["file_index"],
    '3a': ["files_edit"],
    '3b': ["files_edit", "use_normalized"],
    '3c': ["files_edit", "use_normalized"],
    '4': [],
    '5': ["files_edit", "max_harmonic"],
    '6': ["harmonics"],
    '6q': [],
    '7a': ["file_index", "harmonics", "data_range"],
    '7d': ["file_index", "harmonics", "data_range"],
    '7b': ["files_edit", "harmonics", "data_range"],
    '7c': ["file_index", "harmonics", "data_range", "decomp_component"],
    '8': ["show_bifurcation"],
    '9': [],
    '10a': [],
    '10b': []
}

def get_lissajous_subtypes():
        return [
            ("3a", tr("3D Lissajous", "LissajousSubtypes")),
            ("3b", tr("2D Elastic (σ-γ)", "LissajousSubtypes")),
            ("3c", tr("2D Viscous (σ-γ̇)", "LissajousSubtypes")),
        ]


def get_param_tooltips():
    return {'file_index':tr("File index to plot (starting from 0)", "ParamTooltips"), 
     'files_edit':tr("Overlay file indices, comma-separated (e.g., 030,120,150)", "ParamTooltips"), 
     'harmonics':tr("Fourier harmonics number (1-50)", "ParamTooltips"), 
     'omega':tr("Angular frequency ω = n×π (rad/s), default 2π", "ParamTooltips"), 
     'omega_unit':tr("Frequency unit: rad/s or Hz", "ParamTooltips"), 
     'data_range':tr("Select data range for plotting", "ParamTooltips"), 
     'show_bifurcation':tr("Mark bifurcation points and display stress values on the plot", "ParamTooltips")}


LISSAJOUS_SUBTYPES = [
    ('3a', '3D李萨如'),
    ('3b', '2D弹性 (σ-γ)'),
    ('3c', '2D粘性 (σ-γ̇)')]
PARAM_TOOLTIPS = {
 'file_index': '"要绘制的文件索引（从0开始）"', 
 'files_edit': '"叠加文件索引，逗号分隔（如 030,120,150）"', 
 'harmonics': '"傅里叶谐波数（1-50）"', 
 'omega': '"角频率 ω = n×π (rad/s)，默认2π"', 
 'omega_unit': '"频率单位：rad/s 或 Hz"', 
 'data_range': '"选择用于绘图的数据范围"'}

class ControlPanel(QWidget):
    __doc__ = "\n    Control panel widget with preprocessing controls, plot type selection,\n    and parameter inputs\n    "
    run_preprocess = pyqtSignal()
    run_step = pyqtSignal(str)
    plot_requested = pyqtSignal(str, dict)
    cancel_requested = pyqtSignal()
    instrument_changed = pyqtSignal(str)
    ta_excel_requested = pyqtSignal()
    log_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._preprocessed_frequency = None
        self._init_ui()
        get_ui_scale().register(self)
        self.apply_ui_scale()

    def apply_ui_scale(self):
        """Re-apply UI scale to fixed-size elements after a font change."""
        scale = get_ui_scale()
        if hasattr(self, 'colormap_preview_label'):
            self.colormap_preview_label.setFixedHeight(scale.scaled(30))
        self._update_colormap_preview(self.colormap_combo.currentData())

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self._create_preprocess_group()
        layout.addWidget(self.preprocess_group)
        self._create_plot_group()
        layout.addWidget(self.plot_group)
        self._create_colormap_group()
        layout.addWidget(self.colormap_group)
        self._create_params_group()
        layout.addWidget(self.params_group)
        self._create_progress_group()
        layout.addWidget(self.progress_group)
        self._update_params_visibility(self.plot_type_combo.currentData())
        layout.addStretch()

    def _create_preprocess_group(self):
        """Create preprocessing controls group with instrument selection"""
        self.preprocess_group = QGroupBox(tr("Preprocessing", "ControlPanel"))
        layout = QVBoxLayout(self.preprocess_group)
        instrument_layout = QHBoxLayout()
        self.instrument_label = QLabel(tr("Instrument Type:", "ControlPanel"))
        instrument_layout.addWidget(self.instrument_label)
        self.instrument_combo = QComboBox()
        self.instrument_combo.addItem("Thermo HAAKE", "haake")
        self.instrument_combo.addItem("TA Instruments", "ta")
        self.instrument_combo.setToolTip(tr("Select the instrument type for data source", "ControlPanel"))
        self.instrument_combo.currentIndexChanged.connect(self._on_instrument_changed)
        instrument_layout.addWidget(self.instrument_combo)
        layout.addLayout(instrument_layout)
        self.full_preprocess_btn = QPushButton("▶ " + tr("Run Full Preprocess", "ControlPanel"))
        self.full_preprocess_btn.setStyleSheet("\n            QPushButton {\n                background-color: #4CAF50;\n                color: white;\n                font-weight: bold;\n                padding: 8px;\n                border-radius: 4px;\n            }\n            QPushButton:hover {\n                background-color: #45a049;\n            }\n        ")
        self.full_preprocess_btn.clicked.connect(self._on_full_preprocess)
        layout.addWidget(self.full_preprocess_btn)
        self.ta_excel_btn = QPushButton("▶ " + tr("Process TA Excel", "ControlPanel"))
        self.ta_excel_btn.setStyleSheet("\n            QPushButton {\n                background-color: #2196F3;\n                color: white;\n                font-weight: bold;\n                padding: 8px;\n                border-radius: 4px;\n            }\n            QPushButton:hover {\n                background-color: #1976D2;\n            }\n        ")
        self.ta_excel_btn.clicked.connect(self._on_ta_excel_process)
        self.ta_excel_btn.setVisible(False)
        layout.addWidget(self.ta_excel_btn)
        
        self.frequency_display_label = QLabel(tr("Frequency: -- Hz", "ControlPanel"))
        self.frequency_display_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.frequency_display_label.setVisible(False)
        layout.addWidget(self.frequency_display_label)

    def _on_instrument_changed(self, index):
        """Handle instrument type change"""
        instrument_type = self.instrument_combo.currentData()
        self.instrument_changed.emit(instrument_type)
        if instrument_type == "ta":
            self.full_preprocess_btn.setVisible(False)
            self.ta_excel_btn.setVisible(True)
        else:
            self.full_preprocess_btn.setVisible(True)
            self.ta_excel_btn.setVisible(False)

    def _on_ta_excel_process(self):
        """Handle TA Excel processing request"""
        self.ta_excel_requested.emit()

    def get_instrument_type(self) -> str:
        """Get current instrument type selection"""
        return self.instrument_combo.currentData()

    def _create_plot_group(self):
        """Create plot selection group with hierarchical menus for SPP and Contact Stress"""
        self.plot_group = QGroupBox(tr("Plot", "ControlPanel"))
        layout = QVBoxLayout(self.plot_group)
        type_layout = QHBoxLayout()
        self.plot_type_label = QLabel(tr("Plot Type:", "ControlPanel"))
        type_layout.addWidget(self.plot_type_label)
        self.plot_type_combo = QComboBox()
        plot_types = [
         (
          "1", tr("Lissajous Curve", "PlotTypes")),
         (
          "3_menu", tr("Lissajous Overlay", "PlotTypes")),
         (
          "9", tr("Dissipation Rate", "PlotTypes")),
         (
          "6_menu", tr("Single-Order Fourier Coefficients", "PlotTypes")),
         (
          "5", tr("Multi-Order Fourier Coefficients", "PlotTypes")),
         (
          "4", tr("S-T Values", "PlotTypes")),
         (
          "8", tr("Stress Bifurcation", "PlotTypes")),
         (
          "7_menu", tr("SPP Method", "PlotTypes")),
         (
          "10_menu", tr("Cage Modulus", "PlotTypes"))]
        for code, name in plot_types:
            self.plot_type_combo.addItem(name, code)
        else:
            self.plot_type_combo.currentIndexChanged.connect(self._on_plot_type_changed)
            type_layout.addWidget(self.plot_type_combo)
            self.lissajous_combo = QComboBox()
            self.lissajous_combo.setVisible(False)
            for code, name in get_lissajous_subtypes():
                self.lissajous_combo.addItem(name, code)
            else:
                self.lissajous_combo.currentIndexChanged.connect(self._on_lissajous_subtype_changed)
                type_layout.addWidget(self.lissajous_combo)
                self.fourier_single_combo = QComboBox()
                self.fourier_single_combo.setVisible(False)
                fourier_single_subtypes = [
                 ("6", tr("In/I1 Ratio", "FourierSingleSubtypes")),
                 ("6q", tr("Q Value", "FourierSingleSubtypes"))]
                for code, name in fourier_single_subtypes:
                    self.fourier_single_combo.addItem(name, code)
                else:
                    self.fourier_single_combo.currentIndexChanged.connect(self._on_fourier_single_subtype_changed)
                    type_layout.addWidget(self.fourier_single_combo)
                    self.spp_combo = QComboBox()
                    self.spp_combo.setVisible(False)
                    spp_subtypes = [
                     ("7a", tr("SPP-Fourier Calculation", "SPPSubtypes")),
                     ("7d", tr("SPP-Derivative Calculation", "SPPSubtypes")),
                     ("7b", tr("Multi-File Overlay", "SPPSubtypes")),
                     ("7c", tr("Circular Decomposition", "SPPSubtypes"))]
                    for code, name in spp_subtypes:
                        self.spp_combo.addItem(name, code)
                    else:
                        self.spp_combo.currentIndexChanged.connect(self._on_spp_subtype_changed)
                        type_layout.addWidget(self.spp_combo)
                        self.cage_modulus_combo = QComboBox()
                        self.cage_modulus_combo.setVisible(False)
                        cage_subtypes = [
                         ("10a", tr("G'/G_cage vs Strain", "CageSubtypes")),
                         ("10b", tr("G_cage vs Strain", "CageSubtypes"))]
                        for code, name in cage_subtypes:
                            self.cage_modulus_combo.addItem(name, code)
                        else:
                            self.cage_modulus_combo.currentIndexChanged.connect(self._on_cage_modulus_subtype_changed)
                            type_layout.addWidget(self.cage_modulus_combo)
                            layout.addLayout(type_layout)
                            self.plot_btn = QPushButton(tr("Plot", "ControlPanel"))
                            self.plot_btn.setStyleSheet("\n            QPushButton {\n                background-color: #2196F3;\n                color: white;\n                font-weight: bold;\n                padding: 8px;\n                border-radius: 4px;\n            }\n            QPushButton:hover {\n                background-color: #1976D2;\n            }\n        ")
                            self.plot_btn.clicked.connect(self._on_plot)
                            layout.addWidget(self.plot_btn)

    def _create_colormap_group(self):
        """Create colormap selection group with preview"""
        self.colormap_group = QGroupBox(tr("Colormap", "ControlPanel"))
        layout = QVBoxLayout(self.colormap_group)
        layout.setContentsMargins(5, 5, 5, 5)
        cmap_layout = QHBoxLayout()
        self.colormap_label = QLabel(tr("Color:", "ControlPanel"))
        cmap_layout.addWidget(self.colormap_label)
        self.colormap_combo = QComboBox()
        self.colormap_combo.setToolTip(tr("Select colormap for scatter plots and overlays", "ControlPanel"))
        
        general_colormaps, not_3d_colormaps = Config.get_all_colormaps_grouped()
        
        for cmap_name, cmap_display in general_colormaps:
            self.colormap_combo.addItem(tr(cmap_display, "LAOSAnalysis"), cmap_name)
        
        self.colormap_combo.insertSeparator(self.colormap_combo.count())
        separator_text = tr("--- Not suitable for 3D ---", "ColormapTags")
        self.colormap_combo.addItem(separator_text, "__separator__")
        
        for cmap_name, cmap_display in not_3d_colormaps:
            self.colormap_combo.addItem(tr(cmap_display, "LAOSAnalysis"), cmap_name)
        
        default_idx = self.colormap_combo.findData("viridis")
        if default_idx >= 0:
            self.colormap_combo.setCurrentIndex(default_idx)
        self.colormap_combo.currentIndexChanged.connect(self._on_colormap_changed)
        # Do not let the longest item (e.g. "turbo_r (Recommended for Stress
        # Bifurcation)") dictate the panel width: size to a moderate amount of
        # content and let the popup show the full text.
        self.colormap_combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.colormap_combo.setMinimumContentsLength(12)
        self.colormap_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cmap_layout.addWidget(self.colormap_combo)
        layout.addLayout(cmap_layout)
        self.colormap_preview_label = QLabel()
        self.colormap_preview_label.setFixedHeight(get_ui_scale().scaled(30))
        # The preview pixmap must not dictate the panel width (that would feed
        # back into the layout and grow the whole window); ignore its hint.
        self.colormap_preview_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.colormap_preview_label.setMinimumWidth(0)
        self.colormap_preview_label.setToolTip(tr("Colormap preview", "ControlPanel"))
        layout.addWidget(self.colormap_preview_label)
        self._update_colormap_preview("viridis")

    def _on_colormap_changed(self, index):
        """Handle colormap selection change"""
        cmap_name = self.colormap_combo.currentData()
        if cmap_name == "__separator__":
            self.colormap_combo.setCurrentIndex(index - 1 if index > 0 else index + 1)
            return
        self._update_colormap_preview(cmap_name)

    def _render_colormap_pixmap(self, cmap_name: str) -> Optional[QPixmap]:
        """Render a colormap strip to a self-owned QPixmap (cached)."""
        if not hasattr(self, '_colormap_pixmap_cache'):
            self._colormap_pixmap_cache = {}
        cached = self._colormap_pixmap_cache.get(cmap_name)
        if cached is not None and not cached.isNull():
            return cached
        try:
            import matplotlib
            matplotlib.use("Agg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            cmap = plt.get_cmap(cmap_name)
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            fig = Figure(figsize=(4, 0.3), dpi=100)
            canvas = FigureCanvasAgg(fig)
            ax = fig.add_subplot(111)
            ax.imshow(gradient, aspect="auto", cmap=cmap)
            ax.axis("off")
            canvas.draw()
            width, height = canvas.get_width_height()
            buf = np.asarray(canvas.buffer_rgba())
            # Copy the pixels: QImage does not own the buffer and the
            # numpy/matplotlib buffer may be freed, which would leave a
            # dangling pointer and crash Qt later.
            qimg = QImage(buf.data, width, height, int(buf.strides[0]), QImage.Format_RGBA8888).copy()
            pixmap = QPixmap.fromImage(qimg)
            self._colormap_pixmap_cache[cmap_name] = pixmap
            return pixmap
        except Exception:
            return None

    def _update_colormap_preview(self, cmap_name: str):
        """Update colormap preview bar"""
        pixmap = self._render_colormap_pixmap(cmap_name)
        if pixmap is None or pixmap.isNull():
            self.colormap_preview_label.setText(f"[{cmap_name}]")
            return
        label_width = self.colormap_preview_label.width()
        target_height = self.colormap_preview_label.height() or get_ui_scale().scaled(30)
        if label_width > 10:
            scaled_pixmap = pixmap.scaled(label_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.colormap_preview_label.setPixmap(scaled_pixmap)
        else:
            self.colormap_preview_label.setPixmap(pixmap)

    def get_colormap(self) -> str:
        """Get selected colormap name"""
        return self.colormap_combo.currentData()

    def resizeEvent(self, event):
        """Handle resize event to update colormap preview"""
        super().resizeEvent(event)
        # Defer to the event loop: rendering matplotlib synchronously inside a
        # resize (which also fires during a stylesheet re-polish) can re-enter
        # layout/paint and crash Qt.
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, self._refresh_colormap_preview)

    def _refresh_colormap_preview(self):
        """Refresh the colormap preview using the current selection."""
        try:
            cmap_name = self.colormap_combo.currentData()
            if cmap_name and cmap_name != "__separator__":
                self._update_colormap_preview(cmap_name)
        except RuntimeError:
            pass

    def _on_lissajous_subtype_changed(self, index):
        """Handle Lissajous overlay subtype selection"""
        subtype_code = self.lissajous_combo.currentData()
        self._update_params_visibility(subtype_code)

    def _on_spp_subtype_changed(self, index):
        """Handle SPP subtype change"""
        subtype_code = self.spp_combo.currentData()
        self._update_params_visibility(subtype_code)
        # For SPP Multi-File Overlay (7b), auto switch to jet_r
        if subtype_code == "7b":
            jet_r_idx = self.colormap_combo.findData("jet_r")
            if jet_r_idx >= 0:
                self.colormap_combo.setCurrentIndex(jet_r_idx)
        # For SPP single plot (7a, 7d, 7c), switch to viridis
        elif subtype_code in ("7a", "7d", "7c"):
            viridis_idx = self.colormap_combo.findData("viridis")
            if viridis_idx >= 0:
                self.colormap_combo.setCurrentIndex(viridis_idx)

    def _on_harmonics_mode_changed(self, index):
        """Auto: hide spin box; Manual: show spin box for user input"""
        mode = self.harmonics_combo.currentData()
        self.harmonics_spin.setVisible(mode == "manual")

    def _on_cage_modulus_subtype_changed(self, index):
        """Handle cage modulus subtype selection"""
        subtype_code = self.cage_modulus_combo.currentData()
        self._update_params_visibility(subtype_code)
    
    def _on_fourier_single_subtype_changed(self, index):
        """Handle Fourier single subtype selection"""
        subtype_code = self.fourier_single_combo.currentData()
        self._update_params_visibility(subtype_code)

    def _create_params_group(self):
        """Create parameters input group - initially hidden"""
        self.params_group = QGroupBox(tr("Parameters", "ControlPanel"))
        self.params_group.setVisible(False)
        layout = QGridLayout(self.params_group)
        self.file_index_label = QLabel(tr("File Index:", "ControlPanel"))
        layout.addWidget(self.file_index_label, 0, 0)
        self.file_index_edit = QLineEdit()
        self.file_index_edit.setText("000")
        self.file_index_edit.setInputMask("999")
        tooltips = get_param_tooltips()
        self.file_index_edit.setToolTip(tooltips["file_index"])
        self.file_index_edit.setVisible(False)
        layout.addWidget(self.file_index_edit, 0, 1)
        self.files_label = QLabel(tr("Files:", "ControlPanel"))
        self.files_label.setVisible(False)
        layout.addWidget(self.files_label, 1, 0)
        self.files_edit = QLineEdit()
        self.files_edit.setPlaceholderText(tr("e.g., 030,120,150", "ControlPanel"))
        self.files_edit.setToolTip(tooltips["files_edit"])
        self.files_edit.setVisible(False)
        layout.addWidget(self.files_edit, 1, 1)
        self.harmonics_label = QLabel(tr("Harmonics:", "ControlPanel"))
        self.harmonics_label.setVisible(False)
        layout.addWidget(self.harmonics_label, 2, 0)
        harmonics_layout = QHBoxLayout()
        harmonics_layout.setContentsMargins(0, 0, 0, 0)
        self.harmonics_combo = QComboBox()
        self.harmonics_combo.addItem(tr("Auto", "ControlPanel"), "auto")
        self.harmonics_combo.addItem(tr("Manual", "ControlPanel"), "manual")
        self.harmonics_combo.setToolTip(tr("Auto: filter harmonics (In/I1 < 1e-4 removed); Manual: enter N", "ParamTooltips"))
        self.harmonics_combo.setVisible(False)
        self.harmonics_combo.currentIndexChanged.connect(self._on_harmonics_mode_changed)
        harmonics_layout.addWidget(self.harmonics_combo)
        self.harmonics_spin = QLineEdit()
        self.harmonics_spin.setPlaceholderText("15")
        self.harmonics_spin.setToolTip(tooltips["harmonics"])
        self.harmonics_spin.setVisible(False)
        harmonics_layout.addWidget(self.harmonics_spin)
        self.harmonics_widget = QWidget()
        self.harmonics_widget.setLayout(harmonics_layout)
        self.harmonics_widget.setVisible(False)
        layout.addWidget(self.harmonics_widget, 2, 1)
        self.omega_label = QLabel(tr("ω (Frequency):", "ControlPanel"))
        self.omega_label.setVisible(False)
        layout.addWidget(self.omega_label, 3, 0)
        omega_layout = QHBoxLayout()
        self.omega_unit_combo = QComboBox()
        self.omega_unit_combo.addItems(["Hz", "rad/s"])
        self.omega_unit_combo.setToolTip(tooltips["omega_unit"])
        self.omega_unit_combo.currentTextChanged.connect(self._on_omega_unit_changed)
        self.omega_unit_combo.setVisible(False)
        omega_layout.addWidget(self.omega_unit_combo)
        self.omega_value_spin = QDoubleSpinBox()
        self.omega_value_spin.setMinimum(0.01)
        self.omega_value_spin.setMaximum(1000)
        self.omega_value_spin.setValue(1)
        self.omega_value_spin.setDecimals(2)
        self.omega_value_spin.setToolTip(tooltips["omega"])
        self.omega_value_spin.setVisible(False)
        omega_layout.addWidget(self.omega_value_spin)
        self.pi_label = QLabel("π")
        self.pi_label.setVisible(False)
        omega_layout.addWidget(self.pi_label)
        layout.addLayout(omega_layout, 3, 1)
        self._on_omega_unit_changed(self.omega_unit_combo.currentText())
        self.max_harmonic_label = QLabel(tr("Max Harmonic (n):", "ControlPanel"))
        self.max_harmonic_label.setVisible(False)
        layout.addWidget(self.max_harmonic_label, 4, 0)
        self.max_harmonic_spin = QSpinBox()
        self.max_harmonic_spin.setMinimum(1)
        self.max_harmonic_spin.setMaximum(100)
        self.max_harmonic_spin.setValue(30)
        self.max_harmonic_spin.setToolTip(tr("Maximum harmonic number to display (will show n=1 to n=max)", "ControlPanel"))
        self.max_harmonic_spin.setVisible(False)
        layout.addWidget(self.max_harmonic_spin, 4, 1)
        self.data_range_label = QLabel(tr("Data Range:", "ControlPanel"))
        self.data_range_label.setVisible(False)
        layout.addWidget(self.data_range_label, 5, 0)
        self.data_range_combo = QComboBox()
        self.data_range_combo.addItems([
         tr("Full Data", "ControlPanel"),
         tr("First Half", "ControlPanel"),
         tr("Second Half", "ControlPanel")])
        self.data_range_combo.setToolTip(tooltips["data_range"])
        self.data_range_combo.setVisible(False)
        layout.addWidget(self.data_range_combo, 5, 1)

        # Circular decomposition component selector (SPP 7c)
        self.decomp_component_label = QLabel(tr("Trajectory:", "ControlPanel"))
        self.decomp_component_label.setVisible(False)
        layout.addWidget(self.decomp_component_label, 6, 0)
        self.decomp_component_combo = QComboBox()
        self.decomp_component_combo.addItem(tr("G′ₜ - G″ₜ (Cole-Cole)", "ControlPanel"), "Gt")
        self.decomp_component_combo.addItem(tr("dG′ₜ/dt - dG″ₜ/dt", "ControlPanel"), "Gt_deriv")
        self.decomp_component_combo.setToolTip(tr("Choose which SPP trajectory to decompose into rotating circles", "ControlPanel"))
        self.decomp_component_combo.setVisible(False)
        layout.addWidget(self.decomp_component_combo, 6, 1)
        self.edit_titles_btn = QPushButton(tr("Edit Titles...", "ControlPanel"))
        self.edit_titles_btn.setToolTip(tr("Open dialog to edit custom curve titles for each file", "ControlPanel"))
        self.edit_titles_btn.clicked.connect(self._on_edit_titles)
        self.edit_titles_btn.setVisible(False)
        layout.addWidget(self.edit_titles_btn, 6, 0, 1, 2)
        self.show_bifurcation_checkbox = QCheckBox(tr("Show Bifurcation Point", "ControlPanel"))
        self.show_bifurcation_checkbox.setToolTip(tr("Mark bifurcation points on the plot and display stress values", "ControlPanel"))
        self.show_bifurcation_checkbox.setChecked(False)
        self.show_bifurcation_checkbox.setVisible(False)
        layout.addWidget(self.show_bifurcation_checkbox, 7, 0, 1, 2)
        self.use_normalized_checkbox = QCheckBox(tr("Use Normalized Data", "ControlPanel"))
        self.use_normalized_checkbox.setToolTip(tr("Normalize stress-strain data to [-1, 1] range for overlay", "ControlPanel"))
        self.use_normalized_checkbox.setChecked(False)
        self.use_normalized_checkbox.setVisible(False)
        layout.addWidget(self.use_normalized_checkbox, 9, 0, 1, 2)
        
        # Marker size setting for scatter plots
        self.marker_size_label = QLabel(tr("Marker Size:", "ControlPanel"))
        self.marker_size_label.setVisible(False)
        layout.addWidget(self.marker_size_label, 10, 0)
        self.marker_size_spin = QSpinBox()
        self.marker_size_spin.setMinimum(1)
        self.marker_size_spin.setMaximum(200)
        self.marker_size_spin.setValue(50)
        self.marker_size_spin.setToolTip(tr("Marker size for scatter plots (1-200)", "ControlPanel"))
        self.marker_size_spin.setVisible(False)
        layout.addWidget(self.marker_size_spin, 10, 1)
        
        # Line width setting for line plots
        self.line_width_label = QLabel(tr("Line Width:", "ControlPanel"))
        self.line_width_label.setVisible(False)
        layout.addWidget(self.line_width_label, 11, 0)
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setMinimum(1)
        self.line_width_spin.setMaximum(20)
        self.line_width_spin.setValue(5)
        self.line_width_spin.setToolTip(tr("Line width for curve plots (1-20)", "ControlPanel"))
        self.line_width_spin.setVisible(False)
        layout.addWidget(self.line_width_spin, 11, 1)
        
        self._custom_titles = None

    def _on_omega_unit_changed(self, unit: str):
        """Handle omega unit change"""
        if unit == "rad/s":
            self.pi_label.setVisible(False)
            self.omega_value_spin.setToolTip(tr("Angular frequency ω (rad/s)", "ControlPanel"))
            self.omega_value_spin.setDecimals(4)
        else:
            self.pi_label.setVisible(False)
            self.omega_value_spin.setToolTip(tr("Frequency f (Hz)", "ControlPanel"))
            self.omega_value_spin.setDecimals(2)

    def _create_progress_group(self):
        """Create progress display group"""
        self.progress_group = QGroupBox(tr("Progress", "ControlPanel"))
        layout = QVBoxLayout(self.progress_group)
        layout.setContentsMargins(5, 5, 5, 5)
        self.progress_panel = EnhancedProgressPanel()
        layout.addWidget(self.progress_panel)
        self.progress_bar = self.progress_panel.progress_bar
        self.status_label = self.progress_panel.status_label

    def _on_full_preprocess(self):
        """Handle full preprocess button click"""
        self.run_preprocess.emit()

    def _on_cancel(self):
        """Handle cancel button click"""
        self.cancel_requested.emit()

    def _on_plot_type_changed(self, index):
        """Handle plot type change - show/hide relevant parameters"""
        plot_code = self.plot_type_combo.currentData()
        if plot_code == "3_menu":
            self.lissajous_combo.setVisible(True)
            self.fourier_single_combo.setVisible(False)
            self.spp_combo.setVisible(False)
            self.cage_modulus_combo.setVisible(False)
            subtype_code = self.lissajous_combo.currentData()
            self._update_params_visibility(subtype_code)
            viridis_idx = self.colormap_combo.findData("viridis")
            if viridis_idx >= 0:
                self.colormap_combo.setCurrentIndex(viridis_idx)
            return
        if plot_code == "6_menu":
            self.fourier_single_combo.setVisible(True)
            self.lissajous_combo.setVisible(False)
            self.spp_combo.setVisible(False)
            self.cage_modulus_combo.setVisible(False)
            subtype_code = self.fourier_single_combo.currentData()
            self._update_params_visibility(subtype_code)
            viridis_idx = self.colormap_combo.findData("viridis")
            if viridis_idx >= 0:
                self.colormap_combo.setCurrentIndex(viridis_idx)
            return
        if plot_code == "7_menu":
            self.spp_combo.setVisible(True)
            self.lissajous_combo.setVisible(False)
            self.fourier_single_combo.setVisible(False)
            self.cage_modulus_combo.setVisible(False)
            subtype_code = self.spp_combo.currentData()
            self._update_params_visibility(subtype_code)
            # For SPP Multi-File Overlay (7b), auto switch to jet_r
            if subtype_code == "7b":
                jet_r_idx = self.colormap_combo.findData("jet_r")
                if jet_r_idx >= 0:
                    self.colormap_combo.setCurrentIndex(jet_r_idx)
# For SPP single plot (7a, 7d, 7c), switch to viridis
            elif subtype_code in ("7a", "7d", "7c"):
                viridis_idx = self.colormap_combo.findData("viridis")
                if viridis_idx >= 0:
                    self.colormap_combo.setCurrentIndex(viridis_idx)
            return
        if plot_code == "10_menu":
            self.cage_modulus_combo.setVisible(True)
            self.lissajous_combo.setVisible(False)
            self.fourier_single_combo.setVisible(False)
            self.spp_combo.setVisible(False)
            subtype_code = self.cage_modulus_combo.currentData()
            self._update_params_visibility(subtype_code)
            viridis_idx = self.colormap_combo.findData("viridis")
            if viridis_idx >= 0:
                self.colormap_combo.setCurrentIndex(viridis_idx)
            return
        self.lissajous_combo.setVisible(False)
        self.fourier_single_combo.setVisible(False)
        self.spp_combo.setVisible(False)
        self.cage_modulus_combo.setVisible(False)
        self._update_params_visibility(plot_code)
        # Auto switch colormap for specific plot types
        if plot_code == "8":  # Stress Bifurcation
            turbo_r_idx = self.colormap_combo.findData("turbo_r")
            if turbo_r_idx >= 0:
                self.colormap_combo.setCurrentIndex(turbo_r_idx)
        else:
            # Reset to default viridis for other plot types
            viridis_idx = self.colormap_combo.findData("viridis")
            if viridis_idx >= 0:
                self.colormap_combo.setCurrentIndex(viridis_idx)

    def _update_params_visibility(self, plot_code: str):
        """Update parameter widgets visibility based on plot code"""
        required_params = PLOT_PARAM_MAP.get(plot_code, [])
        
        # Determine if we need to show params_group
        scatter_plots = ('4', '9', '6', '6q', '7a', '7d', '7b', '8')  # ST values, Dissipation, Fourier, Q Value, SPP (Fourier/Derivative/multi), Bifurcation
        line_plots = ('1', '3a', '3b', '3c', '5')  # Lissajous curves
        
        # Determine if we need to show params_group
        is_scatter = plot_code in scatter_plots
        is_line = plot_code in line_plots
        
        # Show params_group if there are required params OR if it's a scatter/line plot
        if not required_params and not is_scatter and not is_line:
            self.params_group.setVisible(False)
            return
        
        self.params_group.setVisible(True)
        self.file_index_label.setVisible("file_index" in required_params)
        self.file_index_edit.setVisible("file_index" in required_params)
        self.files_label.setVisible("files_edit" in required_params)
        self.files_edit.setVisible("files_edit" in required_params)
        self.harmonics_label.setVisible("harmonics" in required_params)
        self.harmonics_widget.setVisible("harmonics" in required_params)
        if "harmonics" in required_params:
            if plot_code == '6':
                # For Fourier single-order, hide Auto/Manual, show only spin
                self.harmonics_combo.setVisible(False)
                self.harmonics_spin.setVisible(True)
                self.harmonics_spin.setText("3")
            elif plot_code in ('7a', '7d', '7b', '7c'):
                # For SPP, show Auto/Manual dropdown, default Auto (spin hidden)
                self.harmonics_combo.setVisible(True)
                self.harmonics_combo.setCurrentIndex(0)  # Auto
                self.harmonics_spin.setVisible(False)
                self.harmonics_spin.setText("15")
        max_harmonic_required = "max_harmonic" in required_params
        self.max_harmonic_label.setVisible(max_harmonic_required)
        self.max_harmonic_spin.setVisible(max_harmonic_required)
        omega_required = "omega" in required_params
        self.omega_label.setVisible(omega_required)
        self.omega_unit_combo.setVisible(omega_required)
        self.omega_value_spin.setVisible(omega_required)
        data_range_required = "data_range" in required_params
        self.data_range_label.setVisible(data_range_required)
        self.data_range_combo.setVisible(data_range_required)
        decomp_required = "decomp_component" in required_params
        self.decomp_component_label.setVisible(decomp_required)
        self.decomp_component_combo.setVisible(decomp_required)
        title_options_visible = plot_code in ('7b', '3a', '3b', '3c', '5')
        self.edit_titles_btn.setVisible(title_options_visible)
        show_bifurcation_required = "show_bifurcation" in required_params
        self.show_bifurcation_checkbox.setVisible(show_bifurcation_required)
        use_normalized_required = "use_normalized" in required_params
        self.use_normalized_checkbox.setVisible(use_normalized_required)
        
        # Show marker size for scatter plots, line width for line plots
        scatter_plots = ('4', '9', '6', '6q', '7a', '7d', '7b', '7c', '8')  # ST values, Dissipation, Fourier, SPP (Fourier/Derivative/multi), Bifurcation, Q Value
        line_plots = ('1', '3a', '3b', '3c', '5')  # Lissajous curves
        
        is_scatter = plot_code in scatter_plots
        is_line = plot_code in line_plots
        
        self.marker_size_label.setVisible(is_scatter)
        self.marker_size_spin.setVisible(is_scatter)
        self.line_width_label.setVisible(is_line)
        self.line_width_spin.setVisible(is_line)
        
        params_str = ", ".join(required_params)
        self.plot_btn.setToolTip(f"所需参数: {params_str}")

    def _on_plot(self):
        """Handle plot button click"""
        plot_type = self.plot_type_combo.currentData()
        if plot_type == "3_menu":
            plot_type = self.lissajous_combo.currentData()
        elif plot_type == "6_menu":
            plot_type = self.fourier_single_combo.currentData()
        elif plot_type == "7_menu":
            plot_type = self.spp_combo.currentData()
        elif plot_type == "10_menu":
            plot_type = self.cage_modulus_combo.currentData()
        
        # Debug: Check omega visibility
        print(f"[DEBUG _on_plot] plot_type: {plot_type}")
        print(f"[DEBUG _on_plot] omega_label visible: {self.omega_label.isVisible()}")
        print(f"[DEBUG _on_plot] omega_value_spin value: {self.omega_value_spin.value()}")
        print(f"[DEBUG _on_plot] omega_unit: {self.omega_unit_combo.currentText()}")
        print(f"[DEBUG _on_plot] _preprocessed_frequency: {self._preprocessed_frequency}")
        
        params = self.get_parameters()
        print(f"[DEBUG _on_plot] params keys: {params.keys()}")
        if 'omega' in params:
            print(f"[DEBUG _on_plot] params['omega']: {params['omega']}")
        
        self.plot_requested.emit(plot_type, params)

    def get_parameters(self) -> dict:
        """Get all parameters from the control panel"""
        import numpy as np
        params = {}
        
        plot_type = self.plot_type_combo.currentData()
        if plot_type == "3_menu":
            plot_type = self.lissajous_combo.currentData()
        elif plot_type == "6_menu":
            plot_type = self.fourier_single_combo.currentData()
        elif plot_type == "7_menu":
            plot_type = self.spp_combo.currentData()
        elif plot_type == "10_menu":
            plot_type = self.cage_modulus_combo.currentData()
        
        params['plot_type'] = plot_type
        
        if self.file_index_edit.isVisible():
            try:
                params['file_index'] = int(self.file_index_edit.text())
            except ValueError:
                params['file_index'] = 0
        
        if self.files_edit.isVisible():
            params['files_edit'] = self.files_edit.text()
        
        if self.harmonics_combo.isVisible():
            if self.harmonics_combo.currentData() == "auto":
                params['harmonics'] = 'auto'
            else:
                params['harmonics'] = int(self.harmonics_spin.text()) if self.harmonics_spin.text().strip() else 15
        
        if self.omega_label.isVisible():
            omega_value = self.omega_value_spin.value()
            omega_unit = self.omega_unit_combo.currentText()
            if omega_unit == "rad/s":
                params['omega'] = omega_value  # direct angular frequency input
            else:
                params['omega'] = omega_value * 2 * np.pi  # Hz -> rad/s
        
        if self.max_harmonic_spin.isVisible():
            params['max_harmonic'] = self.max_harmonic_spin.value()
        
        if self.data_range_combo.isVisible():
            params['data_range'] = self.data_range_combo.currentIndex()
        
        if self.decomp_component_combo.isVisible():
            params['decomp_component'] = self.decomp_component_combo.currentData()
        
        if self.show_bifurcation_checkbox.isVisible():
            params['show_bifurcation'] = self.show_bifurcation_checkbox.isChecked()
        
        params['colormap'] = self.colormap_combo.currentData()
        
        title_options_visible = plot_type in ('7b', '3a', '3b', '3c', '5')
        if title_options_visible:
            params['title_options'] = self.get_title_options()
        
        if self.use_normalized_checkbox.isVisible():
            params['use_normalized'] = self.use_normalized_checkbox.isChecked()
        
        # Add marker size and line width settings
        if self.marker_size_spin.isVisible():
            params['marker_size'] = self.marker_size_spin.value()
        
        if self.line_width_spin.isVisible():
            params['line_width'] = self.line_width_spin.value()
        
        return params
    
    def get_file_index(self) -> int:
        """Get file index from edit field"""
        try:
            return int(self.file_index_edit.text())
        except ValueError:
            return 0
    
    def _on_edit_titles(self):
        """Handle edit titles button click"""
        files_edit_text = self.files_edit.text()
        if not files_edit_text:
            QMessageBox.warning(self, tr("Warning", "Messages"),
                               tr("Please enter file indices first.", "Messages"))
            return
        
        try:
            file_indices = [int(x.strip()) for x in files_edit_text.split(',')]
        except ValueError:
            QMessageBox.warning(self, tr("Warning", "Messages"),
                               tr("Invalid file indices format.", "Messages"))
            return
        
        current_titles = self._custom_titles or [f"File {idx:03d}" for idx in file_indices]
        
        from ui.widgets.control_panel import TitleEditDialog
        dialog = TitleEditDialog(file_indices, current_titles, self)
        if dialog.exec_() == QDialog.Accepted:
            self._custom_titles = dialog.get_titles()
            self.log_requested.emit(f"Custom titles set for {len(file_indices)} files")



    def set_progress(self, value: int, message: str='', filename: str=''):
        """
        Set progress bar value with optional time estimation

        Args:
            value: Progress percentage (0-100)
            message: Optional status message
            filename: Optional current file name
        """
        self.progress_panel.update(value, message, filename)

    def start_progress(self, message: str=''):
        """
        Start progress tracking

        Args:
            message: Start message
        """
        self.progress_panel.start(message)

    def finish_progress(self, success: bool=True, message: str=''):
        """
        Finish progress tracking

        Args:
            success: Whether operation succeeded
            message: Finish message
        """
        self.progress_panel.finish(success, message)

    def set_status(self, message: str, is_error: bool=False):
        """
        Set status message

        Args:
            message: Status message
            is_error: Whether this is an error message
        """
        self.status_label.setText(message)
        if is_error:
            self.status_label.setStyleSheet("color: red;")
    
    def set_default_frequency(self, frequency_hz: float):
        """
        Set default frequency value in control panel
        
        Args:
            frequency_hz: Frequency in Hz
        """
        import numpy as np
        if frequency_hz > 0:
            self.omega_unit_combo.setCurrentText("Hz")
            self.omega_value_spin.setValue(frequency_hz)
            self.pi_label.setVisible(False)
            self.omega_value_spin.setToolTip(tr("Frequency f (Hz)", "ControlPanel"))
            
            self.frequency_display_label.setText(tr(f"Frequency: {frequency_hz:.2f} Hz", "ControlPanel"))
            self.frequency_display_label.setVisible(True)
            self._preprocessed_frequency = frequency_hz
            
            print(f"[DEBUG ControlPanel] set_default_frequency: {frequency_hz:.2f} Hz")
            print(f"[DEBUG ControlPanel] _preprocessed_frequency saved: {self._preprocessed_frequency}")
    
    def get_frequency_hz(self) -> float:
        """
        Get current frequency setting in Hz
        
        Returns:
            Frequency in Hz
        """
        import numpy as np
        omega_value = self.omega_value_spin.value()
        omega_unit = self.omega_unit_combo.currentText()
        
        if omega_unit == "rad/s":
            omega = omega_value * np.pi
        else:
            omega = omega_value * 2 * np.pi
        
        return omega / (2 * np.pi)

    def get_preprocessed_frequency(self) -> Optional[float]:
        """
        Get the frequency used during preprocessing
        
        Returns:
            Frequency in Hz if preprocessing was done, None otherwise
        """
        print(f"[DEBUG ControlPanel] get_preprocessed_frequency: returning {self._preprocessed_frequency}")
        return self._preprocessed_frequency

    def set_processing(self, is_processing: bool):
        """
        Set processing state (enable/disable controls)

        Args:
            is_processing: Whether processing is in progress
        """
        self.full_preprocess_btn.setEnabled(not is_processing)
        if is_processing:
            self.full_preprocess_btn.setText("处理中...")
        else:
            self.full_preprocess_btn.setText("▶ 运行完整预处理")

    def set_file_index(self, index: int):
        """
        Set file index with 3-digit format

        Args:
            index: File index (0-999)
        """
        self.file_index_edit.setText(f"{index:03d}")

    def get_file_index(self) -> int:
        """Get file index from edit field"""
        try:
            return int(self.file_index_edit.text())
        except ValueError:
            return 0

    def _on_edit_titles(self):
        """Handle edit titles button click"""
        files_edit_text = self.files_edit.text()
        if not files_edit_text:
            QMessageBox.warning(self, tr("Warning", "Messages"),
                               tr("Please enter file indices first.", "Messages"))
            return
        
        try:
            file_indices = [int(x.strip()) for x in files_edit_text.split(',')]
        except ValueError:
            QMessageBox.warning(self, tr("Warning", "Messages"),
                               tr("Invalid file indices format.", "Messages"))
            return
        
        current_titles = self._custom_titles or [f"File {idx:03d}" for idx in file_indices]
        
        from ui.widgets.control_panel import TitleEditDialog
        dialog = TitleEditDialog(file_indices, current_titles, self)
        if dialog.exec_() == QDialog.Accepted:
            self._custom_titles = dialog.get_titles()
            self.log_requested.emit(f"Custom titles set for {len(file_indices)} files")

    def get_custom_titles(self) -> Optional[List[str]]:
        """Get custom titles set by user"""
        return self._custom_titles

    def get_title_options(self) -> Dict:
        """Get title handling options"""
        return {
            'custom_titles': self._custom_titles
        }
    
    def sync_plot_settings(self):
        """Sync control panel widgets with current settings from settings manager"""
        from utils.settings import get_settings
        settings = get_settings()
        
        colormap = settings.get_plot_setting("colormap", "viridis")
        colormap_idx = self.colormap_combo.findData(colormap)
        if colormap_idx >= 0:
            self.colormap_combo.setCurrentIndex(colormap_idx)
        
        marker_size = settings.get_plot_setting("marker_size", 50)
        if self.marker_size_spin.isVisible():
            self.marker_size_spin.setValue(marker_size)
        
        line_width = settings.get_plot_setting("line_width", 5)
        if self.line_width_spin.isVisible():
            self.line_width_spin.setValue(line_width)
        
        self._update_colormap_preview(colormap)
        
    def sync_from_menu_setting(self, setting_key: str, value):
        """Sync a specific setting from menu change to control panel widget
        
        Args:
            setting_key: The settings key (e.g., 'colormap', 'marker_size', 'line_width')
            value: The new value
        """
        if setting_key == "colormap":
            colormap_idx = self.colormap_combo.findData(value)
            if colormap_idx >= 0:
                self.colormap_combo.setCurrentIndex(colormap_idx)
                self._update_colormap_preview(value)
        elif setting_key == "marker_size":
            if self.marker_size_spin.isVisible():
                self.marker_size_spin.setValue(value)
        elif setting_key == "line_width":
            if self.line_width_spin.isVisible():
                self.line_width_spin.setValue(value)

    def clear_custom_titles(self):
        """Clear custom titles"""
        self._custom_titles = None

    def _refresh_ui(self):
        """Refresh UI elements with new language"""
        tooltips = get_param_tooltips()
        self.preprocess_group.setTitle(tr("Preprocessing", "ControlPanel"))
        self.plot_group.setTitle(tr("Plot", "ControlPanel"))
        self.params_group.setTitle(tr("Parameters", "ControlPanel"))
        self.progress_group.setTitle(tr("Progress", "ControlPanel"))
        self.instrument_label.setText(tr("Instrument Type:", "ControlPanel"))
        self.instrument_combo.setToolTip(tr("Select the instrument type for data source", "ControlPanel"))
        self.full_preprocess_btn.setText("▶ " + tr("Run Full Preprocess", "ControlPanel"))
        self.ta_excel_btn.setText("▶ " + tr("Process TA Excel", "ControlPanel"))
        self.plot_type_label.setText(tr("Plot Type:", "ControlPanel"))
        self.plot_btn.setText(tr("Plot", "ControlPanel"))
        self._refresh_plot_type_combo()
        self._refresh_subtype_combos()
        self.file_index_label.setText(tr("File Index:", "ControlPanel"))
        self.file_index_edit.setToolTip(tooltips["file_index"])
        self.files_label.setText(tr("Files:", "ControlPanel"))
        self.files_edit.setPlaceholderText(tr("e.g., 030,120,150", "ControlPanel"))
        self.files_edit.setToolTip(tooltips["files_edit"])
        self.harmonics_label.setText(tr("Harmonics:", "ControlPanel"))
        self.harmonics_combo.setItemText(0, tr("Auto", "ControlPanel"))
        self.harmonics_combo.setItemText(1, tr("Manual", "ControlPanel"))
        self.harmonics_spin.setToolTip(tooltips["harmonics"])
        self.max_harmonic_label.setText(tr("Max Harmonic (n):", "ControlPanel"))
        self.max_harmonic_spin.setToolTip(tr("Maximum harmonic number to display (will show n=1 to n=max)", "ControlPanel"))
        self.omega_label.setText(tr("ω (Frequency):", "ControlPanel"))
        self.omega_unit_combo.setToolTip(tooltips["omega_unit"])
        self.omega_value_spin.setToolTip(tooltips["omega"])
        self.data_range_label.setText(tr("Data Range:", "ControlPanel"))
        self.data_range_combo.setToolTip(tooltips["data_range"])
        self.data_range_combo.clear()
        self.data_range_combo.addItems([
         tr("Full Data", "ControlPanel"),
         tr("First Half", "ControlPanel"),
         tr("Second Half", "ControlPanel")])
        self.decomp_component_label.setText(tr("Trajectory:", "ControlPanel"))
        current_decomp = self.decomp_component_combo.currentData()
        self.decomp_component_combo.clear()
        self.decomp_component_combo.addItem(tr("G′ₜ - G″ₜ (Cole-Cole)", "ControlPanel"), "Gt")
        self.decomp_component_combo.addItem(tr("dG′ₜ/dt - dG″ₜ/dt", "ControlPanel"), "Gt_deriv")
        idx_decomp = self.decomp_component_combo.findData(current_decomp)
        if idx_decomp >= 0:
            self.decomp_component_combo.setCurrentIndex(idx_decomp)
        self.edit_titles_btn.setText(tr("Edit Titles...", "ControlPanel"))
        self.edit_titles_btn.setToolTip(tr("Open dialog to edit custom curve titles for each file", "ControlPanel"))
        self.show_bifurcation_checkbox.setText(tr("Show Bifurcation Point", "ControlPanel"))
        self.show_bifurcation_checkbox.setToolTip(tooltips.get("show_bifurcation", ""))
        self.use_normalized_checkbox.setText(tr("Use Normalized Data", "ControlPanel"))
        self.use_normalized_checkbox.setToolTip(tr("Normalize stress-strain data to [-1, 1] range for overlay", "ControlPanel"))
        self.marker_size_label.setText(tr("Marker Size:", "ControlPanel"))
        self.marker_size_spin.setToolTip(tr("Marker size for scatter plots (1-200)", "ControlPanel"))
        self.line_width_label.setText(tr("Line Width:", "ControlPanel"))
        self.line_width_spin.setToolTip(tr("Line width for curve plots (1-20)", "ControlPanel"))
        self.progress_panel._refresh_ui()
        self.colormap_group.setTitle(tr("Colormap", "ControlPanel"))
        self.colormap_label.setText(tr("Color:", "ControlPanel"))
        self.colormap_combo.setToolTip(tr("Select colormap for scatter plots and overlays", "ControlPanel"))
        self.colormap_preview_label.setToolTip(tr("Colormap preview", "ControlPanel"))
        self._refresh_colormap_combo()

    def _refresh_colormap_combo(self):
        """Refresh colormap combo box items with grouped display"""
        current_data = self.colormap_combo.currentData()
        self.colormap_combo.clear()
        
        general_colormaps, not_3d_colormaps = Config.get_all_colormaps_grouped()
        
        for cmap_name, cmap_display in general_colormaps:
            self.colormap_combo.addItem(tr(cmap_display, "LAOSAnalysis"), cmap_name)
        
        self.colormap_combo.insertSeparator(self.colormap_combo.count())
        separator_text = tr("--- Not suitable for 3D ---", "ColormapTags")
        self.colormap_combo.addItem(separator_text, "__separator__")
        
        for cmap_name, cmap_display in not_3d_colormaps:
            self.colormap_combo.addItem(tr(cmap_display, "LAOSAnalysis"), cmap_name)
        
        if current_data and current_data != "__separator__":
            index = self.colormap_combo.findData(current_data)
            if index >= 0:
                self.colormap_combo.setCurrentIndex(index)

    def _refresh_plot_type_combo(self):
        """Refresh plot type combo box items"""
        current_data = self.plot_type_combo.currentData()
        self.plot_type_combo.clear()
        plot_types = [
         (
          "1", tr("Lissajous Curve", "PlotTypes")),
         (
          "3_menu", tr("Lissajous Overlay", "PlotTypes")),
         (
          "9", tr("Dissipation Rate", "PlotTypes")),
         (
          "6_menu", tr("Single-Order Fourier Coefficients", "PlotTypes")),
         (
          "5", tr("Multi-Order Fourier Coefficients", "PlotTypes")),
         (
          "4", tr("S-T Values", "PlotTypes")),
         (
          "8", tr("Stress Bifurcation", "PlotTypes")),
         (
          "7_menu", tr("SPP Method", "PlotTypes")),
         (
          "10_menu", tr("Cage Modulus", "PlotTypes"))]
        for code, name in plot_types:
            self.plot_type_combo.addItem(name, code)
        else:
            index = self.plot_type_combo.findData(current_data)
            if index >= 0:
                self.plot_type_combo.setCurrentIndex(index)

    def _refresh_subtype_combos(self):
        """Refresh sub-type combo boxes"""
        current_lissajous = self.lissajous_combo.currentData()
        self.lissajous_combo.clear()
        for code, name in get_lissajous_subtypes():
            self.lissajous_combo.addItem(name, code)
        index = self.lissajous_combo.findData(current_lissajous)
        if index >= 0:
            self.lissajous_combo.setCurrentIndex(index)
        
        current_fourier_single = self.fourier_single_combo.currentData()
        self.fourier_single_combo.clear()
        fourier_single_subtypes = [
            ("6", tr("In/I1 Ratio", "FourierSingleSubtypes")),
            ("6q", tr("Q Value", "FourierSingleSubtypes"))
        ]
        for code, name in fourier_single_subtypes:
            self.fourier_single_combo.addItem(name, code)
        index = self.fourier_single_combo.findData(current_fourier_single)
        if index >= 0:
            self.fourier_single_combo.setCurrentIndex(index)
        
        current_spp = self.spp_combo.currentData()
        self.spp_combo.clear()
        spp_subtypes = [
            ("7a", tr("SPP-Fourier Calculation", "SPPSubtypes")),
            ("7d", tr("SPP-Derivative Calculation", "SPPSubtypes")),
            ("7b", tr("Multi-File Overlay", "SPPSubtypes")),
            ("7c", tr("Circular Decomposition", "SPPSubtypes"))
        ]
        for code, name in spp_subtypes:
            self.spp_combo.addItem(name, code)
        index = self.spp_combo.findData(current_spp)
        if index >= 0:
            self.spp_combo.setCurrentIndex(index)
        
        current_cage = self.cage_modulus_combo.currentData()
        self.cage_modulus_combo.clear()
        cage_subtypes = [
            ("10a", tr("G'/G_cage vs Strain", "CageSubtypes")),
            ("10b", tr("G_cage vs Strain", "CageSubtypes"))
        ]
        for code, name in cage_subtypes:
            self.cage_modulus_combo.addItem(name, code)
        index = self.cage_modulus_combo.findData(current_cage)
        if index >= 0:
            self.cage_modulus_combo.setCurrentIndex(index)


class LogPanel(QWidget):
    __doc__ = "\n    Log display panel for showing processing messages\n    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        from PyQt5.QtWidgets import QTextEdit
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"\n            QTextEdit {{\n                background-color: #1e1e1e;\n                color: #d4d4d4;\n                font-family: Consolas, 'Courier New', monospace;\n                font-size: {get_ui_scale().scaled(11)}px;\n            }}\n        ")
        layout.addWidget(self.log_text)
        self.clear_btn = QPushButton(tr("Clear Log", "LogPanel"))
        self.clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_btn)

    def append_log(self, message: str, level: str='INFO'):
        """
        Append a message to the log

        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
         'INFO': '"#4EC9B0"', 
         'WARNING': '"#DCDCAA"', 
         'ERROR': '"#F44747"', 
         'DEBUG': '"#808080"'}
        color = color_map.get(level, "#d4d4d4")
        formatted = f'<span style="color: #808080;">[{timestamp}]</span> <span style="color: {color};">[{level}]</span> {message}'
        self.log_text.append(formatted)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """Clear the log"""
        self.log_text.clear()
        self.append_log(tr("Log cleared", "LogPanel"), "INFO")

    def _refresh_ui(self):
        """Refresh UI elements with new language"""
        self.clear_btn.setText(tr("Clear Log", "LogPanel"))


class TitleEditDialog(QDialog):
    __doc__ = '\n    Dialog for editing custom curve titles for SPP multi-plot\n    Matching choice=="11" functionality from LAOS数据处理 0417.py\n    '

    def __init__(self, file_numbers, current_titles=None, parent=None):
        super().__init__(parent)
        self.file_numbers = file_numbers
        self.current_titles = current_titles or [f"文件 {num}" for num in file_numbers]
        self.title_edits = []
        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle(tr("Edit Curve Titles", "ControlPanel"))
        self.setMinimumWidth(get_ui_scale().scaled(400))
        self.setMinimumHeight(get_ui_scale().scaled(300))
        layout = QVBoxLayout(self)
        instructions = QLabel(tr("Enter custom curve titles for each file number. These titles will be displayed in the legend.", "ControlPanel"))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        for i, (file_num, title) in enumerate(zip(self.file_numbers, self.current_titles)):
            label = QLabel(tr("File Number:", "ControlPanel") + f" {file_num}")
            scroll_layout.addWidget(label, i, 0)
            edit = QLineEdit()
            edit.setText(title)
            edit.setPlaceholderText(tr("Enter title for file", "ControlPanel") + f" {file_num}")
            self.title_edits.append(edit)
            scroll_layout.addWidget(edit, i, 1)
        else:
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)
            layout.addWidget(button_box)

    def get_titles(self) -> List[str]:
        """Get the edited titles"""
        return [edit.text().strip() or f"File {num}" for num, edit in zip(self.file_numbers, self.title_edits)]