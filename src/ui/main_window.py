# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: ui\main_window.py
"""
Main Window - PyQt5 main window for LAOS Analysis GUI
Implements the full application layout with menu bar, toolbar,
three-panel layout, log area, and status bar
"""
import os, sys, glob, numpy as np
from typing import Optional
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QAction, QActionGroup, QToolBar, QStatusBar, QSplitter, QFileDialog, QMessageBox, QLabel, QApplication, QProgressBar, QStackedWidget, QTabWidget, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QScrollArea, QCheckBox, QComboBox, QLineEdit, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

def get_app_path():
    """Get application path (works for both source and packaged exe)"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from ui.widgets.file_selector import FileSelector
from ui.widgets.plot_widget import PlotWidgetContainer
from ui.widgets.control_panel import ControlPanel, LogPanel
from ui.widgets.data_preview import DataPreviewDialog
from ui.widgets.welcome_panel import WelcomePanel
from ui.widgets.history_panel import HistoryPanel
from core.file_handler import FileHandler
from core.data_processor import DataProcessor
from core.plotter import Plotter
from utils.config import Config
from utils.i18n import tr
from utils.settings import get_settings
from utils.themes import get_theme_manager, apply_theme
from utils.responsive import get_screen_info, get_ui_scale

class WorkerThread(QThread):
    __doc__ = "Background thread for running processing tasks"
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)

    def __init__(self, processor, task, parent=None, ta_sheets_info=None, ta_cycle_ranges=None, ta_frequency=None):
        super().__init__(parent)
        self.processor = processor
        self.task = task
        self.ta_sheets_info = ta_sheets_info
        self.ta_cycle_ranges = ta_cycle_ranges
        self.ta_frequency = ta_frequency
        try:
            self.processor.progress_updated.connect(self.progress_updated)
            self.processor.log_message.connect(self.log_message)
        except Exception as e:
            try:
                print(f"Signal connection error: {e}")
            finally:
                e = None
                del e

    def run(self):
        """Run the assigned task"""
        print(f"[DEBUG] WorkerThread.run() starting task: {self.task}")
        print(f"[DEBUG] processor.folder_path: {self.processor.folder_path}")
        success = False
        message = ""
        try:
            if self.task == "full":
                print("[DEBUG] Running run_full_preprocess")
                success = self.processor.run_full_preprocess()
                message = "Full preprocessing completed" if success else "Preprocessing failed"
                print(f"[DEBUG] run_full_preprocess result: {success}")
            elif self.task == "split":
                success = self.processor.split_txt_files()
                message = "File splitting completed" if success else "File splitting failed"
            elif self.task == "noise":
                success = self.processor.apply_noise_reduction()
                message = "Noise reduction completed" if success else "Noise reduction failed"
            elif self.task == "phase":
                success = self.processor.phase_correction()
                message = "Phase correction completed" if success else "Phase correction failed"
            elif self.task == "shear":
                success = self.processor.calculate_shear_rate()
                message = "Shear rate calculation completed" if success else "Shear rate calculation failed"
            elif self.task == "fourier":
                success = self.processor.fourier_transform()
                message = "Fourier transform completed" if success else "Fourier transform failed"
            elif self.task == "st":
                plotter = Plotter()
                plotter.set_folder_path(self.processor.folder_path)
                success = plotter.calculate_st_value()
                message = "ST calculation completed" if success else "ST calculation failed"
            elif self.task == "bifurcation":
                plotter = Plotter()
                plotter.set_folder_path(self.processor.folder_path)
                success = plotter.calculate_stress_bifurcation()
                message = "Bifurcation calculation completed" if success else "Bifurcation calculation failed"
            elif self.task == "spp":
                plotter = Plotter()
                plotter.set_folder_path(self.processor.folder_path)
                success = plotter.calculate_spp(0, 10)
                message = "SPP calculation completed" if success else "SPP calculation failed"
            elif self.task == "ta_excel":
                success = self.processor.split_ta_excel_files(self.ta_sheets_info, self.ta_cycle_ranges, self.ta_frequency)
                message = "TA Excel processing completed" if success else "TA Excel processing failed"
        except Exception as e:
            print(f"[DEBUG] WorkerThread exception: {str(e)}")
            import traceback
            traceback.print_exc()
            message = f"Task failed with error: {str(e)}"
            success = False
        
        print(f"[DEBUG] WorkerThread finished: success={success}, message={message}")
        self.finished.emit(success, message)


class MainWindow(QMainWindow):
    __doc__ = "\n    Main application window for LAOS Analysis Data Analysis\n    "

    def __init__(self):
        print("[MainWindow] __init__ starting...")
        import traceback
        try:
            print("[MainWindow] Step 1: Calling super().__init__...")
            super().__init__()
            print("[MainWindow] Step 2: super().__init__ completed")
            
            print("[MainWindow] Step 3: Creating settings...")
            self.settings = get_settings()
            print("[MainWindow] Step 4: Settings created")
            
            print("[MainWindow] Step 5: Creating file_handler...")
            self.file_handler = FileHandler()
            print("[MainWindow] Step 6: file_handler created")
            
            print("[MainWindow] Step 7: Creating data_processor...")
            self.data_processor = DataProcessor()
            print("[MainWindow] Step 8: data_processor created")
            
            print("[MainWindow] Step 9: Creating plotter...")
            self.plotter = Plotter()
            print("[MainWindow] Step 10: plotter created")
            
            self.worker = None
            self._is_preprocessed = False
            self._preprocessed_frequency = None
            self._is_initializing = True
            self._processing_state = "no_folder"
            
            print("[MainWindow] Step 11: Setting up window...")
            self._setup_window()
            print("[MainWindow] Step 12: Window setup completed")
            
            print("[MainWindow] Step 13: Creating central widget...")
            self._create_central_widget()
            print("[MainWindow] Step 14: Central widget created")
            
            print("[MainWindow] Step 15: Central widget created (menu and toolbar built inline)")
            print("[MainWindow] Step 16: (skipped - menu now built in central widget)")
            print("[MainWindow] Step 17: (skipped - toolbar now built in central widget)")
            print("[MainWindow] Step 18: (skipped)")
            
            print("[MainWindow] Step 19: Creating status bar...")
            self._create_status_bar()
            print("[MainWindow] Step 20: Status bar created")
            
            print("[MainWindow] Step 21: Connecting signals...")
            self._connect_signals()
            print("[MainWindow] Step 22: Signals connected")
            
            print("[MainWindow] Step 23: Applying theme...")
            saved_theme = self.settings.get_theme()
            theme_manager = get_theme_manager()
            theme_manager.set_theme(saved_theme)
            apply_theme()
            print("[MainWindow] Step 24: Theme applied")

            print("[MainWindow] Step 24b: Applying saved interface font scale...")
            try:
                get_ui_scale().set_from_font_point_size(self.settings.get_font_size())
                self._apply_ui_scale_to_widgets()
                self._fit_splitter_to_content(initial=True)
                print("[MainWindow] Interface font scale applied")
            except Exception as e:
                print(f"[MainWindow] Failed to apply interface font scale: {e}")
            
            print("[MainWindow] Step 25: Loading last folder...")
            last_folder = self.settings.get_last_folder()
            if last_folder:
                if os.path.exists(last_folder):
                    self.file_selector.set_folder_path(last_folder)
            self._is_initializing = False
            print("[MainWindow] Step 26: Refreshing welcome panel translations...")
            if hasattr(self, "welcome_panel"):
                self.welcome_panel._refresh_ui()
            print("[MainWindow] Step 27: __init__ completed successfully")
            
        except Exception as e:
            print(f"[MainWindow] ERROR in __init__: {str(e)}")
            traceback.print_exc()
            raise

    def _setup_window(self):
        """Setup window properties with responsive sizing"""
        self.setWindowTitle(Config.WINDOW_TITLE)
        icon_path_png = os.path.join(get_app_path(), "resources", "icons", "icon_64.png")
        icon_path_svg = os.path.join(get_app_path(), "resources", "icons", "icon_64.svg")
        screen_info = get_screen_info()
        screen_width, screen_height = screen_info.screen_size
        if os.path.exists(icon_path_png):
            self.setWindowIcon(QIcon(icon_path_png))
        elif os.path.exists(icon_path_svg):
            self.setWindowIcon(QIcon(icon_path_svg))
        
        geometry = self.settings.get_window_geometry()
        if geometry["width"] > screen_width or geometry["height"] > screen_height:
            default_width, default_height = screen_info.get_default_window_size()
            screen_info.center_window(self, default_width, default_height)
        else:
            self.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])
        
        min_width = min(Config.WINDOW_MIN_WIDTH, int(screen_width * 0.6))
        min_height = min(Config.WINDOW_MIN_HEIGHT, int(screen_height * 0.6))
        self.setMinimumSize(min_width, min_height)
        if geometry.get("maximized", False):
            self.showMaximized()

    def _build_menu_bar_content(self):
        """Build menu bar content into the custom menu bar widget"""
        menubar = self._menu_bar
        
        # Debug: Check translator status at menu creation
        from utils.i18n import get_translator
        translator = get_translator()
        print(f"[DEBUG MENU] Creating menu bar")
        print(f"[DEBUG MENU] Current language: {translator.get_current_language()}")
        print(f"[DEBUG MENU] Translator has _ts_translator: {translator._ts_translator is not None}")
        if translator._ts_translator:
            print(f"[DEBUG MENU] Translation dict keys: {list(translator._ts_translator._translations.keys())[:5]}")
            if 'LAOSAnalysis' in translator._ts_translator._translations:
                trans_dict = translator._ts_translator._translations['LAOSAnalysis']
                print(f"[DEBUG MENU] LAOSAnalysis has {len(trans_dict)} translations")
                print(f"[DEBUG MENU] Sample translations: {list(trans_dict.items())[:3]}")
        
        file_menu = menubar.addMenu(tr("File", "LAOSAnalysis"))
        open_action = QAction(tr("Open Folder", "LAOSAnalysis"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_folder)
        file_menu.addAction(open_action)
        self.close_folder_action = QAction(tr("Close Folder", "LAOSAnalysis"), self)
        self.close_folder_action.setShortcut("Ctrl+W")
        self.close_folder_action.triggered.connect(self._on_close_folder)
        self.close_folder_action.setEnabled(False)
        file_menu.addAction(self.close_folder_action)
        self.recent_menu = file_menu.addMenu(tr("Recent Folders", "LAOSAnalysis"))
        self._update_recent_folders_menu()
        file_menu.addSeparator()
        export_png_action = QAction(tr("Export PNG", "LAOSAnalysis"), self)
        export_png_action.setShortcut("Ctrl+S")
        export_png_action.triggered.connect(lambda: self._export_plot("png"))
        file_menu.addAction(export_png_action)
        export_jpg_action = QAction(tr("Export JPG", "LAOSAnalysis"), self)
        export_jpg_action.triggered.connect(lambda: self._export_plot("jpg"))
        file_menu.addAction(export_jpg_action)
        export_svg_action = QAction(tr("Export SVG", "LAOSAnalysis"), self)
        export_svg_action.setShortcut("Ctrl+Shift+S")
        export_svg_action.triggered.connect(lambda: self._export_plot("svg"))
        file_menu.addAction(export_svg_action)
        export_html_action = QAction(tr("Export HTML (3D Plot)", "LAOSAnalysis"), self)
        export_html_action.triggered.connect(lambda: self._export_plot("html"))
        file_menu.addAction(export_html_action)
        file_menu.addSeparator()
        exit_action = QAction(tr("Exit", "LAOSAnalysis"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        edit_menu = menubar.addMenu(tr("Edit", "LAOSAnalysis"))
        plot_font_menu = edit_menu.addMenu(tr("Plot Font", "LAOSAnalysis"))
        self.title_font_action_group = QActionGroup(self)
        self.title_font_action_group.setExclusive(True)
        current_title_font = self.settings.get_plot_setting("title_font_size", 14)
        title_font_menu = plot_font_menu.addMenu(tr("Title Font Size", "LAOSAnalysis"))
        for size in [12, 14, 16, 18]:
            action = QAction(tr(f"{size}pt", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(size == current_title_font)
            action.triggered.connect(lambda _, s=size: self._set_plot_font_size("title", s))
            self.title_font_action_group.addAction(action)
            title_font_menu.addAction(action)
        self.label_font_action_group = QActionGroup(self)
        self.label_font_action_group.setExclusive(True)
        current_label_font = self.settings.get_plot_setting("label_font_size", 12)
        label_font_menu = plot_font_menu.addMenu(tr("Label Font Size", "LAOSAnalysis"))
        for size in [10, 12, 14, 16]:
            action = QAction(tr(f"{size}pt", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(size == current_label_font)
            action.triggered.connect(lambda _, s=size: self._set_plot_font_size("label", s))
            self.label_font_action_group.addAction(action)
            label_font_menu.addAction(action)
        self.legend_font_action_group = QActionGroup(self)
        self.legend_font_action_group.setExclusive(True)
        current_legend_font = self.settings.get_plot_setting("legend_font_size", 10)
        legend_font_menu = plot_font_menu.addMenu(tr("Legend Font Size", "LAOSAnalysis"))
        for size in [8, 10, 12, 14]:
            action = QAction(tr(f"{size}pt", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(size == current_legend_font)
            action.triggered.connect(lambda _, s=size: self._set_plot_font_size("legend", s))
            self.legend_font_action_group.addAction(action)
            legend_font_menu.addAction(action)
        self.annotation_font_action_group = QActionGroup(self)
        self.annotation_font_action_group.setExclusive(True)
        current_annotation_font = self.settings.get_plot_setting("annotation_font_size", 12)
        annotation_font_menu = plot_font_menu.addMenu(tr("Annotation Font Size", "LAOSAnalysis"))
        for size in [8, 10, 12, 14, 16, 18]:
            action = QAction(tr(f"{size}pt", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(size == current_annotation_font)
            action.triggered.connect(lambda _, s=size: self._set_plot_font_size("annotation", s))
            self.annotation_font_action_group.addAction(action)
            annotation_font_menu.addAction(action)
        self.font_family_action_group = QActionGroup(self)
        self.font_family_action_group.setExclusive(True)
        current_font_family = self.settings.get_plot_setting("font_family", "Times New Roman")
        font_family_menu = plot_font_menu.addMenu(tr("Font Family", "LAOSAnalysis"))
        for family in ["Times New Roman", "Arial", "SimHei", "Calibri", "Georgia", "Verdana", "Tahoma", "Palatino Linotype", "Cambria", "Courier New"]:
            action = QAction(tr(family, "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(family == current_font_family)
            action.triggered.connect(lambda _, f=family: self._set_plot_font_family(f))
            self.font_family_action_group.addAction(action)
            font_family_menu.addAction(action)
        edit_menu.addSeparator()
        plot_style_menu = edit_menu.addMenu(tr("Plot Style", "LAOSAnalysis"))
        self.line_width_action_group = QActionGroup(self)
        self.line_width_action_group.setExclusive(True)
        current_line_width = self.settings.get_plot_setting("line_width", 5)
        line_width_menu = plot_style_menu.addMenu(tr("Line Width", "LAOSAnalysis"))
        for width in [1, 2, 3, 4, 5, 6, 8, 10]:
            action = QAction(tr(f"{width}px", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(width == current_line_width)
            action.triggered.connect(lambda _, w=width: self._set_line_width(w))
            self.line_width_action_group.addAction(action)
            line_width_menu.addAction(action)
        self.marker_size_action_group = QActionGroup(self)
        self.marker_size_action_group.setExclusive(True)
        current_marker_size = self.settings.get_plot_setting("marker_size", 50)
        marker_size_menu = plot_style_menu.addMenu(tr("Marker Size", "LAOSAnalysis"))
        for size in [20, 50, 100, 150, 200]:
            action = QAction(tr(f"{size}", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(size == current_marker_size)
            action.triggered.connect(lambda _, s=size: self._set_marker_size(s))
            self.marker_size_action_group.addAction(action)
            marker_size_menu.addAction(action)
        self.marker_shape_action_group = QActionGroup(self)
        self.marker_shape_action_group.setExclusive(True)
        current_marker_shape = self.settings.get_plot_setting("marker_shape", "o")
        marker_shape_menu = plot_style_menu.addMenu(tr("Marker Shape", "LAOSAnalysis"))
        shape_circle_action = QAction(tr("Circle", "LAOSAnalysis"), self)
        shape_circle_action.setCheckable(True)
        shape_circle_action.setChecked(current_marker_shape == "o")
        shape_circle_action.triggered.connect(lambda: self._set_marker_shape("o"))
        self.marker_shape_action_group.addAction(shape_circle_action)
        marker_shape_menu.addAction(shape_circle_action)
        shape_square_action = QAction(tr("Square", "LAOSAnalysis"), self)
        shape_square_action.setCheckable(True)
        shape_square_action.setChecked(current_marker_shape == "s")
        shape_square_action.triggered.connect(lambda: self._set_marker_shape("s"))
        self.marker_shape_action_group.addAction(shape_square_action)
        marker_shape_menu.addAction(shape_square_action)
        shape_triangle_action = QAction(tr("Triangle", "LAOSAnalysis"), self)
        shape_triangle_action.setCheckable(True)
        shape_triangle_action.setChecked(current_marker_shape == "^")
        shape_triangle_action.triggered.connect(lambda: self._set_marker_shape("^"))
        self.marker_shape_action_group.addAction(shape_triangle_action)
        marker_shape_menu.addAction(shape_triangle_action)
        self.transparency_action_group = QActionGroup(self)
        self.transparency_action_group.setExclusive(True)
        current_transparency = self.settings.get_plot_setting("transparency", 0.8)
        transparency_menu = plot_style_menu.addMenu(tr("Transparency", "LAOSAnalysis"))
        for alpha in [0.2, 0.4, 0.6, 0.8, 1.0]:
            action = QAction(tr(f"{alpha}", "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(alpha == current_transparency)
            action.triggered.connect(lambda _, a=alpha: self._set_transparency(a))
            self.transparency_action_group.addAction(action)
            transparency_menu.addAction(action)
        edit_menu.addSeparator()
        colors_menu = edit_menu.addMenu(tr("Colors", "LAOSAnalysis"))
        self.colormap_action_group = QActionGroup(self)
        self.colormap_action_group.setExclusive(True)
        current_colormap = self.settings.get_plot_setting("colormap", "viridis")
        colormap_menu = colors_menu.addMenu(tr("Colormap", "LAOSAnalysis"))
        for cmap in ["viridis", "jet", "jet_r", "plasma", "cool", "hot", "rainbow", "autumn", "summer", "winter"]:
            action = QAction(tr(cmap, "LAOSAnalysis"), self)
            action.setCheckable(True)
            action.setChecked(cmap == current_colormap)
            action.triggered.connect(lambda _, c=cmap: self._set_colormap(c))
            self.colormap_action_group.addAction(action)
            colormap_menu.addAction(action)
        edit_menu.addSeparator()
        clear_action = QAction(tr("Clear All", "LAOSAnalysis"), self)
        clear_action.setShortcut("Ctrl+D")
        clear_action.triggered.connect(self._on_clear_all)
        edit_menu.addAction(clear_action)
        clear_log_action = QAction(tr("Clear Log", "LAOSAnalysis"), self)
        clear_log_action.setShortcut("Ctrl+L")
        clear_log_action.triggered.connect(self.log_panel.clear_log)
        edit_menu.addAction(clear_log_action)
        edit_menu.addSeparator()
        reset_preprocess_action = QAction(tr("Reset Preprocessing Data", "LAOSAnalysis"), self)
        reset_preprocess_action.setShortcut("Ctrl+R")
        reset_preprocess_action.triggered.connect(self._on_reset_preprocess)
        edit_menu.addAction(reset_preprocess_action)
        plot_menu = menubar.addMenu(tr("Plot", "LAOSAnalysis"))
        plot_lissajous_action = QAction(tr("Lissajous Curve", "LAOSAnalysis"), self)
        plot_lissajous_action.setShortcut("F9")
        plot_lissajous_action.triggered.connect(lambda: self._on_quick_plot_menu("1"))
        plot_menu.addAction(plot_lissajous_action)
        lissajous_overlay_menu = plot_menu.addMenu(tr("Lissajous Overlay", "LAOSAnalysis"))
        plot_3a_action = QAction(tr("3D Lissajous", "LAOSAnalysis"), self)
        plot_3a_action.triggered.connect(lambda: self._on_quick_plot_menu("3a"))
        lissajous_overlay_menu.addAction(plot_3a_action)
        plot_3b_action = QAction(tr("2D Elastic (σ-γ)", "LAOSAnalysis"), self)
        plot_3b_action.triggered.connect(lambda: self._on_quick_plot_menu("3b"))
        lissajous_overlay_menu.addAction(plot_3b_action)
        plot_3c_action = QAction(tr("2D Viscous (σ-γ̇)", "LAOSAnalysis"), self)
        plot_3c_action.triggered.connect(lambda: self._on_quick_plot_menu("3c"))
        lissajous_overlay_menu.addAction(plot_3c_action)
        plot_menu.addSeparator()
        plot_st_action = QAction(tr("S-T Values", "LAOSAnalysis"), self)
        plot_st_action.triggered.connect(lambda: self._on_quick_plot_menu("4"))
        plot_menu.addAction(plot_st_action)
        fourier_single_menu = plot_menu.addMenu(tr("Single-Order Fourier Coefficients", "LAOSAnalysis"))
        plot_6a_action = QAction(tr("In/I1 Ratio", "LAOSAnalysis"), self)
        plot_6a_action.triggered.connect(lambda: self._on_quick_plot_menu("6"))
        fourier_single_menu.addAction(plot_6a_action)
        plot_6q_action = QAction(tr("Q Value", "LAOSAnalysis"), self)
        plot_6q_action.triggered.connect(lambda: self._on_quick_plot_menu("6q"))
        fourier_single_menu.addAction(plot_6q_action)
        plot_fourier_multi_action = QAction(tr("Multi-Order Fourier Coefficients", "LAOSAnalysis"), self)
        plot_fourier_multi_action.triggered.connect(lambda: self._on_quick_plot_menu("5"))
        plot_menu.addAction(plot_fourier_multi_action)
        plot_menu.addSeparator()
        plot_dissipation_action = QAction(tr("Dissipation Rate", "LAOSAnalysis"), self)
        plot_dissipation_action.triggered.connect(lambda: self._on_quick_plot_menu("9"))
        plot_menu.addAction(plot_dissipation_action)
        plot_bifurcation_action = QAction(tr("Stress Bifurcation", "LAOSAnalysis"), self)
        plot_bifurcation_action.triggered.connect(lambda: self._on_quick_plot_menu("8"))
        plot_menu.addAction(plot_bifurcation_action)
        plot_menu.addSeparator()
        spp_menu = plot_menu.addMenu(tr("SPP Method", "LAOSAnalysis"))
        plot_7a_action = QAction(tr("Calculate & Plot", "LAOSAnalysis"), self)
        plot_7a_action.triggered.connect(lambda: self._on_quick_plot_menu("7a"))
        spp_menu.addAction(plot_7a_action)
        plot_7b_action = QAction(tr("Multi-File Overlay", "LAOSAnalysis"), self)
        plot_7b_action.triggered.connect(lambda: self._on_quick_plot_menu("7b"))
        spp_menu.addAction(plot_7b_action)
        cage_menu = plot_menu.addMenu(tr("Cage Modulus", "LAOSAnalysis"))
        plot_10a_action = QAction(tr("G'/G_cage vs Strain", "LAOSAnalysis"), self)
        plot_10a_action.triggered.connect(lambda: self._on_quick_plot_menu("10a"))
        cage_menu.addAction(plot_10a_action)
        plot_10b_action = QAction(tr("G_cage vs Strain", "LAOSAnalysis"), self)
        plot_10b_action.triggered.connect(lambda: self._on_quick_plot_menu("10b"))
        cage_menu.addAction(plot_10b_action)
        view_menu = menubar.addMenu(tr("View", "LAOSAnalysis"))
        reset_view_action = QAction(tr("Reset View / Auto Range", "LAOSAnalysis"), self)
        reset_view_action.setShortcut("Space")
        reset_view_action.triggered.connect(self._on_reset_view)
        view_menu.addAction(reset_view_action)
        show_data_action = QAction(tr("Show Plot Data", "LAOSAnalysis"), self)
        show_data_action.setShortcut("Ctrl+D")
        show_data_action.triggered.connect(self._on_show_plot_data)
        view_menu.addAction(show_data_action)
        view_menu.addSeparator()
        tab_analysis_action = QAction(tr("Analysis Tab", "LAOSAnalysis"), self)
        tab_analysis_action.setShortcut("Ctrl+Tab")
        tab_analysis_action.triggered.connect(lambda: self.plot_widget.set_current_tab(0))
        view_menu.addAction(tab_analysis_action)
        tab_3d_action = QAction(tr("3D Plot Tab", "LAOSAnalysis"), self)
        tab_3d_action.setShortcut("Ctrl+Shift+Tab")
        tab_3d_action.triggered.connect(lambda: self.plot_widget.set_current_tab(1))
        view_menu.addAction(tab_3d_action)
        help_menu = menubar.addMenu(tr("Help", "LAOSAnalysis"))
        about_action = QAction(tr("About", "LAOSAnalysis"), self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        manual_action = QAction(tr("User Manual", "LAOSAnalysis"), self)
        manual_action.setShortcut("F1")
        manual_action.triggered.connect(self._on_open_manual)
        help_menu.addAction(manual_action)
        help_menu.addSeparator()
        update_action = QAction(tr("Check for Updates", "LAOSAnalysis"), self)
        update_action.triggered.connect(self._on_check_updates)
        help_menu.addAction(update_action)
        settings_menu = menubar.addMenu(tr("Settings", "LAOSAnalysis"))
        theme_menu = settings_menu.addMenu(tr("Theme", "LAOSAnalysis"))
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)
        light_action = QAction(tr("Light", "Theme"), self)
        light_action.setCheckable(True)
        light_action.setChecked(self.settings.get_theme() == "light")
        light_action.triggered.connect(lambda: self._set_theme("light"))
        self.theme_action_group.addAction(light_action)
        theme_menu.addAction(light_action)
        dark_action = QAction(tr("Dark", "Theme"), self)
        dark_action.setCheckable(True)
        dark_action.setChecked(self.settings.get_theme() == "dark")
        dark_action.triggered.connect(lambda: self._set_theme("dark"))
        self.theme_action_group.addAction(dark_action)
        theme_menu.addAction(dark_action)
        settings_menu.addSeparator()
        lang_menu = settings_menu.addMenu(tr("Language", "LAOSAnalysis"))
        self.lang_action_group = QActionGroup(self)
        self.lang_action_group.setExclusive(True)
        current_lang = self.settings.get_language()
        languages = [
         (
          "auto", tr("Auto (System)", "Language")),
         ('en', 'English'),
         ('zh_CN', '中文'),
         ('ja', '日本語')]
        for code, name in languages:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(current_lang == code)
            action.triggered.connect(lambda _, c=code: self._change_language(c))
            self.lang_action_group.addAction(action)
            lang_menu.addAction(action)
        settings_menu.addSeparator()
        window_menu = settings_menu.addMenu(tr("Window Size", "LAOSAnalysis"))
        self.window_size_action_group = QActionGroup(self)
        self.window_size_action_group.setExclusive(True)
        
        window_sizes = [(1200, 800), (1400, 900), (1600, 1000)]
        geometry = self.settings.get_window_geometry()
        current_size = (geometry.get('width', 1400), geometry.get('height', 900))
        
        size_labels = [
            tr("Small (1200x800)", "LAOSAnalysis"),
            tr("Medium (1400x900)", "LAOSAnalysis"),
            tr("Large (1600x1000)", "LAOSAnalysis")
        ]
        
        for i, (width, height) in enumerate(window_sizes):
            action = QAction(size_labels[i], self)
            action.setCheckable(True)
            action.setChecked(current_size == (width, height))
            action.triggered.connect(lambda _, w=width, h=height: self._set_window_size(w, h))
            self.window_size_action_group.addAction(action)
            window_menu.addAction(action)
        
        window_max_action = QAction(tr("Maximize", "LAOSAnalysis"), self)
        window_max_action.triggered.connect(self.showMaximized)
        window_menu.addAction(window_max_action)
        
        settings_menu.addSeparator()
        interface_font_menu = settings_menu.addMenu(tr("Interface Font", "LAOSAnalysis"))
        self.interface_font_action_group = QActionGroup(self)
        self.interface_font_action_group.setExclusive(True)
        
        font_sizes = [8, 10, 12, 14]
        current_font_size = self.settings.get_font_size()
        
        font_labels = [
            tr("Small (8pt)", "LAOSAnalysis"),
            tr("Medium (10pt)", "LAOSAnalysis"),
            tr("Large (12pt)", "LAOSAnalysis"),
            tr("Extra Large (14pt)", "LAOSAnalysis")
        ]
        
        for i, size in enumerate(font_sizes):
            action = QAction(font_labels[i], self)
            action.setCheckable(True)
            action.setChecked(current_font_size == size)
            action.triggered.connect(lambda _, s=size: self._set_font_size(s))
            self.interface_font_action_group.addAction(action)
            interface_font_menu.addAction(action)
        settings_menu.addSeparator()
        show_hide_menu = settings_menu.addMenu(tr("Show/Hide", "LAOSAnalysis"))
        toolbar_action = QAction(tr("Toolbar", "LAOSAnalysis"), self)
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        toolbar_action.triggered.connect(self._toggle_toolbar)
        show_hide_menu.addAction(toolbar_action)
        menubar_action = QAction(tr("Menu Bar", "LAOSAnalysis"), self)
        menubar_action.setCheckable(True)
        menubar_action.setChecked(True)
        menubar_action.triggered.connect(self._toggle_menubar)
        show_hide_menu.addAction(menubar_action)
        statusbar_action = QAction(tr("Status Bar", "LAOSAnalysis"), self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self._toggle_statusbar)
        show_hide_menu.addAction(statusbar_action)
        left_panel_action = QAction(tr("File & Log Panel", "LAOSAnalysis"), self)
        left_panel_action.setCheckable(True)
        left_panel_action.setChecked(True)
        left_panel_action.triggered.connect(self._toggle_left_panel)
        show_hide_menu.addAction(left_panel_action)
        middle_panel_action = QAction(tr("Plot Panel", "LAOSAnalysis"), self)
        middle_panel_action.setCheckable(True)
        middle_panel_action.setChecked(True)
        middle_panel_action.triggered.connect(self._toggle_middle_panel)
        show_hide_menu.addAction(middle_panel_action)
        control_panel_action = QAction(tr("Control Panel", "LAOSAnalysis"), self)
        control_panel_action.setCheckable(True)
        control_panel_action.setChecked(True)
        control_panel_action.triggered.connect(self._toggle_control_panel)
        show_hide_menu.addAction(control_panel_action)
        logpanel_action = QAction(tr("Log Panel", "LAOSAnalysis"), self)
        logpanel_action.setCheckable(True)
        logpanel_action.setChecked(True)
        logpanel_action.triggered.connect(self._toggle_logpanel)
        show_hide_menu.addAction(logpanel_action)
        settings_menu.addSeparator()
        export_settings_action = QAction(tr("Export Settings", "LAOSAnalysis"), self)
        export_settings_action.triggered.connect(self._on_export_settings)
        settings_menu.addAction(export_settings_action)
        settings_menu.addSeparator()
        reset_action = QAction(tr("Reset Settings", "LAOSAnalysis"), self)
        reset_action.triggered.connect(self._on_reset_settings)
        settings_menu.addAction(reset_action)

    def _build_toolbar_content(self):
        """Build toolbar content into the custom toolbar widget"""
        toolbar = self._toolbar
        self.toolbar_open_btn = QAction(tr("Open Folder", "LAOSAnalysis"), self)
        self.toolbar_open_btn.setToolTip("Ctrl+O")
        self.toolbar_open_btn.triggered.connect(self._on_open_folder)
        toolbar.addAction(self.toolbar_open_btn)
        self.close_folder_toolbar_btn = QAction(tr("Close Folder", "LAOSAnalysis"), self)
        self.close_folder_toolbar_btn.setToolTip(tr("Return to initial screen (Ctrl+W)", "LAOSAnalysis"))
        self.close_folder_toolbar_btn.triggered.connect(self._on_close_folder)
        self.close_folder_toolbar_btn.setEnabled(False)
        toolbar.addAction(self.close_folder_toolbar_btn)
        toolbar.addSeparator()
        self.toolbar_process_btn = QAction(tr("Run Preprocess", "LAOSAnalysis"), self)
        self.toolbar_process_btn.setToolTip("F5")
        self.toolbar_process_btn.triggered.connect(self._on_run_preprocess)
        toolbar.addAction(self.toolbar_process_btn)
        self.toolbar_plot_btn = QAction(tr("Plot", "LAOSAnalysis"), self)
        self.toolbar_plot_btn.setToolTip("F9")
        self.toolbar_plot_btn.setShortcut("F9")
        self.toolbar_plot_btn.triggered.connect(self._on_quick_plot)
        toolbar.addAction(self.toolbar_plot_btn)
        toolbar.addSeparator()
        self.toolbar_export_btn = QAction(tr("Export PNG", "LAOSAnalysis"), self)
        self.toolbar_export_btn.setToolTip("Ctrl+S")
        self.toolbar_export_btn.triggered.connect(self._on_export_plot)
        toolbar.addAction(self.toolbar_export_btn)
        toolbar.addSeparator()
        self.toolbar_data_btn = QAction(tr("View Data", "LAOSAnalysis"), self)
        self.toolbar_data_btn.setToolTip(tr("Show plot data in table format", "LAOSAnalysis"))
        self.toolbar_data_btn.triggered.connect(self._on_show_plot_data)
        toolbar.addAction(self.toolbar_data_btn)

    def _create_central_widget(self):
        """Create the central widget with three-panel layout and resizable top area"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        screen_info = get_screen_info()
        margins = screen_info.get_margins()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(*margins)
        main_layout.setSpacing(0)

        self.v_splitter = QSplitter(Qt.Vertical)

        self.top_container = QWidget()
        top_layout = QVBoxLayout(self.top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        self._menu_bar = QMenuBar()
        self._menu_bar.setNativeMenuBar(False)
        self.setMenuBar(self._menu_bar)
        top_layout.addWidget(self._menu_bar)

        self._toolbar = QToolBar("Main Toolbar")
        self._toolbar.setMovable(False)
        top_layout.addWidget(self._toolbar)

        self.top_container.setMaximumHeight(get_ui_scale().scaled(200))
        self.v_splitter.addWidget(self.top_container)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(screen_info.get_spacing())

        self.h_splitter = QSplitter(Qt.Horizontal)
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.file_selector = FileSelector()
        left_layout.addWidget(self.file_selector)
        self.bottom_tabs = QTabWidget()
        self.log_panel = LogPanel()
        self.bottom_tabs.addTab(self.log_panel, tr("Log", "MainWindow"))
        self.history_panel = HistoryPanel()
        self.history_panel.redo_requested.connect(self._on_history_redo)
        self.bottom_tabs.addTab(self.history_panel, tr("History", "MainWindow"))
        left_layout.addWidget(self.bottom_tabs)
        self.h_splitter.addWidget(self.left_panel)
        self.middle_stack = QStackedWidget()
        self.welcome_panel = WelcomePanel()
        self.welcome_panel.open_folder_clicked.connect(self._on_open_folder)
        self.welcome_panel.tutorial_clicked.connect(self._on_open_manual)
        self.middle_stack.addWidget(self.welcome_panel)
        self.plot_widget = PlotWidgetContainer()
        self.middle_stack.addWidget(self.plot_widget)
        self.middle_stack.setCurrentIndex(0)
        self.h_splitter.addWidget(self.middle_stack)
        self.control_panel = ControlPanel()
        # Keep the analysis panel fully visible (no scrollbars) and never let
        # it be squeezed below its content, so text cannot overlap the borders.
        self.control_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.h_splitter.addWidget(self.control_panel)
        self.h_splitter.setStretchFactor(2, 0)
        self.h_splitter.setCollapsible(0, True)
        self.h_splitter.setCollapsible(1, True)
        self.h_splitter.setCollapsible(2, False)
        self.h_splitter.setSizes([280, 840, 320])
        content_layout.addWidget(self.h_splitter)

        self.v_splitter.addWidget(content_widget)
        self.v_splitter.setStretchFactor(0, 0)
        self.v_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(self.v_splitter)

        # Build menu bar and toolbar AFTER log_panel is created,
        # since _build_menu_bar_content connects to self.log_panel.clear_log.
        self._build_menu_bar_content()
        self._build_toolbar_content()

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel(tr("Ready", "StatusBar"))
        self.status_label.setMinimumWidth(get_ui_scale().scaled(200))
        self.status_bar.addWidget(self.status_label, 1)
        self.processing_label = QLabel("")
        self.processing_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.status_bar.addWidget(self.processing_label)
        self.status_bar.addWidget(QLabel(" | "))
        self.file_count_label = QLabel(tr("Files:", "StatusBar") + " 0")
        self.status_bar.addPermanentWidget(self.file_count_label)
        self.folder_label = QLabel(tr("Folder:", "StatusBar") + " -")
        self.folder_label.setMinimumWidth(get_ui_scale().scaled(150))
        self.status_bar.addPermanentWidget(self.folder_label)
        self.omega_label = QLabel("ω: -")
        self.status_bar.addPermanentWidget(self.omega_label)
        self.data_preview = DataPreviewDialog(self)
        self.data_preview.hide()

    def set_processing_status(self, status: str, active: bool=False):
        """
        Update processing status in status bar

        Args:
            status: Status message
            active: Whether processing is active
        """
        if active:
            self.processing_label.setText(f"⏳ {status}")
            self.processing_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            self.processing_label.setText("")
            self.status_label.setText(status)

    def _connect_signals(self):
        """Connect signals between components"""
        self.file_selector.folder_changed.connect(self._on_folder_changed)
        self.file_selector.file_selected.connect(self._on_file_selected)
        self.file_selector.preview_requested.connect(self._on_preview_file)
        self.file_selector.plot_requested.connect(self._on_plot_from_file_list)
        self.file_selector.double_click_plot.connect(self._on_quick_plot_from_file)
        self.file_selector.batch_plot_requested.connect(self._on_batch_plot)
        self.file_selector.keyboard_navigate.connect(self._on_keyboard_navigate)
        self.control_panel.run_preprocess.connect(self._on_run_preprocess)
        self.control_panel.run_step.connect(self._on_run_step)
        self.control_panel.plot_requested.connect(self._on_plot_requested)
        self.control_panel.cancel_requested.connect(self._on_cancel)
        self.control_panel.instrument_changed.connect(self._on_instrument_changed)
        self.control_panel.ta_excel_requested.connect(self._on_process_ta_excel)
        self.control_panel.log_requested.connect(self._on_log_message)
        self.data_processor.progress_updated.connect(self._on_progress_updated)
        self.data_processor.log_message.connect(self._on_log_message)
        self.plotter.plot_error.connect(self._on_plot_error)
        self.plotter.progress_updated.connect(self._on_progress_updated)
        self.plotter.log_message.connect(self._on_log_message)
        self.plotter.plot_data_ready.connect(self._on_plot_data_ready)

    def _on_open_folder(self):
        """Handle open folder action"""
        folder = QFileDialog.getExistingDirectory(self, "Select Data Folder", "", QFileDialog.ShowDirsOnly)
        if folder:
            self.file_selector.set_folder_path(folder)

    def _on_folder_changed(self, folder_path: str):
        """Handle folder change"""
        print(f"[DEBUG] _on_folder_changed called: folder_path={folder_path}")
        self.file_handler.set_folder_path(folder_path)
        self.data_processor.set_folder_path(folder_path)
        self.plotter.set_folder_path(folder_path)
        self._is_preprocessed = False
        self._preprocessed_frequency = None
        self.control_panel._preprocessed_frequency = None
        
        self.omega_label.setText("ω: - | f: -")
        self.control_panel.frequency_display_label.setVisible(False)
        
        fourier_folder = os.path.join(folder_path, "fourier_coefficients")
        if os.path.exists(fourier_folder) and os.path.isdir(fourier_folder):
            fourier_files = [f for f in os.listdir(fourier_folder) if f.endswith('.txt')]
            if len(fourier_files) > 0:
                cache_file = os.path.join(folder_path, ".laos_preprocessed.json")
                if os.path.exists(cache_file):
                    try:
                        import json
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                        cached_freq = cache_data.get('frequency')
                        if cached_freq and cached_freq > 0:
                            self._is_preprocessed = True
                            self._preprocessed_frequency = cached_freq
                            self.control_panel._preprocessed_frequency = cached_freq
                            omega = cached_freq * 2 * np.pi
                            self.omega_label.setText(f"ω: {omega:.4f} rad/s | f: {cached_freq:.2f} Hz")
                            self.plotter.set_omega(omega)
                            self.data_processor.omega = omega
                            self.data_processor.set_frequency(cached_freq)
                            self.control_panel.set_default_frequency(cached_freq)
                            self._processing_state = "ready"
                            self.log_panel.append_log(f"Preprocessed data detected, loaded cached frequency: {cached_freq:.2f} Hz", "INFO")
                            self.status_label.setText(tr("Preprocessed data loaded", "StatusBar"))
                    except Exception as e:
                        print(f"[DEBUG] Failed to load cache: {e}")
                        if not self._is_initializing:
                            self._prompt_frequency_for_preprocessed(folder_path)
                else:
                    if not self._is_initializing:
                        self._prompt_frequency_for_preprocessed(folder_path)
        
        print(f"[DEBUG] After check: _is_preprocessed={self._is_preprocessed}, _preprocessed_frequency={self._preprocessed_frequency}")
        self.settings.add_recent_folder(folder_path)
        self.settings.set_last_folder(folder_path)
        self._update_recent_folders_menu()
        folder_name = os.path.basename(folder_path)
        self.setWindowTitle(f"LAOS Analysis - {folder_name}")
        self.folder_label.setText(tr("Folder:", "StatusBar") + f" {folder_name}")
        valid, message = self.file_handler.validate_folder()
        if not self._is_preprocessed:
            self.status_label.setText(message)
        self.file_count_label.setText(f"Files: {self.file_handler.get_file_count()}")
        self.middle_stack.setCurrentIndex(1)
        self.close_folder_action.setEnabled(True)
        self.close_folder_toolbar_btn.setEnabled(True)
        self.log_panel.append_log(f"Folder loaded: {folder_path}", "INFO")
        if valid:
            self.log_panel.append_log(f"Found {self.file_handler.get_file_count()} data files", "INFO")
        else:
            self.log_panel.append_log(message, "WARNING")
    
    def _prompt_frequency_for_preprocessed(self, folder_path: str):
        """Prompt user to input frequency for already preprocessed data"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QDialogButtonBox, QFormLayout, QComboBox, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Input Frequency", "Messages"))
        dialog.setMinimumWidth(get_ui_scale().scaled(400))
        layout = QVBoxLayout(dialog)
        
        info_label = QLabel(tr("Preprocessed data detected in this folder.\nPlease enter the frequency used during preprocessing for ST/SPP calculation.", "Messages"))
        info_label.setStyleSheet("color: green;")
        layout.addWidget(info_label)
        
        form_layout = QFormLayout()
        
        freq_layout = QHBoxLayout()
        freq_spin = QDoubleSpinBox()
        freq_spin.setMinimum(0.01)
        freq_spin.setMaximum(1000)
        freq_spin.setValue(1.0)
        freq_spin.setDecimals(4)
        
        unit_combo = QComboBox()
        unit_combo.addItems(["Hz", "rad/s"])
        
        freq_layout.addWidget(freq_spin)
        freq_layout.addWidget(unit_combo)
        form_layout.addRow(QLabel(tr("Frequency:", "Messages")), freq_layout)
        layout.addLayout(form_layout)
        
        hint_label = QLabel(tr("Hint: input 1 means frequency is 1 Hz", "Messages"))
        hint_label.setStyleSheet(f"color: gray; font-size: {get_ui_scale().scaled(10)}px;")
        layout.addWidget(hint_label)
        
        skip_btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        skip_btn.accepted.connect(dialog.accept)
        skip_btn.rejected.connect(dialog.reject)
        layout.addWidget(skip_btn)
        
        if dialog.exec_() == QDialog.Accepted:
            freq_value = freq_spin.value()
            unit = unit_combo.currentText()
            
            if unit == "rad/s":
                omega = freq_value * np.pi
                frequency_hz = omega / (2 * np.pi)
            else:
                frequency_hz = freq_value
                omega = 2 * np.pi * freq_value
            
            self._is_preprocessed = True
            self._preprocessed_frequency = frequency_hz
            self.control_panel._preprocessed_frequency = frequency_hz
            self.plotter.set_omega(omega)
            self.data_processor.omega = omega
            self.data_processor.set_frequency(frequency_hz)
            self.control_panel.set_default_frequency(frequency_hz)
            self._processing_state = "ready"
            self.omega_label.setText(f"ω: {omega:.4f} rad/s | f: {frequency_hz:.2f} Hz")
            
            cache_file = os.path.join(folder_path, ".laos_preprocessed.json")
            try:
                import json
                with open(cache_file, 'w') as f:
                    json.dump({'frequency': frequency_hz}, f)
                self.log_panel.append_log(f"Frequency saved to cache: {frequency_hz:.2f} Hz", "INFO")
            except Exception as e:
                print(f"[DEBUG] Failed to save cache: {e}")
            
            self.log_panel.append_log(f"Frequency set: {frequency_hz:.2f} Hz, ready for ST/SPP calculation", "INFO")
            self.status_label.setText(tr("Preprocessed data loaded", "StatusBar"))

    def _on_close_folder(self):
        """Handle close folder action - return to welcome screen"""
        print("[DEBUG] _on_close_folder called")
        self.file_handler.folder_path = ""
        self.file_handler.txt_files = []
        self.file_handler.numbers_txt_files = []
        self.file_handler.excel_file = None
        self.data_processor.folder_path = ""
        self.data_processor.frequency = None
        self.data_processor.omega = None
        self.plotter.folder_path = ""
        self.plotter.omega = None
        self._is_preprocessed = False
        self._preprocessed_frequency = None
        self.control_panel._preprocessed_frequency = None
        self._processing_state = "no_folder"
        self.file_selector.clear()
        self.plot_widget.clear_all()
        self.log_panel.clear_log()
        self.setWindowTitle("LAOS Analysis")
        self.status_label.setText(tr("Ready", "StatusBar"))
        self.folder_label.setText(tr("Folder:", "StatusBar") + " -")
        self.file_count_label.setText(tr("Files:", "StatusBar") + " 0")
        self.omega_label.setText("ω: - | f: -")
        self.control_panel.frequency_display_label.setVisible(False)
        self.close_folder_action.setEnabled(False)
        self.close_folder_toolbar_btn.setEnabled(False)
        self.middle_stack.setCurrentIndex(0)
        if hasattr(self, "welcome_panel"):
            self.welcome_panel._refresh_ui()
        self.log_panel.append_log("Folder closed", "INFO")
        print("[DEBUG] _on_close_folder completed")

    def _on_file_selected(self, index: int):
        """Handle file selection"""
        file_path = self.file_selector.get_file_path(index)
        if file_path:
            self.status_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.control_panel.set_file_index(index)

    def _on_keyboard_navigate(self, index: int):
        """
        Handle keyboard navigation in file list
        Updates the file index parameter in real-time
        """
        self.control_panel.set_file_index(index)
        file_path = self.file_selector.get_file_path(index)
        if file_path:
            self.status_label.setText(f"Selected: {os.path.basename(file_path)}")

    def _on_quick_plot_from_file(self, index: int):
        """
        Handle double-click quick plot
        Directly plot Lissajous curve for the selected file
        """
        if not self._is_preprocessed:
            reply = QMessageBox.question(self, tr("Quick Plot", "Messages"), tr("Data has not been preprocessed. Run preprocessing first?\n\nNote: Without preprocessing, raw data will be displayed.", "Messages"), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Cancel:
                return
            if reply == QMessageBox.Yes:
                self.control_panel.set_file_index(index)
                self._on_run_preprocess()
                return
        self.control_panel.set_file_index(index)
        params = self.control_panel.get_parameters()
        if params:
            self._execute_plot("1", params)
            self.log_panel.append_log(f"Quick plot: file {index}", "INFO")

    def _on_quick_plot_menu(self, plot_type: str):
        """Handle quick plot from menu bar - show parameter dialog if needed"""
        if not self.file_handler.get_folder_path():
            QMessageBox.warning(self, tr("Warning", "Messages"), tr("Please select a folder first.", "Messages"))
            return
        
        required_params = self._get_required_params(plot_type)
        if required_params:
            dialog_params = self._show_param_dialog(plot_type, required_params)
            if dialog_params is None:
                return
        else:
            dialog_params = {}
        
        base_params = self._get_base_plot_params()
        base_params.update(dialog_params)
        base_params['plot_type'] = plot_type
        
        self._execute_plot(plot_type, base_params)
        self.log_panel.append_log(f"Quick plot: {plot_type}", "INFO")
    
    def _get_required_params(self, plot_type: str) -> list:
        """Get required parameters for plot type"""
        from ui.widgets.control_panel import PLOT_PARAM_MAP
        return PLOT_PARAM_MAP.get(plot_type, [])
    
    def _get_base_plot_params(self) -> dict:
        """Get base plot parameters from control panel"""
        params = {}
        params['colormap'] = self.control_panel.colormap_combo.currentData()
        if self.control_panel.marker_size_spin.isVisible():
            params['marker_size'] = self.control_panel.marker_size_spin.value()
        if self.control_panel.line_width_spin.isVisible():
            params['line_width'] = self.control_panel.line_width_spin.value()
        params['title_options'] = self.control_panel.get_title_options()
        return params
    
    def _show_param_dialog(self, plot_type: str, required_params: list) -> dict:
        """Show parameter input dialog for plot type"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QCheckBox, QDialogButtonBox, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Quick Plot", "Messages") + f" - {plot_type}")
        dialog.setMinimumWidth(get_ui_scale().scaled(350))
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        params = {}
        
        widgets = {}
        if "file_index" in required_params:
            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(999)
            spin.setValue(self.control_panel.get_file_index())
            form_layout.addRow(tr("File Index:", "ControlPanel"), spin)
            widgets["file_index"] = spin
        
        if "files_edit" in required_params:
            edit = QLineEdit()
            edit.setPlaceholderText(tr("e.g., 030,120,150", "ControlPanel"))
            edit.setText(self.control_panel.files_edit.text())
            form_layout.addRow(tr("Files:", "ControlPanel"), edit)
            widgets["files_edit"] = edit
        
        if "harmonics" in required_params:
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(50)
            spin.setValue(self.control_panel.harmonics_spin.value())
            form_layout.addRow(tr("Harmonics:", "ControlPanel"), spin)
            widgets["harmonics"] = spin
        
        if "max_harmonic" in required_params:
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(50)
            spin.setValue(self.control_panel.max_harmonic_spin.value())
            form_layout.addRow(tr("Max Harmonic (n):", "ControlPanel"), spin)
            widgets["max_harmonic"] = spin
        
        if "data_range" in required_params:
            combo = QComboBox()
            combo.addItems([tr("Full Data", "ControlPanel"), tr("First Half", "ControlPanel"), tr("Second Half", "ControlPanel")])
            combo.setCurrentIndex(self.control_panel.data_range_combo.currentIndex())
            form_layout.addRow(tr("Data Range:", "ControlPanel"), combo)
            widgets["data_range"] = combo
        
        if "use_normalized" in required_params:
            checkbox = QCheckBox()
            checkbox.setChecked(self.control_panel.use_normalized_checkbox.isChecked())
            form_layout.addRow(tr("Use Normalized Data", "ControlPanel"), checkbox)
            widgets["use_normalized"] = checkbox
        
        if "show_bifurcation" in required_params:
            checkbox = QCheckBox()
            checkbox.setChecked(self.control_panel.show_bifurcation_checkbox.isChecked())
            form_layout.addRow(tr("Show Bifurcation Point", "ControlPanel"), checkbox)
            widgets["show_bifurcation"] = checkbox
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            if "file_index" in widgets:
                params["file_index"] = widgets["file_index"].value()
            if "files_edit" in widgets:
                params["files_edit"] = widgets["files_edit"].text()
            if "harmonics" in widgets:
                params["harmonics"] = widgets["harmonics"].value()
            if "max_harmonic" in widgets:
                params["max_harmonic"] = widgets["max_harmonic"].value()
            if "data_range" in widgets:
                params["data_range"] = widgets["data_range"].currentIndex()
            if "use_normalized" in widgets:
                params["use_normalized"] = widgets["use_normalized"].isChecked()
            if "show_bifurcation" in widgets:
                params["show_bifurcation"] = widgets["show_bifurcation"].isChecked()
            return params
        return None

    def _on_preview_file(self, index: int):
        """Handle preview file request"""
        file_path = self.file_selector.get_file_path(index)
        if not file_path:
            return
        data = self.data_processor.load_txt_data(file_path)
        if data is not None:
            self.data_preview.show_data(file_path, data)

    def _on_plot_from_file_list(self, indices: list):
        """Handle plot request from file list context menu"""
        if not indices:
            return
        self.control_panel.set_file_index(indices[0])
        if len(indices) > 1:
            self.control_panel.files_edit.setText(",".join(map(str, indices)))
        params = self.control_panel.get_parameters()
        if params:
            plot_type = "3" if len(indices) > 1 else "1"
            self._execute_plot(plot_type, params)

    def _on_batch_plot(self, plot_type: str, indices: list):
        """
        Handle batch plot request

        Args:
            plot_type: Plot type code or 'individual' for separate plots
            indices: List of file indices to plot
        """
        if not indices:
            return
        elif plot_type == "individual":
            for idx in indices:
                self.control_panel.set_file_index(idx)
                params = self.control_panel.get_parameters()
                if params:
                    self._execute_plot("1", params)
                self.log_panel.append_log(f"Plotted {len(indices)} files", "INFO")

        else:
            self.control_panel.set_file_index(indices[0])
            self.control_panel.files_edit.setText(",".join(map(str, indices)))
            params = self.control_panel.get_parameters()
            if params:
                self._execute_plot(plot_type, params)

    def _on_run_preprocess(self):
        """Handle run full preprocess with frequency input"""
        print("[DEBUG] _on_run_preprocess called")
        folder_path = self.file_handler.get_folder_path()
        print(f"[DEBUG] folder_path from file_handler: {folder_path}")
        if not folder_path:
            QMessageBox.warning(self, "Warning", tr("Please select a folder first.", "Messages"))
            return
        
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QDialogButtonBox, QFormLayout, QComboBox, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Frequency Input", "Messages"))
        dialog.setMinimumWidth(get_ui_scale().scaled(450))
        layout = QVBoxLayout(dialog)
        
        info_label = QLabel(tr("Please enter the oscillation frequency of the experiment", "Messages"))
        layout.addWidget(info_label)
        
        form_layout = QFormLayout()
        
        freq_layout = QHBoxLayout()
        freq_spin = QDoubleSpinBox()
        freq_spin.setMinimum(0.01)
        freq_spin.setMaximum(1000)
        freq_spin.setValue(1.0)
        freq_spin.setDecimals(4)
        freq_spin.setToolTip(tr("Oscillation frequency value", "Messages"))
        
        unit_combo = QComboBox()
        unit_combo.addItems(["Hz", "rad/s"])
        unit_combo.setToolTip(tr("Select frequency unit: Hz or rad/s", "Messages"))
        
        def on_unit_changed(unit):
            if unit == "rad/s":
                hint_label.setText(tr("Hint: input angular frequency directly in rad/s", "Messages"))
            else:
                hint_label.setText(tr("Hint: input 1 means frequency is 1 Hz", "Messages"))
        
        unit_combo.currentTextChanged.connect(on_unit_changed)
        
        freq_layout.addWidget(freq_spin)
        freq_layout.addWidget(unit_combo)
        
        form_layout.addRow(QLabel(tr("Frequency:", "Messages")), freq_layout)
        layout.addLayout(form_layout)
        
        hint_label = QLabel(tr("Hint: input 1 means frequency is 1 Hz", "Messages"))
        hint_label.setStyleSheet(f"color: gray; font-size: {get_ui_scale().scaled(10)}px;")
        layout.addWidget(hint_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            freq_value = freq_spin.value()
            unit = unit_combo.currentText()
            
            if unit == "rad/s":
                omega = freq_value
                frequency_hz = omega / (2 * np.pi)
                self.log_panel.append_log(f"Input: ω = {omega:.4f} rad/s = {frequency_hz:.2f} Hz", "INFO")
            else:
                frequency_hz = freq_value
                omega = 2 * np.pi * freq_value
                self.log_panel.append_log(f"Input frequency: {frequency_hz:.2f} Hz = {omega:.4f} rad/s", "INFO")
            
            self.data_processor.set_folder_path(folder_path)
            self.data_processor.set_frequency(frequency_hz)
            print(f"[DEBUG] data_processor.folder_path: {self.data_processor.folder_path}")
            print(f"[DEBUG] frequency set to: {frequency_hz:.2f} Hz")
            
            self._start_worker("full")
        else:
            self.log_panel.append_log("Preprocessing cancelled by user", "INFO")

    def _on_run_step(self, step: str):
        """Handle run single step"""
        if not self.file_handler.get_folder_path():
            QMessageBox.warning(self, "Warning", tr("Please select a folder first.", "Messages"))
            return
        self._start_worker(step)
    
    def _on_process_ta_excel(self):
        """Handle TA Excel processing request with frequency input and cycle detection"""
        folder_path = self.file_handler.get_folder_path()
        if not folder_path:
            QMessageBox.warning(self, "Warning", tr("Please select a folder first.", "Messages"))
            return
        
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QDialogButtonBox, QFormLayout, QComboBox, QHBoxLayout
        
        # First scan Excel sheets
        self.data_processor.set_folder_path(folder_path)
        sheets_info = self.data_processor.scan_ta_excel_sheets()
        
        if not sheets_info:
            QMessageBox.warning(self, "Warning", tr("No valid 'Sine Strain' sheets found in Excel file.", "Messages"))
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("TA Excel Processing", "Messages"))
        dialog.setMinimumWidth(get_ui_scale().scaled(400))
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Frequency input with unit selection
        freq_layout = QHBoxLayout()
        freq_spin = QDoubleSpinBox()
        freq_spin.setMinimum(0.01)
        freq_spin.setMaximum(1000)
        freq_spin.setValue(1.0)
        freq_spin.setDecimals(4)
        
        unit_combo = QComboBox()
        unit_combo.addItems(["Hz", "rad/s"])
        
        def on_unit_changed(unit):
            if unit == "rad/s":
                hint_label.setText(tr("Hint: input angular frequency directly in rad/s", "Messages"))
            else:
                hint_label.setText(tr("Hint: input 1 means frequency is 1 Hz", "Messages"))
        
        unit_combo.currentTextChanged.connect(on_unit_changed)
        
        freq_layout.addWidget(freq_spin)
        freq_layout.addWidget(unit_combo)
        
        form_layout.addRow(QLabel(tr("Frequency:", "Messages")), freq_layout)
        layout.addLayout(form_layout)
        
        hint_label = QLabel(tr("Hint: input 1 means frequency is 1 Hz", "Messages"))
        hint_label.setStyleSheet(f"color: gray; font-size: {get_ui_scale().scaled(10)}px;")
        layout.addWidget(hint_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            freq_value = freq_spin.value()
            unit = unit_combo.currentText()
            
            # Calculate frequency in Hz
            if unit == "rad/s":
                omega = freq_value
                frequency_hz = omega / (2 * np.pi)
                self.log_panel.append_log(f"Input: ω = {omega:.4f} rad/s = {frequency_hz:.2f} Hz", "INFO")
            else:
                frequency_hz = freq_value
                omega = 2 * np.pi * freq_value
                self.log_panel.append_log(f"Input frequency: {frequency_hz:.2f} Hz = {omega:.4f} rad/s", "INFO")
            
            self._ta_excel_frequency = frequency_hz
            self._ta_excel_sheets_info = sheets_info
            self._ta_excel_cycle_ranges = None
            
            self._start_worker("ta_excel")
            self.log_panel.append_log(f"TA Excel processing started, frequency: {frequency_hz:.2f} Hz", "INFO")



    def _start_worker(self, task: str):
        """Start background worker thread"""
        self.control_panel.set_processing(True)
        self.set_processing_status((tr("Processing...", "StatusBar")), active=True)
        self.log_panel.append_log(f"Starting task: {task}", "INFO")
        if task == "ta_excel":
            self.worker = WorkerThread((self.data_processor),
              task, ta_sheets_info=(self._ta_excel_sheets_info),
              ta_cycle_ranges=(self._ta_excel_cycle_ranges),
              ta_frequency=(self._ta_excel_frequency))
        else:
            self.worker = WorkerThread(self.data_processor, task)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.log_message.connect(self._on_log_message)
        self.worker.finished.connect(self._on_task_finished)
        self.worker.start()

    def _on_task_finished(self, success: bool, message: str):
        """Handle task completion"""
        print(f"[DEBUG] _on_task_finished called: success={success}, message={message}")
        print(f"[DEBUG] Before update: _is_preprocessed={self._is_preprocessed}, _preprocessed_frequency={self._preprocessed_frequency}")
        self.control_panel.set_processing(False)
        self.control_panel.set_progress(100, message)
        self.set_processing_status("", active=False)
        self._processing_state = "ready" if success else "raw_data"
        if success:
            self._is_preprocessed = True
            self.log_panel.append_log(message, "INFO")
            freq_hz = self.data_processor.frequency
            omega = freq_hz * 2 * np.pi
            
            print(f"[DEBUG] Task finished: freq_hz = {freq_hz}")
            print(f"[DEBUG] Task finished: omega = {omega}")
            
            self.omega_label.setText(f"ω: {omega:.4f} rad/s | f: {freq_hz:.2f} Hz")
            self.plotter.set_omega(omega)
            self.data_processor.omega = omega
            
            self.control_panel.set_default_frequency(freq_hz)
            self._preprocessed_frequency = freq_hz
            
            cache_file = os.path.join(self.file_handler.get_folder_path(), ".laos_preprocessed.json")
            try:
                import json
                cache_data = {'frequency': freq_hz}
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f)
                self.log_panel.append_log(f"Preprocessing results cached to: {cache_file}", "INFO")
            except Exception as e:
                print(f"[DEBUG] Failed to save cache: {e}")
            
            print(f"[DEBUG] After update: _is_preprocessed={self._is_preprocessed}, _preprocessed_frequency={self._preprocessed_frequency}")
            print(f"[DEBUG] control_panel._preprocessed_frequency = {self.control_panel._preprocessed_frequency}")
            
            self.log_panel.append_log(f"Preprocessing frequency saved: {freq_hz:.2f} Hz", "INFO")
            self.log_panel.append_log(f"Control panel frequency auto-set to: {freq_hz:.2f} Hz", "INFO")
            self.status_label.setText(tr("Ready - Preprocessing complete", "StatusBar"))
            
            self.file_handler._scan_files()
            self.file_selector._load_files()
            self.file_count_label.setText(f"Files: {self.file_handler.get_file_count()}")
        else:
            self._is_preprocessed = False
            self.log_panel.append_log(message, "ERROR")
        self.worker = None

    def _on_progress_updated(self, value: int, message: str):
        """Handle progress update"""
        self.control_panel.set_progress(value, message)

    def _on_log_message(self, message: str):
        """Handle log message"""
        self.log_panel.append_log(message, "INFO")

    def _on_plot_requested(self, plot_type: str, params: dict):
        """Handle plot request"""
        print(f"[DEBUG] _on_plot_requested: plot_type={plot_type}, params={params}")
        if not self.file_handler.get_folder_path():
            print("[DEBUG] No folder path selected")
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return
        print(f"[DEBUG] Folder path: {self.file_handler.get_folder_path()}")
        self._execute_plot(plot_type, params)

    def _execute_plot(self, plot_type: str, params: dict):
        """Execute plotting based on plot type and parameters"""
        import numpy as np
        
        if not params:
            self.log_panel.append_log("No parameters provided", "ERROR")
            return
        
        folder_path = self.file_handler.get_folder_path()
        if not folder_path:
            QMessageBox.warning(self, "Warning", tr("Please select a folder first.", "Messages"))
            return
        
        # Get preprocessed frequency for ST and SPP calculations
        preprocessed_freq = self.control_panel.get_preprocessed_frequency()
        omega = preprocessed_freq * 2 * np.pi if preprocessed_freq else 2 * np.pi
        
        # For ST and SPP plots, use preprocessed frequency directly
        if plot_type in ('4', '7a', '7d', '7b'):
            print(f"[DEBUG] ST/SPP plot requested: preprocessed_freq={preprocessed_freq}, _is_preprocessed={self._is_preprocessed}")
            if preprocessed_freq is None:
                QMessageBox.warning(self, "Warning", tr("Please run preprocessing first to set frequency parameter.", "Messages"))
                return
            if not self._is_preprocessed:
                QMessageBox.warning(self, "Warning", tr("Data not preprocessed, cannot perform ST/SPP calculation.", "Messages"))
                return
            self.log_panel.append_log(f"Using preprocessed frequency: {preprocessed_freq:.2f} Hz (ω={omega:.4f} rad/s)", "INFO")
        
        self.plotter.set_folder_path(folder_path)
        self.plotter.set_colormap(params.get('colormap', 'viridis'))
        
        try:
            if plot_type == '1':
                file_index = params.get('file_index', 0)
                line_width = params.get('line_width', 3)
                txt_files = self.plotter._get_numbered_files()
                if file_index < len(txt_files):
                    data = self.plotter._load_data(txt_files[file_index])
                    if data is not None:
                        file_number = os.path.basename(txt_files[file_index]).replace('.txt', '')
                        self.plotter.plot_lissajous_3d_with_projections(
                            self.plot_widget.get_plotly_widget(),
                            self.plot_widget.get_projections_widget(), 
                            data, file_number, line_width)
                        self.plot_widget.set_current_tab(1)
                        self.log_panel.append_log(f"Lissajous 3D plotted: file {file_number}", "INFO")
            
            elif plot_type == '3a':
                files_str = params.get('files_edit', '')
                line_width = params.get('line_width', 3)
                if files_str:
                    file_indices = [int(x.strip()) for x in files_str.split(',')]
                    use_normalized = params.get('use_normalized', False)
                    title_opts = params.get('title_options', {})
                    
                    self.plotter.plot_multiple_lissajous_3d(
                        self.plot_widget.get_plotly_widget(),
                        self.plot_widget.get_projections_widget(),
                        file_indices,
                        legend_titles=title_opts.get('custom_titles'),
                        use_normalized=use_normalized,
                        line_width=line_width
                    )
                    self.plot_widget.set_current_tab(1)
                    norm_status = "normalized" if use_normalized else "original"
                    self.log_panel.append_log(f"3D Lissajous Overlay ({norm_status}): {len(file_indices)} files", "INFO")
            
            elif plot_type in ('3b', '3c'):
                files_str = params.get('files_edit', '')
                line_width = params.get('line_width', 10)
                if files_str:
                    file_indices = [int(x.strip()) for x in files_str.split(',')]
                    use_normalized = params.get('use_normalized', False)
                    title_opts = params.get('title_options', {})
                    self.plotter.plot_lissajous_projections_multi(
                        self.plot_widget.get_projections_widget(),
                        file_indices,
                        legend_titles=title_opts.get('custom_titles'),
                        use_normalized=use_normalized,
                        plot_subtype=plot_type,
                        line_width=line_width
                    )
                    self.plot_widget.set_current_tab(2)
                    subtype_name = "Elastic" if plot_type == '3b' else "Viscous"
                    norm_status = "normalized" if use_normalized else "original"
                    self.log_panel.append_log(f"{subtype_name} Lissajous Overlay ({norm_status}): {len(file_indices)} files", "INFO")
                self.log_panel.append_log(f"3D SPP + Frenet plotted: file {file_index}", "INFO")
            
            elif plot_type == '4':
                marker_size = params.get('marker_size', 50)
                self.plotter.plot_st_value(self.plot_widget.get_matplotlib_widget(), marker_size)
                self.plot_widget.set_current_tab(0)
                self.log_panel.append_log("ST values plotted", "INFO")
            
            elif plot_type == '5':
                files_str = params.get('files_edit', '')
                max_harmonic = params.get('max_harmonic', 30)
                line_width = params.get('line_width', 4)
                self.plotter.plot_fourier_multi(self.plot_widget.get_plotly_widget(), files_str, max_harmonic, line_width)
                self.plot_widget.set_current_tab(1)
            
            elif plot_type == '6':
                harmonic_n = params.get('harmonics', 3)
                marker_size = params.get('marker_size', 50)
                self.plotter.plot_fourier_coefficients(self.plot_widget.get_matplotlib_widget(), harmonic_n, marker_size)
                self.plot_widget.set_current_tab(0)
            
            elif plot_type == '6q':
                marker_size = params.get('marker_size', 50)
                self.plotter.plot_q_value(self.plot_widget.get_matplotlib_widget(), marker_size)
                self.plot_widget.set_current_tab(0)
            
            elif plot_type == '7a':
                file_index = params.get('file_index', 0)
                harmonics = params.get('harmonics', 15)
                data_range = params.get('data_range', 0)
                marker_size = params.get('marker_size', 50)
                self.plotter.set_omega(omega)
                self.plotter.plot_spp_method(self.plot_widget.get_matplotlib_widget(),
                                             file_index, harmonics, data_range, marker_size,
                                             method='fourier')
                self.plot_widget.set_current_tab(0)
                self.log_panel.append_log(f"SPP-Fourier plotted: file {file_index}", "INFO")

            elif plot_type == '7d':
                file_index = params.get('file_index', 0)
                harmonics = params.get('harmonics', 15)
                data_range = params.get('data_range', 0)
                marker_size = params.get('marker_size', 50)
                self.plotter.set_omega(omega)
                self.plotter.plot_spp_method(self.plot_widget.get_matplotlib_widget(),
                                             file_index, harmonics, data_range, marker_size,
                                             method='numerical')
                self.plot_widget.set_current_tab(0)
                self.log_panel.append_log(f"SPP-Derivative plotted: file {file_index}", "INFO")

            elif plot_type == '7b':
                files_str = params.get('files_edit', '')
                harmonics = params.get('harmonics', 15)
                data_range = params.get('data_range', 0)
                marker_size = params.get('marker_size', 50)
                self.plotter.set_omega(omega)
                title_opts = params.get('title_options', {})
                if files_str:
                    file_indices = [int(x.strip()) for x in files_str.split(',')]
                    self.plotter.plot_spp_multi(
                        self.plot_widget.get_matplotlib_widget(),
                        file_indices,
                        legend_titles=title_opts.get('custom_titles'),
                        harmonics=harmonics,
                        data_range=data_range,
                        marker_size=marker_size,
                        method='fourier'
                    )
                    self.plot_widget.set_current_tab(0)
                    self.log_panel.append_log(f"SPP Overlay: {len(file_indices)} files", "INFO")

            elif plot_type == '7c':
                file_index = params.get('file_index', 0)
                harmonics = params.get('harmonics', 15)
                data_range = params.get('data_range', 0)
                marker_size = params.get('marker_size', 50)
                component = params.get('decomp_component', 'Gt')
                self.plotter.set_omega(omega)
                self.plotter.plot_spp_circular_decomposition(
                    self.plot_widget.get_matplotlib_widget(),
                    file_index, component=component, harmonics=harmonics,
                    data_range=data_range, marker_size=marker_size,
                    method='fourier')
                self.plot_widget.set_current_tab(0)
                self.log_panel.append_log(
                    f"SPP Circular decomposition plotted: file {file_index} ({component})", "INFO")
            
            elif plot_type == '8':
                show_bifurcation = params.get('show_bifurcation', False)
                marker_size = params.get('marker_size', 70)
                self.plotter.plot_stress_bifurcation(self.plot_widget.get_matplotlib_widget(), show_bifurcation, marker_size)
                self.plot_widget.set_current_tab(0)

            elif plot_type == '9':
                marker_size = params.get('marker_size', 50)
                self.plotter.plot_dissipation_rate(self.plot_widget.get_matplotlib_widget(), marker_size)
                self.plot_widget.set_current_tab(0)
            
            elif plot_type in ['10', '10a', '10b']:
                marker_size = params.get('marker_size', 50)
                self.plotter.plot_cage_modulus(self.plot_widget.get_matplotlib_widget(), marker_size, plot_type)
                self.plot_widget.set_current_tab(0)
            
            self.history_panel.add_operation("plot", {'plot_type': plot_type, 'params': params}, f"Plot: {plot_type}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log_panel.append_log(f"Plot error: {str(e)}", "ERROR")
            QMessageBox.warning(self, "Plot Error", str(e))

    def _on_quick_plot(self):
        """Handle quick plot button"""
        params = self.control_panel.get_parameters()
        plot_type = self.control_panel.plot_type_combo.currentData()
        if plot_type == "7_menu":
            plot_type = self.control_panel.spp_combo.currentData()
        else:
            if plot_type == "10_menu":
                plot_type = self.control_panel.cage_modulus_combo.currentData()
        self._execute_plot(plot_type, params)

    def _on_instrument_changed(self, instrument_type: str):
        """Handle instrument type change"""
        self.data_processor.set_instrument_type(instrument_type)
        self.log_panel.append_log(f"Instrument type switched to: {instrument_type.upper()}", "INFO")

    def _on_cancel(self):
        """Handle cancel request"""
        if self.worker:
            if self.worker.isRunning():
                self.data_processor.cancel_processing()
                self.worker.terminate()
                self.control_panel.set_processing(False)
                self.log_panel.append_log("Processing cancelled", "WARNING")

    def _on_history_redo(self, operation_type: str, data: dict):
        """
        Handle redo request from history panel

        Args:
            operation_type: Type of operation to redo
            data: Operation data (params for plot, etc.)
        """
        if operation_type == "plot":
            plot_type = data.get("plot_type", "1")
            params = data.get("params", {})
            if "file_index" in params:
                self.control_panel.set_file_index(params["file_index"])
            if "harmonics" in params:
                self.control_panel.harmonics_spin.setValue(params["harmonics"])
            if "omega" in params:
                self.control_panel.omega_spin.setValue(params["omega"])
            if "file_indices" in params:
                self.control_panel.files_edit.setText(",".join(map(str, params["file_indices"])))
            self._execute_plot(plot_type, params)
            self.log_panel.append_log(f"Redo: {operation_type}", "INFO")

    def _on_export_plot(self):
        """Handle export plot"""
        self._export_plot("png")

    def _export_plot(self, format: str='png'):
        """
        Export current plot to file

        Args:
            format: Export format ('png', 'jpg', or 'svg')
        """
        if format == "png":
            self.plot_widget._export_png()
        elif format == "jpg":
            self.plot_widget._export_jpg()
        elif format == "svg":
            self.plot_widget._export_svg()

    def _update_recent_folders_menu(self):
        """Update the recent folders submenu"""
        self.recent_menu.clear()
        recent_folders = self.settings.get_recent_folders()
        if not recent_folders:
            no_recent = QAction(tr("No recent folders", "LAOSAnalysis"), self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            for folder in recent_folders:
                action = QAction(folder, self)
                action.triggered.connect(lambda _, f=folder: self.file_selector.set_folder_path(f))
                self.recent_menu.addAction(action)
            else:
                self.recent_menu.addSeparator()
                clear_action = QAction(tr("Clear Recent", "LAOSAnalysis"), self)
                clear_action.triggered.connect(self._clear_recent_folders)
                self.recent_menu.addAction(clear_action)

    def _clear_recent_folders(self):
        """Clear recent folders list"""
        self.settings.clear_recent_folders()
        self._update_recent_folders_menu()
        self.log_panel.append_log("Recent folders cleared", "INFO")

    def _on_clear_all(self):
        """Handle clear all with confirmation"""
        reply = QMessageBox.question(self, tr("Confirm Clear", "Messages"), tr("Are you sure you want to clear all plots and logs?", "Messages"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.plot_widget.clear_all()
            self.log_panel.clear_log()
            self.status_label.setText(tr("Ready", "StatusBar"))

    def _on_reset_preprocess(self):
        """Handle reset preprocess data - clear all generated files"""
        folder_path = self.file_handler.get_folder_path()
        if not folder_path:
            QMessageBox.warning(self, tr("Warning", "Messages"), tr("Please select a folder first.", "Messages"))
            return
        
        reply = QMessageBox.question(
            self, 
            tr("Confirm Reset", "Messages"), 
            tr("Are you sure you want to reset all processed data in the current folder?\nThis will delete:\n- fourier_coefficients folder\n- SPP Data folder\n- rebuild folder\n- ST.txt\n- stress_bifurcation.txt\n- file_titles.txt\n- Preprocessing cache file\n- Numbered data files (001.txt, etc.)\n- TA preprocessing files (01.txt, etc.)\n\nThis operation is irreversible.", "Messages"),
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            import shutil
            import glob
            
            deleted_items = []
            
            folders_to_delete = [
                ("fourier_coefficients", "fourier_coefficients folder"),
                ("SPP Data", "SPP Data folder"),
                ("rebuild", "rebuild folder")
            ]
            for folder_name, display_name in folders_to_delete:
                folder = os.path.join(folder_path, folder_name)
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                        deleted_items.append(display_name)
                    except Exception as e:
                        self.log_panel.append_log(f"Failed to delete {folder_name}: {str(e)}", "ERROR")
            
            files_to_delete = [
                ("ST.txt", "ST.txt"),
                ("stress_bifurcation.txt", "stress_bifurcation.txt"),
                ("file_titles.txt", "file_titles.txt"),
                (".laos_preprocessed.json", "preprocessing cache file")
            ]
            for file_name, display_name in files_to_delete:
                file_path = os.path.join(folder_path, file_name)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_items.append(display_name)
                    except Exception as e:
                        self.log_panel.append_log(f"Failed to delete {file_name}: {str(e)}", "ERROR")
            
            numbered_files = glob.glob(os.path.join(folder_path, "[0-9][0-9][0-9].txt"))
            if numbered_files:
                try:
                    for f in numbered_files:
                        os.remove(f)
                    deleted_items.append(f"{len(numbered_files)} numbered data files")
                except Exception as e:
                    self.log_panel.append_log(f"Failed to delete numbered files: {str(e)}", "ERROR")
            
            ta_txt_files = glob.glob(os.path.join(folder_path, "[0-9][0-9].txt"))
            if ta_txt_files:
                try:
                    for f in ta_txt_files:
                        os.remove(f)
                    deleted_items.append(f"{len(ta_txt_files)} TA preprocessing files")
                except Exception as e:
                    self.log_panel.append_log(f"Failed to delete TA preprocessing files: {str(e)}", "ERROR")
            
            self._is_preprocessed = False
            self._preprocessed_frequency = None
            self.control_panel._preprocessed_frequency = None
            self._processing_state = "raw_data"
            self.omega_label.setText("ω: - | f: -")
            self.control_panel.frequency_display_label.setVisible(False)
            
            self.file_handler._scan_files()
            self.file_selector._load_files()
            self.file_count_label.setText(f"Files: {self.file_handler.get_file_count()}")
            
            if deleted_items:
                self.log_panel.append_log(f"Processed data reset, deleted: {', '.join(deleted_items)}", "INFO")
                self.status_label.setText(tr("Processed data reset", "StatusBar"))
            else:
                self.log_panel.append_log("No processed data found to delete", "INFO")
                self.status_label.setText(tr("No processed data found", "StatusBar"))

    def _set_theme(self, theme_name: str):
        """
        Set application theme

        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        theme_manager = get_theme_manager()
        if theme_manager.set_theme(theme_name):
            self.settings.set_theme(theme_name)
            apply_theme()
            self.log_panel.append_log(f"Theme changed to: {theme_name}", "INFO")

    def _set_font_size(self, size: int):
        """
        Set application font size

        Args:
            size: Font size in points (8, 10, 12, 14)
        """
        ui_scale = get_ui_scale()
        ui_scale.set_from_font_point_size(size)

        self._apply_ui_scale_to_widgets()

        # Grow the window and fit the analysis panel's full content, but never
        # beyond the available screen so controls stay reachable.
        screen_info = get_screen_info()
        screen_width, screen_height = screen_info.screen_size
        scale = ui_scale.scale
        min_width = min(Config.WINDOW_MIN_WIDTH, int(screen_width * 0.6))
        min_height = min(Config.WINDOW_MIN_HEIGHT, int(screen_height * 0.6))
        self.setMinimumSize(
            min(min_width, int(900 * scale)),
            min(min_height, int(650 * scale)),
        )
        self._fit_splitter_to_content()
        self.settings.set_font_size(size)

        self.log_panel.append_log(f"Font size changed to: {size}pt", "INFO")

    def _fit_splitter_to_content(self, initial: bool = False):
        """Size the three panels so the analysis panel shows its full content.

        The analysis (control) panel keeps its complete width; the remaining
        space is shared between the left and middle panels, and the window is
        grown when needed (clamped to the available screen).
        """
        screen_info = get_screen_info()
        screen_width, screen_height = screen_info.screen_size
        scale = get_ui_scale().scale
        left_need, right_need = self._panel_minimum_widths()
        avail = int(screen_width * 0.98)
        mid_min = int(320 * scale)

        # Prefer the current window width; only grow when the analysis panel
        # does not fit, and never beyond the available screen.
        required = left_need + mid_min + right_need
        current_w = max(int(self.width()), self.minimumWidth())
        content_w = min(avail, max(current_w, required))
        remaining = max(0, content_w - right_need)
        left_w = min(remaining, max(left_need, int(remaining * 0.35)))
        mid_w = max(0, remaining - left_w)
        right_w = right_need

        # Vertical: make sure the whole analysis panel is visible (menu bar,
        # toolbar and status bar take some of the window height).
        chrome = 0
        for attr in ('_menu_bar', '_toolbar'):
            widget = getattr(self, attr, None)
            if widget is not None:
                chrome += widget.sizeHint().height()
        if hasattr(self, 'status_bar'):
            chrome += self.status_bar.sizeHint().height()
        panel_need_h = 0
        if hasattr(self, 'control_panel'):
            panel_need_h = self._fresh_panel_min_height(self.control_panel)
        # Add a safety margin: layouts can grow a few pixels more once the
        # window is resized, so a zero-margin exact fit can clip the last row.
        needed_h = panel_need_h + chrome + int(36 * scale)
        current_h = max(int(self.height()), self.minimumHeight())
        target_height = min(int(screen_height * 0.98), max(current_h, needed_h))

        # Guarantee the analysis panel is always fully visible: never allow the
        # window to be resized below the size its content needs (clamped to the
        # usable screen so the window can still be manipulated).
        self.setMinimumSize(min(required, avail),
                            min(needed_h, int(screen_height * 0.95)))

        if hasattr(self, 'h_splitter'):
            self.h_splitter.setSizes([left_w, mid_w, right_w])
        self.resize(max(self.minimumWidth(), content_w),
                    max(self.minimumHeight(), target_height))

    def _panel_minimum_widths(self):
        """Return the minimum widths needed by the left and analysis panels."""
        left_need = int(280 * get_ui_scale().scale)
        right_need = int(300 * get_ui_scale().scale)
        if hasattr(self, 'left_panel'):
            left_need = max(left_need, self.left_panel.minimumSizeHint().width())
        if hasattr(self, 'control_panel'):
            right_need = max(right_need, self._fresh_panel_size_hint(self.control_panel).width())
        return left_need, right_need

    @staticmethod
    def _fresh_panel_size_hint(widget):
        """Return an up-to-date size hint for a widget.

        Qt caches size hints and can report a stale value for one font step
        after a stylesheet change, so force a layout recalculation first.
        """
        try:
            widget.ensurePolished()
            layout = widget.layout()
            if layout is not None:
                layout.activate()
        except Exception:
            pass
        return widget.sizeHint()

    @staticmethod
    def _fresh_panel_min_height(widget):
        """Return an up-to-date minimum height for a widget."""
        try:
            widget.ensurePolished()
            layout = widget.layout()
            if layout is not None:
                layout.activate()
        except Exception:
            pass
        return widget.minimumSizeHint().height()

    def _apply_ui_scale_to_widgets(self):
        """Push the current UI scale into fonts, stylesheet and fixed sizes.

        Safe to call both at startup (after widgets exist) and whenever the
        interface font changes.
        """
        from PyQt5.QtWidgets import QApplication as _QApp
        from PyQt5.QtGui import QFont as _QFont
        ui_scale = get_ui_scale()
        font = _QFont("Segoe UI")
        font.setPointSizeF(ui_scale.font_point_size())
        font.setStyleStrategy(_QFont.PreferAntialias)
        font.setHintingPreference(_QFont.PreferFullHinting)
        app = _QApp.instance()
        if app is not None:
            app.setFont(font)
        self.setFont(font)

        # Regenerate the stylesheet from the new UI scale so every QSS
        # height/padding/font metric grows with the font and text no longer
        # overflows its container.
        apply_theme()

        # Rescale fixed-size widgets that live outside the stylesheet.
        ui_scale.refresh()
        self._apply_scaled_layout()

    def _apply_scaled_layout(self):
        """Re-apply scaled fixed layout metrics that Qt does not recompute."""
        ui_scale = get_ui_scale()
        if hasattr(self, 'top_container'):
            self.top_container.setMaximumHeight(ui_scale.scaled(200))
        if hasattr(self, 'status_label'):
            self.status_label.setMinimumWidth(ui_scale.scaled(200))
        if hasattr(self, 'folder_label'):
            self.folder_label.setMinimumWidth(ui_scale.scaled(150))
        if hasattr(self, 'control_panel'):
            self.control_panel.setMinimumWidth(self._fresh_panel_size_hint(self.control_panel).width())

    def _set_plot_font_size(self, font_type: str, size: int):
        """
        Set plot font size
        
        Args:
            font_type: 'title', 'label', or 'legend'
            size: Font size in points
        """
        print(f"[DEBUG] _set_plot_font_size called: font_type={font_type}, size={size}")
        from utils.plot_font import set_font_size_setting
        set_font_size_setting(font_type, size)
        self.settings.set_plot_setting(f"{font_type}_font_size", size)
        print(f"[DEBUG] Settings updated: {font_type}_font_size = {size}")
        try:
            self.log_panel.append_log(f"Plot {font_type} font size changed to: {size}pt", "INFO")
        except Exception as e:
            print(f"[DEBUG] log_panel.append_log failed: {e}")

    def _set_plot_font_family(self, family: str):
        """
        Set plot font family
        
        Args:
            family: Font family name (e.g., 'Times New Roman', 'Arial')
        """
        print(f"[DEBUG] _set_plot_font_family called: family={family}")
        from utils.plot_font import set_font_family_setting
        set_font_family_setting(family)
        self.settings.set_plot_setting("font_family", family)
        print(f"[DEBUG] Settings updated: font_family = {family}")
        try:
            self.log_panel.append_log(f"Plot font family changed to: {family}", "INFO")
        except Exception as e:
            print(f"[DEBUG] log_panel.append_log failed: {e}")

    def _set_line_width(self, width: int):
        """
        Set plot line width
        
        Args:
            width: Line width in pixels (1-10)
        """
        self.settings.set_plot_setting("line_width", width)
        self.control_panel.sync_from_menu_setting("line_width", width)
        self.log_panel.append_log(f"Line width changed to: {width}px", "INFO")

    def _set_marker_size(self, size: int):
        """
        Set marker size
        
        Args:
            size: Marker size (20-200)
        """
        self.settings.set_plot_setting("marker_size", size)
        self.control_panel.sync_from_menu_setting("marker_size", size)
        self.log_panel.append_log(f"Marker size changed to: {size}", "INFO")

    def _set_marker_shape(self, shape: str):
        """
        Set marker shape
        
        Args:
            shape: Marker shape ('o', 's', '^')
        """
        self.settings.set_plot_setting("marker_shape", shape)
        self.log_panel.append_log(f"Marker shape changed to: {shape}", "INFO")

    def _set_transparency(self, alpha: float):
        """
        Set plot transparency
        
        Args:
            alpha: Transparency value (0.0-1.0)
        """
        self.settings.set_plot_setting("transparency", alpha)
        self.log_panel.append_log(f"Transparency changed to: {alpha}", "INFO")

    def _set_colormap(self, cmap: str):
        """Set colormap for all plots"""
        self.settings.set_plot_setting("colormap", cmap)
        self.plotter.set_colormap(cmap)
        self.control_panel.sync_from_menu_setting("colormap", cmap)
        self.log_panel.append_log(f"Colormap changed to: {cmap}", "INFO")

    def _set_colormap_2d(self, cmap: str):
        """
        Set 2D colormap
        
        Args:
            cmap: Colormap name (e.g., 'viridis', 'jet')
        """
        self.settings.set_plot_setting("colormap_2d", cmap)
        self.log_panel.append_log(f"2D colormap changed to: {cmap}", "INFO")

    def _set_colormap_3d(self, cmap: str):
        """
        Set 3D colormap
        
        Args:
            cmap: Colormap name (e.g., 'viridis', 'jet_r')
        """
        self.settings.set_plot_setting("colormap_3d", cmap)
        self.log_panel.append_log(f"3D colormap changed to: {cmap}", "INFO")

    def _set_legend_position(self, position: str):
        """
        Set legend position
        
        Args:
            position: Legend position (e.g., 'upper right', 'upper left')
        """
        self.settings.set_plot_setting("legend_position", position)
        self.log_panel.append_log(f"Legend position changed to: {position}", "INFO")

    def _set_window_size(self, width: int, height: int):
        """
        Set window size
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.resize(width, height)
        self.settings.set_window_geometry(self.x(), self.y(), width, height, False)
        self.log_panel.append_log(f"Window size changed to: {width}x{height}", "INFO")

    def _toggle_toolbar(self):
        """Toggle toolbar visibility"""
        toolbar = self._toolbar
        if toolbar:
            toolbar.setVisible(not toolbar.isVisible())
            visible = "visible" if toolbar.isVisible() else "hidden"
            self.log_panel.append_log(f"Toolbar {visible}", "INFO")

    def _toggle_menubar(self):
        """Toggle menu bar visibility"""
        self._menu_bar.setVisible(not self._menu_bar.isVisible())
        visible = "visible" if self._menu_bar.isVisible() else "hidden"
        self.log_panel.append_log(f"Menu bar {visible}", "INFO")

    def _toggle_statusbar(self):
        """Toggle status bar visibility"""
        self.status_bar.setVisible(not self.status_bar.isVisible())
        visible = "visible" if self.status_bar.isVisible() else "hidden"
        self.log_panel.append_log(f"Status bar {visible}", "INFO")

    def _toggle_logpanel(self):
        """Toggle log panel visibility"""
        self.log_panel.setVisible(not self.log_panel.isVisible())
        visible = "visible" if self.log_panel.isVisible() else "hidden"
        self.log_panel.append_log(f"Log panel {visible}", "INFO")

    def _toggle_left_panel(self):
        """Toggle left panel (file selector + log) visibility"""
        self.left_panel.setVisible(not self.left_panel.isVisible())
        visible = "visible" if self.left_panel.isVisible() else "hidden"
        self.log_panel.append_log(f"File & Log panel {visible}", "INFO")

    def _toggle_middle_panel(self):
        """Toggle middle panel (plot widget) visibility"""
        self.middle_stack.setVisible(not self.middle_stack.isVisible())
        visible = "visible" if self.middle_stack.isVisible() else "hidden"
        self.log_panel.append_log(f"Plot panel {visible}", "INFO")

    def _toggle_control_panel(self):
        """Toggle control panel visibility"""
        target = self.control_panel
        target.setVisible(not target.isVisible())
        visible = "visible" if target.isVisible() else "hidden"
        self.log_panel.append_log(f"Control panel {visible}", "INFO")

    def _change_language(self, lang_code: str):
        """
        Change application language immediately

        Args:
            lang_code: Language code ('auto', 'en', 'zh_CN')
        """
        print(f"[DEBUG LANG] Changing language to: {lang_code}")
        self.settings.set_language(lang_code)
        from utils.i18n import get_translator
        translator = get_translator()
        print(f"[DEBUG LANG] Before load - current: {translator.get_current_language()}")
        translator.load_language(lang_code)
        print(f"[DEBUG LANG] After load - current: {translator.get_current_language()}")
        print(f"[DEBUG LANG] Translator has _ts_translator: {translator._ts_translator is not None}")
        self._refresh_ui_language()
        self.log_panel.append_log(f"Language changed to: {lang_code}", "INFO")

    def _refresh_ui_language(self):
        """Refresh all UI elements with new language"""
        print("[DEBUG REFRESH] Starting UI refresh")
        menubar = self._menu_bar
        menubar.clear()
        print("[DEBUG REFRESH] Menubar cleared, recreating...")
        self._build_menu_bar_content()
        print("[DEBUG REFRESH] Menu bar recreated")
        self._refresh_toolbar()
        self.control_panel._refresh_ui()
        self._refresh_status_bar()
        if hasattr(self, "welcome_panel"):
            self.welcome_panel._refresh_ui()
        self.file_selector._refresh_ui()
        print("[DEBUG REFRESH] UI refresh completed")

    def _refresh_toolbar(self):
        """Refresh toolbar button text with new translations"""
        if hasattr(self, "toolbar_open_btn"):
            self.toolbar_open_btn.setText(tr("Open Folder", "LAOSAnalysis"))
        if hasattr(self, "close_folder_toolbar_btn"):
            self.close_folder_toolbar_btn.setText(tr("Close Folder", "LAOSAnalysis"))
            self.close_folder_toolbar_btn.setToolTip(tr("Return to initial screen (Ctrl+W)", "LAOSAnalysis"))
        if hasattr(self, "toolbar_process_btn"):
            self.toolbar_process_btn.setText(tr("Run Preprocess", "LAOSAnalysis"))
        if hasattr(self, "toolbar_plot_btn"):
            self.toolbar_plot_btn.setText(tr("Plot", "LAOSAnalysis"))
        if hasattr(self, "toolbar_export_btn"):
            self.toolbar_export_btn.setText(tr("Export PNG", "LAOSAnalysis"))
        if hasattr(self, "toolbar_data_btn"):
            self.toolbar_data_btn.setText(tr("View Data", "LAOSAnalysis"))
            self.toolbar_data_btn.setToolTip(tr("Show plot data in table format", "LAOSAnalysis"))

    def _refresh_status_bar(self):
        """Refresh status bar text"""
        self.status_label.setText(tr("Ready", "StatusBar"))
        self.file_count_label.setText(tr("Files:", "StatusBar") + " 0")
        self.folder_label.setText(tr("Folder:", "StatusBar") + " -")

    def _on_reset_settings(self):
        """Handle reset settings request"""
        reply = QMessageBox.question(self, tr("Reset Settings", "Messages"), tr("Are you sure you want to reset all settings to defaults?", "Messages"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.settings.reset_to_defaults()
            self.log_panel.append_log("Settings reset to defaults", "INFO")
            QMessageBox.information(self, tr("Settings Reset", "Messages"), tr("Settings have been reset. Please restart the application.", "Messages"))

    def _on_export_settings(self):
        """Handle export settings request"""
        from ui.dialogs.export_settings_dialog import ExportSettingsDialog
        dialog = ExportSettingsDialog(self)
        dialog.exec_()

    def _on_reset_view(self):
        """Handle reset view"""
        self.plot_widget._auto_range()

    def _on_show_plot_data(self):
        """Handle show plot data action - switch to Data Table tab"""
        self.plot_widget.set_current_tab(3)

    def _on_plot_data_ready(self, data_type: str, data_dict: dict):
        """Handle plot data ready signal - display data in table"""
        print(f"[DEBUG] Plot data ready: type={data_type}")
        data_table = self.plot_widget.get_data_table_widget()
        
        if data_type == "lissajous":
            data_table.show_lissajous_data(data_dict["file_number"], data_dict["data"])
        elif data_type == "st_values":
            data_table.show_st_values(data_dict["strain"], data_dict["S"], data_dict["T"], 
                                     data_dict.get("G_l"), data_dict.get("G_m"), 
                                     data_dict.get("eta_l"), data_dict.get("eta_m"))
        elif data_type == "spp":
            data_table.show_spp_data(data_dict["file_number"], data_dict["data"])
        elif data_type == "spp_circular":
            data_table.show_spp_circular_data(
                data_dict["file_number"], data_dict.get("component", "Gt"),
                data_dict["components"], data_dict.get("mean"), data_dict.get("residual", 0.0))
        elif data_type == "stress_bifurcation":
            data_table.show_stress_bifurcation(data_dict["sigma_0"], data_dict["gamma_0"], 
                                               data_dict["gamma_dot_0"], data_dict["gamma_sigma_0"], 
                                               data_dict["sigma_gamma_0"], data_dict["sigma_gamma_dot_0"], 
                                               data_dict["gamma_dot_sigma_0"])
        elif data_type == "dissipation_rate":
            data_table.show_dissipation_rate(data_dict["strain"], data_dict["dissipation"])
        elif data_type == "cage_modulus":
            data_table.show_cage_modulus(data_dict["strain"], data_dict["G_ratio"])
        elif data_type == "fourier_ratio":
            data_table.show_fourier_ratio(data_dict["strain"], data_dict["ratio"], data_dict["n"])
        elif data_type == "fourier_multi":
            data_table.show_fourier_multi_data(data_dict["data"], data_dict["max_harmonic"])
        elif data_type == "q_value":
            data_table.show_q_value(data_dict["strain"], data_dict["q_value"])
        elif data_type == "different_strain_in_i1":
            data_table.show_different_strain_in_i1(data_dict["strains"], data_dict["ratios"], data_dict["n"])
        
        self.plot_widget.set_current_tab(3)

    def _on_plot_error(self, message: str):
        """Handle plot error"""
        QMessageBox.warning(self, "Plot Error", message)
        self.log_panel.append_log(message, "ERROR")

    def _on_about(self):
        """Handle about dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QScrollArea, QWidget
        from PyQt5.QtGui import QPixmap
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("About LAOS Analysis", "About"))
        dialog.setMinimumSize(550, 600)
        
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        
        logo_path_png = os.path.join(get_app_path(), "resources", "icons", "icon_128.png")
        logo_path_svg = os.path.join(get_app_path(), "resources", "icons", "logo.svg")
        logo_label = QLabel()
        logo_loaded = False
        if os.path.exists(logo_path_png):
            pixmap = QPixmap(logo_path_png)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
            logo_loaded = True
        elif os.path.exists(logo_path_svg):
            pixmap = QPixmap(logo_path_svg)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
            logo_loaded = True
        
        title = QLabel(f'<h2><b>{tr("LAOS Analysis Software", "About")}</b></h2>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel(f'<h3>{tr("Version", "About")}: v1.0</h3>')
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(15)
        
        team_title = QLabel(f'<h3><b>{tr("Development Team", "About")}:</b></h3>')
        team_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(team_title)
        
        team_name = tr("Institute of Rheology, Shanghai Jiao Tong University", "About")
        team_content = QLabel(f'<h4>{team_name}</h4>')
        team_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(team_content)
        
        layout.addSpacing(15)
        
        author_title = QLabel(f'<h3><b>{tr("Authors", "About")}:</b></h3>')
        author_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_title)
        
        author_name = tr("Ziyu Zhou, Hongbin Zhang", "About")
        author_content = QLabel(f'<h4>{author_name}</h4>')
        author_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_content)
        
        layout.addSpacing(15)
        
        contact_title = QLabel(f'<h3><b>{tr("Contact", "About")}:</b></h3>')
        contact_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact_title)
        
        contact_email = QLabel(f'<h4>hbzhang@sjtu.edu.cn</h4>')
        contact_email.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact_email)
        
        layout.addSpacing(15)
        
        tech_title = QLabel(f'<h3><b>{tr("Technology", "About")}:</b></h3>')
        tech_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(tech_title)
        
        tech = QLabel(f'<h4>PyQt5, PyQtGraph, NumPy, Matplotlib, Plotly</h4>')
        tech.setAlignment(Qt.AlignCenter)
        layout.addWidget(tech)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        main_layout.addWidget(button_box)
        dialog.exec_()

    def _on_open_manual(self):
        """Open user manual PDF based on current language"""
        import subprocess
        import platform
        from utils.i18n import get_translator
        
        translator = get_translator()
        current_lang = translator.get_current_language()
        
        if current_lang == 'zh_CN':
            manual_filename = 'manual_zh_CN.pdf'
        elif current_lang == 'ja':
            manual_filename = 'manual_en.pdf'
        else:
            manual_filename = 'manual_en.pdf'
        
        manual_path = os.path.join(get_app_path(), "resources", "docs", manual_filename)
        
        if not os.path.exists(manual_path):
            QMessageBox.warning(self, tr("Error", "Messages"), tr("User manual not found.", "Messages"))
            return
        
        try:
            if platform.system() == 'Windows':
                os.startfile(manual_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', manual_path])
            else:
                subprocess.run(['xdg-open', manual_path])
        except Exception as e:
            QMessageBox.warning(self, tr("Error", "Messages"), tr("Failed to open user manual.", "Messages"))

    def _on_check_updates(self):
        """Handle check for updates"""
        QMessageBox.information(self, tr("Check for Updates", "Messages"), tr("Current version: 1.0.0\n\nPlease visit the GitHub repository to check for the latest version.", "Messages"))

    def closeEvent(self, event):
        """Handle window close event"""
        if self.worker:
            if self.worker.isRunning():
                reply = QMessageBox.question(self, tr("Processing in Progress", "Messages"), tr("Processing is still running. Cancel and exit?", "Messages"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.data_processor.cancel_processing()
                    self.worker.terminate()
                else:
                    event.ignore()
                    return
        if not self.isMaximized():
            self.settings.set_window_geometry(self.x(), self.y(), self.width(), self.height(), self.isMaximized())
        plot_type = self.control_panel.plot_type_combo.currentData()
        if plot_type:
            self.settings.set_last_plot_type(plot_type)
        event.accept()
