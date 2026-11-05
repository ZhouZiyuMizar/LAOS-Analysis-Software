"""
PlotWidget - PyQt5 widget for plotting
"""
import os
import sys
import numpy as np
from typing import Optional, List

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QFileDialog, QToolBar, QAction, QLabel, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont
import pyqtgraph as pg
from pyqtgraph import PlotWidget

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    print(f"Warning: PyQtWebEngine not available: {e}")

from utils.i18n import tr
from utils.settings import get_settings
from utils.responsive import get_ui_scale
from utils.plot_font import get_legend_fontdict
import plotly.graph_objects as go
import plotly.io as pio


class PlotlyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if not WEBENGINE_AVAILABLE:
            layout = QVBoxLayout(self)
            error_label = QLabel("PyQtWebEngine not installed.\n3D Plotly unavailable.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet(f"color: red; font-size: {get_ui_scale().scaled(14)}px;")
            layout.addWidget(error_label)
            self.web_view = None
            self._current_figure = None
            return
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.web_view.setHtml("<html><body style='background: white;'></body></html>")
        self._current_figure = None
    
    def set_plotly_figure(self, fig):
        if self.web_view is None:
            return
        self._current_figure = fig
        html = pio.to_html(fig, full_html=True, include_plotlyjs="cdn")
        self.web_view.setHtml(html)
    
    def clear_plot(self):
        if self.web_view is None:
            return
        self._current_figure = None
        self.web_view.setHtml("<html><body style='background: white;'></body></html>")
    
    def plot_lissajous_3d(self, strain, stress, strain_rate, title="Lissajous 3D", colormap='viridis', line_width=5):
        if self.web_view is None:
            return
        import plotly.graph_objects as go
        import numpy as np
        
        plotly_colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'greys', 'purples', 'blues', 
                           'greens', 'oranges', 'reds', 'ylorbr', 'ylorrd', 'ylgn', 'ylgnbu', 'gnbu', 
                           'pubu', 'pubugn', 'bugn', 'bupu', 'rdpu', 'purd', 'orrd', 'purp', 'purpor',
                           'hot', 'gray', 'haline', 'jet', 'rainbow', 'turbo', 'twilight', 'spectral',
                           'rdbu', 'rdgy', 'rdylbu', 'rdylgn', 'piyg', 'prgn', 'brbg', 'puor', 'sunset',
                           'sunsetdark', 'teal', 'tealgrn', 'tealrose', 'tempo', 'temps', 'thermal', 
                           'tropic', 'turbid', 'ice', 'icefire', 'emrld', 'mint', 'matter', 'electric',
                           'fall', 'geyser', 'deep', 'dense', 'delta', 'curl', 'blackbody', 'edge',
                           'speed', 'phase', 'peach', 'pinkyl', 'oryel', 'oxy', 'aggrnyl', 'agsunset',
                           'algae', 'amp', 'armyrose', 'balance', 'bluered', 'blugrn', 'bluyl', 'brwnyl',
                           'bugn', 'burg', 'burgyl', 'darkmint', 'earth', 'hsv', 'magenta', 'picnic',
                           'portland', 'redor', 'solar']
        
        cmap_lower = colormap.lower().rstrip('_r')
        plotly_cmap = cmap_lower
        if cmap_lower not in plotly_colormaps:
            cmap_mapping = {
                'greys': 'greys', 'purples': 'purples', 'blues': 'blues', 'greens': 'greens',
                'oranges': 'oranges', 'reds': 'reds', 'gray': 'gray', 'grey': 'greys',
                'bone': 'greys', 'gist_gray': 'gray', 'gist_yarg': 'gray', 'binary': 'greys',
                'pink': 'pinkyl', 'spring': 'rainbow', 'summer': 'ylgn', 'autumn': 'ylorrd',
                'winter': 'blues', 'cool': 'teal', 'wistia': 'oranges', 'afmhot': 'hot',
                'gist_heat': 'hot', 'copper': 'hot', 'seismic': 'rdbu', 'coolwarm': 'rdbu',
                'bwr': 'rdbu', 'twilight_shifted': 'twilight', 'spectral': 'spectral',
                'rdylgn': 'rdylgn', 'rdylbu': 'rdylbu', 'rdgy': 'rdgy', 'rdbu': 'rdbu',
                'puor': 'puor', 'prgn': 'prgn', 'piyg': 'piyg', 'brbg': 'brbg',
                'ylgnbu': 'ylgnbu', 'ylorbr': 'ylorbr', 'ylorrd': 'ylorrd', 'ylgn': 'ylgn',
                'pubu': 'pubu', 'pubugn': 'pubugn', 'bugn': 'bugn', 'bupu': 'bupu',
                'gnbu': 'gnbu', 'orrd': 'orrd', 'rdpu': 'rdpu', 'purd': 'purd',
                'purp': 'purp', 'purpor': 'purpor', 'purples': 'purples',
                'terrain': 'earth', 'gist_earth': 'earth', 'ocean': 'deep',
                'cubehelix': 'viridis', 'gnuplot': 'hot', 'gnuplot2': 'jet',
                'cmrmap': 'matter', 'flag': 'rainbow', 'prism': 'rainbow',
                'brg': 'rainbow', 'gist_rainbow': 'rainbow', 'gist_stern': 'haline',
                'hsv': 'hsv', 'tab10': 'plotly3', 'tab20': 'plotly3', 'paired': 'plotly3'
            }
            plotly_cmap = cmap_mapping.get(cmap_lower, 'viridis')
        
        if colormap.endswith('_r'):
            plotly_cmap = plotly_cmap + '_r'
        
        strain_norm = (strain - strain.min()) / (strain.max() - strain.min())
        
        fig = go.Figure()
        
        # Further performance optimization: reduce sampling points from 500 to 250
        if len(strain) > 250:
            sample_idx = np.linspace(0, len(strain)-1, 250, dtype=int)
            strain_plot = strain[sample_idx]
            strain_rate_plot = strain_rate[sample_idx]
            stress_plot = stress[sample_idx]
            strain_norm_plot = strain_norm[sample_idx]
        else:
            strain_plot = strain
            strain_rate_plot = strain_rate
            stress_plot = stress
            strain_norm_plot = strain_norm
        
        fig.add_trace(go.Scatter3d(
            x=strain_plot,
            y=strain_rate_plot,
            z=stress_plot,
            mode='lines',
            line=dict(
                width=line_width,
                color=strain_norm_plot,
                colorscale=plotly_cmap,
                showscale=True,
                colorbar=dict(title='Strain', thickness=10, len=0.8)
            ),
            hovertemplate='Strain: %{x:.3f}<br>Strain Rate: %{y:.3f}<br>Stress: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='Strain'),
                yaxis=dict(title='Strain Rate (s⁻¹)'),
                zaxis=dict(title='Stress (Pa)'),
                aspectmode='auto'
            ),
            title=title,
            font=dict(family='Times New Roman', size=14),
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        self.set_plotly_figure(fig)
    
    def plot_lissajous_3d_multi(self, data_list, legend_titles, colormap='viridis', line_width=5):
        if self.web_view is None:
            return
        import plotly.graph_objects as go
        import numpy as np
        from matplotlib import cm as mpl_cm
        import matplotlib.pyplot as plt
        
        cmap = mpl_cm.get_cmap(colormap)
        curve_colors = cmap(np.linspace(0.1, 0.9, len(data_list)))
        
        fig = go.Figure()
        
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 3:
                continue
            
            if data.dtype.kind in ('U', 'S', 'O'):
                data = np.asarray(data, dtype=np.float64)
            
            time = data[:, 0]
            stress = data[:, 1]
            strain = data[:, 2]
            strain_rate = data[:, 3] if data.shape[1] > 3 else np.gradient(strain, time)
            
            # Further performance optimization: reduce sampling points from 300 to 150
            if len(strain) > 150:
                sample_idx = np.linspace(0, len(strain)-1, 150, dtype=int)
                strain = strain[sample_idx]
                strain_rate = strain_rate[sample_idx]
                stress = stress[sample_idx]
            
            color_hex = '#{:02x}{:02x}{:02x}'.format(
                int(curve_colors[i][0] * 255),
                int(curve_colors[i][1] * 255),
                int(curve_colors[i][2] * 255)
            )
            
            hover_text = title + '<br>Strain: %{x:.3f}<br>Strain Rate: %{y:.3f}<br>Stress: %{z:.3f}<extra></extra>'
            
            fig.add_trace(go.Scatter3d(
                x=strain,
                y=strain_rate,
                z=stress,
                mode='lines',
                line=dict(width=line_width, color=color_hex),
                name=title,
                hovertemplate=hover_text
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='Strain'),
                yaxis=dict(title='Strain Rate (s⁻¹)'),
                zaxis=dict(title='Stress (Pa)'),
                aspectmode='auto'
            ),
            title='3D Lissajous Overlay',
            font=dict(family='Times New Roman', size=14),
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(x=1.02, y=1, font=dict(size=10))
        )
        
        self.set_plotly_figure(fig)


