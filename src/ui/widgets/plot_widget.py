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
        line_styles = ['-', '--', '-.', ':']
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 4:
                continue
            stress = data[:, 1]
            strain = data[:, 2]
            strain_rate = data[:, 3]
            color = curve_colors[i]
            style = line_styles[i % len(line_styles)]
            self.ax_elastic.plot(strain, stress, color=color, linewidth=line_width, linestyle=style, label=title, alpha=0.85)
            self.ax_viscous.plot(strain_rate, stress, color=color, linewidth=line_width, linestyle=style, label=title, alpha=0.85)
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
        line_styles = ['-', '--', '-.', ':']
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 4:
                continue
            stress = data[:, 1]
            strain = data[:, 2]
            color = curve_colors[i]
            style = line_styles[i % len(line_styles)]
            self.ax_elastic.plot(strain, stress, color=color, linewidth=line_width, linestyle=style, label=title, alpha=0.85)
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
        line_styles = ['-', '--', '-.', ':']
        for i, (data, title) in enumerate(zip(data_list, legend_titles)):
            if data is None or data.shape[1] < 4:
                continue
            stress = data[:, 1]
            strain_rate = data[:, 3]
            color = curve_colors[i]
            style = line_styles[i % len(line_styles)]
            self.ax_viscous.plot(strain_rate, stress, color=color, linewidth=line_width, linestyle=style, label=title, alpha=0.85)
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
    
    def _export_current_plot(self, filepath, fmt):
        settings = get_settings()
        dpi = settings.get_plot_setting('export_dpi', 300)
        
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:
            self.matplotlib_widget.fig.savefig(filepath, dpi=dpi, bbox_inches='tight', 
                                               facecolor='white', edgecolor='none')
        
        elif current_tab == 1:
            if self._use_plotly and self.plotly_widget._current_figure is not None:
                try:
                    if fmt == 'html':
                        pio.write_html(self.plotly_widget._current_figure, filepath, 
                                       include_plotlyjs='cdn', full_html=True)
                    else:
                        # In frozen/compiled app, kaleido has compatibility issues
                        # Show message to user to use HTML export instead
                        title = tr("Export Format Not Supported")
                        msg = tr("3D plot image export (PNG/JPG/SVG) is not supported in the compiled application.\n\n"
                                "Please use HTML format for 3D plot export.\n\n"
                                "HTML export provides:\n"
                                "- Interactive 3D visualization\n"
                                "- Zoom, rotate, pan\n"
                                "- Smaller file size\n"
                                "- Works in any web browser")
                        QMessageBox.information(self, title, msg)
                        return
                except Exception as e:
                    QMessageBox.warning(self, "Export Error", 
                                       f"Failed to export Plotly figure:\n{str(e)}")
            elif not self._use_plotly and hasattr(self.plotly_widget, 'fig'):
                self.plotly_widget.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                                               facecolor='white', edgecolor='none')
        
        elif current_tab == 2:
            self.projections_plotly.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                                               facecolor='white', edgecolor='none')
        
        elif current_tab == 3:
            QMessageBox.information(self, "Export", 
                                   "Data Table tab cannot be exported as image.\n"
                                   "Please use the Export button in the data table to export as Excel.")
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