class Plot2DWidget(PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground("w")
        self.showGrid(x=True, y=True)
        self.setLabel("left", "Y")
        self.setLabel("bottom", "X")
        self.setTitle("2D Plot")
        self.setMouseEnabled(x=True, y=True)
        self.enableAutoRange()
        self.addLegend()
        self._plot_items = []
    
    def clear_plot(self):
        self.clear()
        self._plot_items = []


class Matplotlib3DWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig = Figure(figsize=(10, 8), dpi=100, facecolor="white")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self._current_data = None
    
    def clear_plot(self):
        self.fig.clear()
        self.canvas.draw_idle()
        self._current_data = None
    
    def clear(self):
        self.clear_plot()
    
    def plot_lissajous_3d(self, strain, stress, strain_rate, title="Lissajous 3D", colormap='viridis'):
        import numpy as np
        from mpl_toolkits.mplot3d import Axes3D
        
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='3d')
        
        strain_norm = (strain - strain.min()) / (strain.max() - strain.min())
        cmap = cm.get_cmap(colormap)
        
        ax.scatter(strain, strain_rate, stress, c=strain_norm, cmap=cmap, s=5, alpha=0.7)
        ax.plot(strain, strain_rate, stress, 'k-', linewidth=0.5, alpha=0.3)
        
        ax.set_xlabel('Strain', fontweight='bold')
        ax.set_ylabel('Strain Rate (s⁻¹)', fontweight='bold')
        ax.set_zlabel('Stress (Pa)', fontweight='bold')
        ax.set_title(title, fontweight='bold')
        
        sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=strain.min(), vmax=strain.max()))
        sm.set_array([])
        cbar = self.fig.colorbar(sm, ax=ax, shrink=0.6)
        cbar.set_label('Strain', fontweight='bold')
        
        self.canvas.draw_idle()


class LissajousPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.fig = Figure(figsize=(14, 6), dpi=100, facecolor="white")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.ax_elastic = self.fig.add_subplot(121)
        self.ax_viscous = self.fig.add_subplot(122)
        for ax in (self.ax_elastic, self.ax_viscous):
            ax.set_facecolor("white")
            ax.grid(False)
            ax.tick_params(colors="gray", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("lightgray")
        self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.12, top=0.88, wspace=0.25)
    
    def clear_plot(self):
        if hasattr(self, 'ax_elastic') and self.ax_elastic is not None:
            self.ax_elastic.clear()
        if hasattr(self, 'ax_viscous') and self.ax_viscous is not None:
            self.ax_viscous.clear()
        if hasattr(self, 'canvas'):
            self.canvas.draw_idle()
    
    def plot_lissajous(self, data, colormap='viridis', line_width=5):
        if data is None or data.shape[1] < 4:
            return
        if self.ax_elastic is None or self.ax_viscous is None:
            self.fig.clear()
            self.ax_elastic = self.fig.add_subplot(121)
            self.ax_viscous = self.fig.add_subplot(122)
            for ax in (self.ax_elastic, self.ax_viscous):
                ax.set_facecolor("white")
                ax.grid(False)
                ax.tick_params(colors="gray", labelsize=9)
                for spine in ax.spines.values():
                    spine.set_color("lightgray")
            self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.12, top=0.88, wspace=0.25)
        else:
            self.clear_plot()
        time = data[:, 0]
        stress = data[:, 1]
        strain = data[:, 2]
        strain_rate = data[:, 3]
        cmap = cm.get_cmap(colormap)
        strain_norm = (strain - strain.min()) / (strain.max() - strain.min())
        
        self.ax_elastic.scatter(strain, stress, c=strain_norm, cmap=cmap, s=10, alpha=0.8, edgecolors='none')
        for i in range(len(strain) - 1):
            self.ax_elastic.plot([strain[i], strain[i+1]], [stress[i], stress[i+1]], 
                                  color=cmap(strain_norm[i]), linewidth=line_width, alpha=0.6)
        self.ax_elastic.set_xlabel('Strain', fontweight='bold')
        self.ax_elastic.set_ylabel('Stress (Pa)', fontweight='bold')
        self.ax_elastic.set_title('Elastic Lissajous', fontweight='bold')
        
        self.ax_viscous.scatter(strain_rate, stress, c=strain_norm, cmap=cmap, s=10, alpha=0.8, edgecolors='none')
        for i in range(len(strain_rate) - 1):
            self.ax_viscous.plot([strain_rate[i], strain_rate[i+1]], [stress[i], stress[i+1]], 
                                  color=cmap(strain_norm[i]), linewidth=line_width, alpha=0.6)
        self.ax_viscous.set_xlabel('Strain Rate (s⁻¹)', fontweight='bold')
        self.ax_viscous.set_ylabel('Stress (Pa)', fontweight='bold')
        self.ax_viscous.set_title('Viscous Lissajous', fontweight='bold')
        self.canvas.draw_idle()
    
    def plot_lissajous_multi(self, data_list, legend_titles, colormap='viridis', line_width=5):
        if not data_list:
            return
        self.fig.clear()
        self.ax_elastic = self.fig.add_subplot(121)
        self.ax_viscous = self.fig.add_subplot(122)
        for ax in (self.ax_elastic, self.ax_viscous):
            ax.set_facecolor("white")
            ax.grid(False)
            ax.tick_params(colors="gray", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("lightgray")
        n_curves = len(data_list)
        cmap = cm.get_cmap(colormap)
        curve_colors = cmap(np.linspace(0.2, 0.9, n_curves))
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 4:
                continue
            stress = data[:, 1]
            strain = data[:, 2]
            strain_rate = data[:, 3]
            color = curve_colors[i]
            self.ax_elastic.plot(strain, stress, color=color, linewidth=line_width, linestyle='-', label=title, alpha=0.85)
            self.ax_viscous.plot(strain_rate, stress, color=color, linewidth=line_width, linestyle='-', label=title, alpha=0.85)
        self.ax_elastic.set_xlabel('Strain', fontweight='bold')
        self.ax_elastic.set_ylabel('Stress', fontweight='bold')
        self.ax_elastic.set_title('Elastic Overlay', fontweight='bold')
        legend_font = get_legend_fontdict()
        self.ax_elastic.legend(prop=legend_font)
        self.ax_viscous.set_xlabel('Strain Rate', fontweight='bold')
        self.ax_viscous.set_ylabel('Stress', fontweight='bold')
        self.ax_viscous.set_title('Viscous Overlay', fontweight='bold')
        legend_font = get_legend_fontdict()
        self.ax_viscous.legend(prop=legend_font)
        self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.12, top=0.88, wspace=0.25)
        self.canvas.draw_idle()
    
    def plot_lissajous_elastic_multi(self, data_list, legend_titles, colormap='viridis', line_width=5):
        if not data_list:
            return
        self.fig.clear()
        self.ax_elastic = self.fig.add_subplot(111)
        self.ax_viscous = None
        self.ax_elastic.set_facecolor("white")
        self.ax_elastic.grid(False)
        self.ax_elastic.tick_params(colors="gray", labelsize=9)
        for spine in self.ax_elastic.spines.values():
            spine.set_color("lightgray")
        n_curves = len(data_list)
        cmap = cm.get_cmap(colormap)
        curve_colors = cmap(np.linspace(0.2, 0.9, n_curves))
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 4:
                continue
            stress = data[:, 1]
            strain = data[:, 2]
            color = curve_colors[i]
            self.ax_elastic.plot(strain, stress, color=color, linewidth=line_width, linestyle='-', label=title, alpha=0.85)
        self.ax_elastic.set_xlabel('Strain', fontweight='bold')
        self.ax_elastic.set_ylabel('Stress', fontweight='bold')
        self.ax_elastic.set_title('Elastic Lissajous Overlay', fontweight='bold')
        legend_font = get_legend_fontdict()
        self.ax_elastic.legend(prop=legend_font)
        self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.12, top=0.88)
        self.canvas.draw_idle()
    
    def plot_lissajous_viscous_multi(self, data_list, legend_titles, colormap='viridis', line_width=5):
        if not data_list:
            return
        self.fig.clear()
        self.ax_viscous = self.fig.add_subplot(111)
        self.ax_elastic = None
        self.ax_viscous.set_facecolor("white")
        self.ax_viscous.grid(False)
        self.ax_viscous.tick_params(colors="gray", labelsize=9)
        for spine in self.ax_viscous.spines.values():
            spine.set_color("lightgray")
        n_curves = len(data_list)
        cmap = cm.get_cmap(colormap)
        curve_colors = cmap(np.linspace(0.2, 0.9, n_curves))
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 4:
                continue
            stress = data[:, 1]
            strain_rate = data[:, 3]
            color = curve_colors[i]
            self.ax_viscous.plot(strain_rate, stress, color=color, linewidth=line_width, linestyle='-', label=title, alpha=0.85)
        self.ax_viscous.set_xlabel('Strain Rate (s⁻¹)', fontweight='bold')
        self.ax_viscous.set_ylabel('Stress', fontweight='bold')
        self.ax_viscous.set_title('Viscous Lissajous Overlay', fontweight='bold')
        legend_font = get_legend_fontdict()
        self.ax_viscous.legend(prop=legend_font)
        self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.12, top=0.88)
        self.canvas.draw_idle()


class PlotWidgetContainer(QWidget):
    plot_clicked = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._create_toolbar()
        layout.addWidget(self.toolbar)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        from core.plotter import MatplotlibCanvas
        self.matplotlib_widget = MatplotlibCanvas(width=14, height=7, dpi=100)
        self.tabs.addTab(self.matplotlib_widget, "Analysis")
        
        if WEBENGINE_AVAILABLE:
            self.plotly_widget = PlotlyWidget()
            self._use_plotly = True
        else:
            self.plotly_widget = Matplotlib3DWidget()
            self._use_plotly = False
        self.tabs.addTab(self.plotly_widget, "3D Plot")
        
        self.projections_plotly = LissajousPlotWidget()
        self.tabs.addTab(self.projections_plotly, "Projections")
        
        from ui.widgets.plot_data_viewer import DataTableWidget
        self.data_table_widget = DataTableWidget()
        self.tabs.addTab(self.data_table_widget, "Data Table")
        
        self.plot_2d = Plot2DWidget()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background: #f0f0f0;")
        layout.addWidget(self.status_label)
    
    def _create_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(get_ui_scale().scaled(24), get_ui_scale().scaled(24)))
        export_png = QAction("PNG", self)
        export_png.triggered.connect(self._export_png)
        self.toolbar.addAction(export_png)
        export_jpg = QAction("JPG", self)
        export_jpg.triggered.connect(self._export_jpg)
        self.toolbar.addAction(export_jpg)
        export_svg = QAction("SVG", self)
        export_svg.triggered.connect(self._export_svg)
        self.toolbar.addAction(export_svg)
        export_html = QAction(tr("HTML (3D)"), self)
        export_html.triggered.connect(self._export_html)
        self.toolbar.addAction(export_html)
        self.toolbar.addSeparator()
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_all)
        self.toolbar.addAction(clear_action)
    
    def _export_png(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export PNG", "", "PNG (*.png)")
        if filepath:
            if not filepath.endswith(".png"):
                filepath += ".png"
            self._export_current_plot(filepath, "png")
    
    def _export_jpg(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export JPG", "", "JPEG (*.jpg *.jpeg)")
        if filepath:
            if not (filepath.endswith(".jpg") or filepath.endswith(".jpeg")):
                filepath += ".jpg"
            self._export_current_plot(filepath, "jpg")
    
    def _export_svg(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export SVG", "", "SVG (*.svg)")
        if filepath:
            if not filepath.endswith(".svg"):
                filepath += ".svg"
            self._export_current_plot(filepath, "svg")
    
    def _export_html(self):
        filepath, _ = QFileDialog.getSaveFileName(self, tr("Export HTML (3D Plot)"), "", "HTML (*.html)")
        if filepath:
            if not filepath.endswith(".html"):
                filepath += ".html"
            self._export_current_plot(filepath, "html")
    
    @staticmethod
    def _plotly_figure_to_matplotlib(fig):
        """Re-render a Plotly 3D figure with matplotlib for image export.

        Plotly image export (kaleido) is unreliable in the compiled application,
        so the 3D tab (Lissajous 3D, Fourier 3D, ...) is converted to an
        equivalent matplotlib 3D figure before saving as SVG/PNG/JPG.
        """
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib import cm, colors as mcolors
        from mpl_toolkits.mplot3d.art3d import Line3DCollection

        def _text_of(value):
            if value is None:
                return ''
            if isinstance(value, str):
                return value
            return getattr(value, 'text', '') or ''

        def _as_float_1d(values):
            try:
                arr = np.asarray(values, dtype=float).ravel()
            except Exception:
                return None
            if arr.size == 0:
                return None
            mask = np.isfinite(arr)
            if not mask.all():
                arr = arr[mask]
            return arr if arr.size else None

        def _resolve_color(color_value, count):
            """Return ('solid', css_color) / ('array', values) or None."""
            if color_value is None:
                return None
            if isinstance(color_value, str):
                return ('solid', color_value)
            try:
                arr = np.asarray(color_value)
            except Exception:
                return None
            if arr.ndim == 0:
                return ('solid', str(arr))
            if arr.dtype.kind in ('U', 'S', 'O'):
                return ('solid', str(arr.ravel()[0]))
            arr = arr.astype(float).ravel()
            if arr.size == count:
                return ('array', arr)
            return None

        def _colorscale_of(holder):
            scale = getattr(holder, 'colorscale', None)
            if isinstance(scale, str):
                try:
                    return cm.get_cmap(scale)
                except Exception:
                    return cm.get_cmap('viridis')
            if scale is not None:
                try:
                    return mcolors.LinearSegmentedColormap.from_list(
                        'plotly_scale', [color for _, color in scale])
                except Exception:
                    pass
            return cm.get_cmap('viridis')

        try:
            scene = fig.layout.scene
        except Exception:
            scene = None

        def _axis_of(name):
            if scene is None:
                return None
            return getattr(scene, name, None)

        _xaxis, _yaxis, _zaxis = _axis_of('xaxis'), _axis_of('yaxis'), _axis_of('zaxis')
        log_flags = {
            'x': str(getattr(_xaxis, 'type', '') or '').lower() == 'log',
            'y': str(getattr(_yaxis, 'type', '') or '').lower() == 'log',
            'z': str(getattr(_zaxis, 'type', '') or '').lower() == 'log',
        }

        mfig = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        ax = mfig.add_subplot(111, projection='3d')

        traces = list(getattr(fig, 'data', []) or [])
        colorbar_values = None
        colorbar_cmap = None
        colorbar_label = ''
        xs_all, ys_all, zs_all = [], [], []

        for trace in traces:
            x = _as_float_1d(getattr(trace, 'x', None))
            y = _as_float_1d(getattr(trace, 'y', None))
            z = _as_float_1d(getattr(trace, 'z', None))
            if x is None or y is None or z is None:
                continue
            count = min(x.size, y.size, z.size)
            if count == 0:
                continue
            x, y, z = x[:count], y[:count], z[:count]
            # Plotly log axes are rendered as linear axes on log10-transformed
            # coordinates (mplot3d handles log scales poorly).
            mask = np.ones(count, dtype=bool)
            if log_flags['x']:
                mask &= (x > 0)
            if log_flags['y']:
                mask &= (y > 0)
            if log_flags['z']:
                mask &= (z > 0)
            if not mask.all():
                x, y, z = x[mask], y[mask], z[mask]
                count = x.size
            if count == 0:
                continue
            xt = np.log10(x) if log_flags['x'] else x
            yt = np.log10(y) if log_flags['y'] else y
            zt = np.log10(z) if log_flags['z'] else z
            xs_all.append(xt)
            ys_all.append(yt)
            zs_all.append(zt)
            mode = str(getattr(trace, 'mode', 'lines') or 'lines')
            name = getattr(trace, 'name', '') or ''
            line = getattr(trace, 'line', None)
            marker = getattr(trace, 'marker', None)
            try:
                line_width = float(getattr(line, 'width', None))
            except (TypeError, ValueError):
                line_width = None
            lw = max(0.6, (line_width or 3.0) / 3.0)

            line_color = None
            marker_color = None
            if line is not None:
                line_color = _resolve_color(getattr(line, 'color', None), count)
            if marker is not None:
                marker_color = _resolve_color(getattr(marker, 'color', None), count)

            if line_color is not None and line_color[0] == 'array':
                values = line_color[1]
                cmap = _colorscale_of(line)
                norm = mcolors.Normalize(vmin=float(np.nanmin(values)),
                                         vmax=float(np.nanmax(values)))
                segments = [[(xt[i], yt[i], zt[i]),
                             (xt[i + 1], yt[i + 1], zt[i + 1])]
                            for i in range(count - 1)]
                if segments:
                    collection = Line3DCollection(segments, cmap=cmap, norm=norm,
                                                  linewidths=lw)
                    collection.set_array(values[:-1] if values.size > 1 else values)
                    ax.add_collection3d(collection)
                    if colorbar_values is None:
                        colorbar_values = values
                        colorbar_cmap = cmap
                        colorbar_label = _text_of(getattr(
                            getattr(line, 'colorbar', None), 'title', None)) or 'Color'
            elif 'lines' in mode:
                color = None
                if line_color is not None and line_color[0] == 'solid':
                    color = line_color[1]
                elif marker_color is not None and marker_color[0] == 'solid':
                    color = marker_color[1]
                ax.plot(xt, yt, zt, color=color, linewidth=lw, label=name or None)

            if marker_color is not None and marker_color[0] == 'array':
                values = marker_color[1]
                cmap = _colorscale_of(marker)
                norm = mcolors.Normalize(vmin=float(np.nanmin(values)),
                                         vmax=float(np.nanmax(values)))
                ax.scatter(xt, yt, zt, c=values, cmap=cmap, norm=norm, s=8)
                if colorbar_values is None:
                    colorbar_values = values
                    colorbar_cmap = cmap
                    colorbar_label = _text_of(getattr(
                        getattr(marker, 'colorbar', None), 'title', None)) or 'Color'
            elif 'markers' in mode:
                color = None
                if marker_color is not None and marker_color[0] == 'solid':
                    color = marker_color[1]
                elif line_color is not None and line_color[0] == 'solid':
                    color = line_color[1]
                ax.scatter(xt, yt, zt, color=color, s=8,
                           label=None if 'lines' in mode else (name or None))

        ax.set_xlabel(_text_of(getattr(_xaxis, 'title', None)))
        ax.set_ylabel(_text_of(getattr(_yaxis, 'title', None)))
        ax.set_zlabel(_text_of(getattr(_zaxis, 'title', None)))

        def _set_limits(arrays, setter):
            if not arrays:
                return
            try:
                values = np.concatenate([np.ravel(a) for a in arrays if np.size(a)])
            except Exception:
                return
            values = values[np.isfinite(values)]
            if values.size == 0:
                return
            low, high = float(values.min()), float(values.max())
            if high <= low:
                high = low + 1.0
            padding = 0.06 * (high - low)
            setter(low - padding, high + padding)

        _set_limits(xs_all, ax.set_xlim)
        _set_limits(ys_all, ax.set_ylim)
        _set_limits(zs_all, ax.set_zlim)

        for flag, lim, ticks_setter, labels_setter in (
                (log_flags['x'], ax.get_xlim, ax.set_xticks, ax.set_xticklabels),
                (log_flags['y'], ax.get_ylim, ax.set_yticks, ax.set_yticklabels),
                (log_flags['z'], ax.get_zlim, ax.set_zticks, ax.set_zticklabels)):
            if not flag:
                continue
            try:
                low, high = lim()
                first, last = int(np.ceil(low)), int(np.floor(high))
                if last < first:
                    continue
                step = max(1, int(np.ceil((last - first) / 8.0)))
                tick_values = list(range(first, last + 1, step))
                if not tick_values:
                    continue
                ticks_setter(tick_values)
                labels_setter([f'$10^{{{t}}}$' for t in tick_values])
            except Exception:
                pass

        layout_title = getattr(fig.layout, 'title', None)
        title = layout_title if isinstance(layout_title, str) else _text_of(getattr(layout_title, 'text', None))
        if title:
            ax.set_title(title, fontweight='bold')

        try:
            aspectmode = getattr(scene, 'aspectmode', None)
            aspectratio = getattr(scene, 'aspectratio', None)
            if aspectmode == 'manual' and aspectratio is not None:
                ax.set_box_aspect((float(getattr(aspectratio, 'x', 1) or 1),
                                   float(getattr(aspectratio, 'y', 1) or 1),
                                   float(getattr(aspectratio, 'z', 1) or 1)))
        except Exception:
            pass

        if len(traces) > 1:
            try:
                ax.legend(loc='upper left', fontsize=8,
                          prop={'family': 'Times New Roman'})
            except Exception:
                pass
        if colorbar_values is not None:
            try:
                mappable = cm.ScalarMappable(
                    norm=mcolors.Normalize(vmin=float(np.nanmin(colorbar_values)),
                                           vmax=float(np.nanmax(colorbar_values))),
                    cmap=colorbar_cmap)
                mappable.set_array(colorbar_values)
                cbar = mfig.colorbar(mappable, ax=ax, shrink=0.7, pad=0.08)
                if colorbar_label:
                    cbar.set_label(colorbar_label, fontweight='bold')
            except Exception:
                pass

        for label in (ax.get_xticklabels() + ax.get_yticklabels() + ax.get_zticklabels()):
            label.set_fontfamily('Times New Roman')
        for setter, getter in ((ax.set_xlabel, ax.get_xlabel),
                               (ax.set_ylabel, ax.get_ylabel),
                               (ax.set_zlabel, ax.get_zlabel)):
            setter(getter(), fontfamily='Times New Roman', fontweight='bold')
        mfig.subplots_adjust(left=0.02, right=0.88, bottom=0.02, top=0.92)
        return mfig

    def _export_current_plot(self, filepath, fmt):
        settings = get_settings()
        dpi = settings.get_plot_setting('export_dpi', 300)

        current_tab = self.tabs.currentIndex()

        try:
            if current_tab == 0:
                self.matplotlib_widget.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                                                   facecolor='white', edgecolor='none')

            elif current_tab == 1:
                if self._use_plotly and self.plotly_widget._current_figure is not None:
                    if fmt == 'html':
                        pio.write_html(self.plotly_widget._current_figure, filepath,
                                       include_plotlyjs='cdn', full_html=True)
                    else:
                        # kaleido is unreliable in the compiled application, so
                        # convert the Plotly 3D figure to matplotlib and export it
                        mfig = self._plotly_figure_to_matplotlib(
                            self.plotly_widget._current_figure)
                        mfig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                                     facecolor='white', edgecolor='none')
                elif not self._use_plotly and hasattr(self.plotly_widget, 'fig'):
                    self.plotly_widget.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                                                   facecolor='white', edgecolor='none')
                else:
                    QMessageBox.information(self, tr("Export"),
                                            tr("No 3D plot to export.\nPlease draw a 3D plot first."))
                    return

            elif current_tab == 2:
                self.projections_plotly.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                                                    facecolor='white', edgecolor='none')

            elif current_tab == 3:
                QMessageBox.information(self, "Export",
                                       "Data Table tab cannot be exported as image.\n"
                                       "Please use the Export button in the data table to export as Excel.")
                return
        except Exception as e:
            QMessageBox.warning(self, tr("Export Error"),
                                tr("Failed to export image:\n{}").format(str(e)))
            return

        self.status_label.setText(f"Exported to {filepath}")
    
    def get_matplotlib_widget(self):
        return self.matplotlib_widget
    
    def get_plotly_widget(self):
        return self.plotly_widget
    
    def get_projections_widget(self):
        return self.projections_plotly
    
    def get_2d_widget(self):
        return self.plot_2d
    
    def get_data_table_widget(self):
        return self.data_table_widget
    
    def set_current_tab(self, index):
        self.tabs.setCurrentIndex(index)
    
    def clear_all(self):
        self.plot_2d.clear_plot()
        if hasattr(self.plotly_widget, "clear_plot"):
            self.plotly_widget.clear_plot()
        self.projections_plotly.clear_plot()
        self.matplotlib_widget.clear()
        self.status_label.setText("Cleared")
    
    def set_status(self, message):
        self.status_label.setText(message)
    
    def _auto_range(self):
        self.matplotlib_widget.canvas.draw_idle()