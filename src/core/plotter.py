# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: core\plotter.py
"""
Plotter - PyQtGraph-based plotting for ChemicalStrain GUI
Adapts matplotlib/plotly functions from src/plotters.py
"""
import os, numpy as np, pandas as pd
from typing import List, Optional, Tuple, Dict
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from pyqtgraph.opengl import GLViewWidget, GLScatterPlotItem, GLLinePlotItem
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm
import plotly.graph_objects as go
from matplotlib.ticker import LogFormatterMathtext
from utils.i18n import tr

def format_colorbar_log(cbar, vmin, vmax):
    """
    Format colorbar with logarithmic scale and scientific notation (10^n)
    格式化颜色条为对数刻度，使用10次方科学表示法
    只显示主刻度，只显示整数次方
    """
    import matplotlib.ticker as ticker
    
    class IntLogFormatter(ticker.LogFormatterMathtext):
        def _num_to_string(self, x, vmin, vmax):
            exp = np.log10(x)
            if abs(exp - round(exp)) < 0.01:
                return '$10^{%d}$' % int(round(exp))
            return ''
        
        def format_data(self, value):
            if value <= 0:
                return ''
            exp = np.log10(value)
            if abs(exp - round(exp)) < 0.01:
                return '$10^{%d}$' % int(round(exp))
            return ''
    
    if vmin > 0 and vmax > vmin:
        cbar.ax.set_yscale('log')
        
        formatter = IntLogFormatter(base=10, labelOnlyBase=False)
        cbar.ax.yaxis.set_major_formatter(formatter)
        
        log_min = int(np.floor(np.log10(vmin)))
        log_max = int(np.ceil(np.log10(vmax)))
        
        major_ticks = [10**i for i in range(log_min, log_max + 1) if 10**i >= vmin and 10**i <= vmax]
        cbar.ax.set_yticks(major_ticks, minor=False)
        
        cbar.ax.tick_params(which='major', length=6, width=1.5, labelsize=10, direction='out')
        cbar.ax.tick_params(which='minor', length=0, width=0)
    else:
        cbar.ax.tick_params(which='both', length=6, width=1.5, labelsize=10, direction='out')

class MatplotlibCanvas(QWidget):
    __doc__ = "\n    Matplotlib canvas widget for 2D plotting (Analysis tab)\n    Compatible with pyqtgraph PlotWidget interface\n    "

    def __init__(self, width=14, height=7, dpi=100, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="white")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111)
        self._title = ""
        self._xlabel = ""
        self._ylabel = ""

    def clear(self):
        """Clear the figure"""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.canvas.draw_idle()

    def draw(self):
        """Redraw the canvas"""
        self.canvas.draw_idle()

    def setTitle(self, title: str):
        """Set plot title"""
        self._title = title
        self.ax.set_title(title)
        self.canvas.draw_idle()

    def setLabel(self, axis: str, label: str):
        """Set axis label (axis: 'left', 'bottom', 'right', 'top')"""
        if axis == "left":
            self._ylabel = label
            self.ax.set_ylabel(label)
        else:
            if axis == "bottom":
                self._xlabel = label
                self.ax.set_xlabel(label)
            else:
                if axis == "right":
                    self.ax.twinx().set_ylabel(label)
                else:
                    if axis == "top":
                        pass
        self.canvas.draw_idle()

    def showGrid(self, x: bool=True, y: bool=True):
        """Show grid"""
        self.ax.grid(x and y)
        self.canvas.draw_idle()

    def addLegend(self):
        """Add legend"""
        self.ax.legend()
        self.canvas.draw_idle()

    def setLogMode(self, x: bool=None, y: bool=None):
        """Set log scale mode"""
        if x is not None:
            if x:
                self.ax.set_xscale("log")
        if y is not None:
            if y:
                self.ax.set_yscale("log")
        self.canvas.draw_idle()

    def plot(self, x, y, pen=None, symbol=None, symbolBrush=None, name=None, **kwargs):
        """Plot data - compatible with pyqtgraph interface"""
        if symbol:
            self.ax.scatter(x, y, label=name, marker="o")
        else:
            color = "b"
            if pen:
                if hasattr(pen, "color"):
                    color = pen.color()
                else:
                    if isinstance(pen, dict):
                        color = pen.get("color", "b")
            self.ax.plot(x, y, color=color, label=name)
        if name:
            self.ax.legend()
        self.canvas.draw_idle()


class Plotter(QObject):
    __doc__ = "\n    PyQtGraph-based plotting class for LAOS data visualization\n    "
    plot_error = pyqtSignal(str)
    plot_finished = pyqtSignal()
    progress_updated = pyqtSignal(int, str)
    log_message = pyqtSignal(str)
    plot_data_ready = pyqtSignal(str, dict)
    spp_titles_request = pyqtSignal(list, str)

    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.omega = 2 * np.pi
        self.current_plot_widget = None
        self._colormap = "viridis"

    def set_folder_path(self, folder_path: str):
        """Set the working folder path"""
        self.folder_path = folder_path

    def set_omega(self, omega: float):
        """Set angular frequency"""
        self.omega = omega

    def set_colormap(self, colormap: str):
        """Set colormap for scatter plots and overlays"""
        self._colormap = colormap

    def _get_cmap(self, default: str='viridis') -> str:
        """Get current colormap or fallback to default"""
        if self._colormap:
            return self._colormap
        return default

    def _create_combined_colormap(self) -> LinearSegmentedColormap:
        """
        Create combined colormap from user-selected colormap for multi-file overlays
        Uses autumn+cool style but with user-selected colors
        """
        cmap = cm.get_cmap(self._get_cmap("viridis"), 256)
        return cmap

    def _load_data(self, file_path) -> Optional[np.ndarray]:
        """Load data from a txt file"""
        if not os.path.exists(file_path):
            self.log_message.emit(f"File not found: {file_path}")
            return None
        try:
            # Try loading with default settings
            data = np.loadtxt(file_path, dtype=np.float64)
            return data
        except ValueError:
            try:
                # Try skipping header row
                data = np.loadtxt(file_path, skiprows=1, dtype=np.float64)
                return data
            except ValueError:
                try:
                    # Try with genfromtxt for more flexibility
                    data = np.genfromtxt(file_path, skip_header=1, filling_values=np.nan, dtype=np.float64)
                    data = data[~np.any(np.isnan(data), axis=1)]
                    return data
                except Exception as e:
                    self.log_message.emit(f"Error loading {file_path}: {str(e)}")
                    return None
        except Exception as e:
            self.log_message.emit(f"Error loading {file_path}: {str(e)}")
            return None

    def _get_numbered_files(self) -> List[str]:
        """Get list of numbered txt files"""
        files = []
        if not self.folder_path or not os.path.exists(self.folder_path):
            return files
        for f in os.listdir(self.folder_path):
            if f.endswith(".txt") and f.replace(".txt", "").isdigit():
                files.append(os.path.join(self.folder_path, f))
        files.sort(key=lambda x: int(os.path.basename(x).replace(".txt", "")))
        return files

    def _get_file_by_number(self, file_number: int) -> Optional[str]:
        """
        Get file path by file number (e.g., 30 -> '030.txt')

        Args:
            file_number: The numeric part of the file name (e.g., 30 for '030.txt')

        Returns:
            Full file path or None if not found
        """
        possible_names = [
            f"{file_number}.txt",
            f"{file_number:03d}.txt",
            f"{file_number:02d}.txt"
        ]
        for name in possible_names:
            path = os.path.join(self.folder_path, name)
            if os.path.exists(path):
                return path

        # Try to find in numbered files list
        numbered_files = self._get_numbered_files()
        for f in numbered_files:
            num = int(os.path.basename(f).replace(".txt", ""))
            if num == file_number:
                return f
        return None

    def _load_spp_titles(self, titles_file: str) -> Tuple[(List[str], List[str])]:
        """
        Load previously saved file numbers and curve titles from file_titles.txt
        Matching LAOS数据处理 0417.py choice=="11" load_previous_selection()

        Args:
            titles_file: Path to the file_titles.txt file

        Returns:
            Tuple of (file_numbers, titles)
        """
        if os.path.exists(titles_file):
            try:
                with open(titles_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                file_numbers = []
                titles = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        pass
                    elif "文件编号:" in line:
                        if "曲线标题:" in line:
                            parts = line.split(", 曲线标题: ")
                            if len(parts) >= 2:
                                file_num = parts[0].split("文件编号: ")[1].strip()
                                title = parts[1].strip()
                                file_numbers.append(file_num)
                                titles.append(title)
                return (file_numbers, titles)

            except Exception as e:
                try:
                    self.log_message.emit(f"Error loading titles file: {str(e)}")
                finally:
                    e = None
                    del e

        return ([], [])

    def _save_spp_titles(self, titles_file: str, file_numbers: List[str], titles: List[str]):
        """
        Save file numbers and curve titles to file_titles.txt
        Matching LAOS数据处理 0417.py choice=="11" save functionality

        Args:
            titles_file: Path to the file_titles.txt file
            file_numbers: List of file numbers
            titles: List of corresponding curve titles
        """
        try:
            with open(titles_file, "w", encoding="utf-8") as f:
                for num, title in zip(file_numbers, titles):
                    f.write(f"文件编号: {num}, 曲线标题: {title}\n")

            self.log_message.emit(f"Curve titles saved to {titles_file}")
        except Exception as e:
            try:
                self.log_message.emit(f"Error saving titles file: {str(e)}")
            finally:
                e = None
                del e

    def get_available_spp_files(self) -> List[str]:
        """
        Get list of available SPP data file numbers

        Returns:
            List of file numbers (e.g., ["030", "060", "090"])
        """
        spp_folder = os.path.join(self.folder_path, "SPP Data")
        if not os.path.exists(spp_folder):
            return []
        files = [f for f in os.listdir(spp_folder) if f.endswith(".txt") if "_spp" in f]
        file_numbers = []
        for f in files:
            num = f.split("_")[0]
            if num.isdigit():
                file_numbers.append(num)
            file_numbers.sort(key=(lambda x: int(x)))
            return file_numbers

    def _get_excel_strain_values(self) -> List[float]:
        """Get strain values from Excel file"""
        excel_file = None
        for f in os.listdir(self.folder_path):
            if f.endswith(".xlsx") or f.endswith(".xls"):
                if not f.startswith("~"):
                    excel_file = os.path.join(self.folder_path, f)
                    break
        if excel_file:
            try:
                df = pd.read_excel(excel_file)
                if "ɣ in -" in df.columns:
                    return df["ɣ in -"].tolist()
            except Exception as e:
                self.log_message.emit(f"Error reading Excel: {str(e)}")
        return []

    def _get_excel_labels(self) -> Dict[int, str]:
        """Get labels (strain values) from Excel file for each file number"""
        labels = {}
        excel_file = None
        for f in os.listdir(self.folder_path):
            if f.endswith(".xlsx") or f.endswith(".xls"):
                if not f.startswith("~"):
                    excel_file = os.path.join(self.folder_path, f)
                    break
        if excel_file:
            try:
                df = pd.read_excel(excel_file)
                strain_col = None
                for col in df.columns:
                    if "ɣ" in str(col) or "gamma" in str(col).lower() or "strain" in str(col).lower():
                        strain_col = col
                        break
                if strain_col:
                    file_col = None
                    for col in df.columns:
                        if "file" in str(col).lower() or "no" in str(col).lower() or "number" in str(col).lower():
                            file_col = col
                            break
                    if file_col:
                        for i, row in df.iterrows():
                            file_num = int(row[file_col]) if pd.notna(row[file_col]) else i + 1
                            strain_val = row[strain_col]
                            if pd.notna(strain_val):
                                labels[file_num] = f"γ={strain_val:.2f}%"
                    else:
                        for i, row in df.iterrows():
                            strain_val = row[strain_col]
                            if pd.notna(strain_val):
                                labels[i + 1] = f"γ={strain_val:.2f}%"
            except Exception as e:
                print(f"[DEBUG] Error reading Excel labels: {e}")
        return labels

    def plot_lissajous_2d(self):
        """Placeholder method"""
        pass

    def plot_viscous_lissajous_2d(self):
        """Placeholder method"""
        pass

    def plot_lissajous_2d_multi(self):
        """Placeholder method"""
        pass

    def plot_viscous_lissajous_2d_multi(self):
        """Placeholder method"""
        pass

    def plot_stress_strain_curve(self):
        """Placeholder method"""
        pass

    def plot_st_value(self, plot_widget, marker_size=None):
        """Plot ST values vs Strain using matplotlib (matching LAOS数据处理 0417.py choice=="4")

        Creates 4 separate figures:
        1. Strain vs S (log x, linear y)
        2. Strain vs T (log x, linear y)
        3. Strain vs G'_l and G'_m (log-log)
        4. Strain vs η'_l and η'_m (log-log)
        
        Args:
            plot_widget: MatplotlibCanvas widget
            marker_size: Marker size for scatter plots (default 50)
        """
        st_file = os.path.join(self.folder_path, "ST.txt")
        if not os.path.exists(st_file):
            self.log_message.emit("ST.txt not found. Auto-calculating ST values...")
            if not self.calculate_st_value():
                self.plot_error.emit("ST calculation failed. Ensure preprocessing is complete.")
                return

        # Load data from ST.txt
        strain_values = []
        s_values = []
        t_values = []
        g_l_values = []
        g_m_values = []
        eta_l_values = []
        eta_m_values = []

        for encoding in ('utf-8', 'gbk', 'latin-1'):
            try:
                with open(st_file, "r", encoding=encoding, errors="replace") as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        values = line.split("\t")
                        try:
                            strain_val = float(values[0])
                            s_val = float(values[1])
                            t_val = float(values[2])
                            strain_values.append(strain_val)
                            s_values.append(s_val)
                            t_values.append(t_val)
                            if len(values) >= 7:
                                g_l_values.append(float(values[3]))
                                g_m_values.append(float(values[4]))
                                eta_l_values.append(float(values[5]))
                                eta_m_values.append(float(values[6]))
                        except ValueError:
                            continue
                break
            except UnicodeDecodeError:
                continue

        if not strain_values:
            self.plot_error.emit("No valid ST data found.")
            return

        # Use matplotlib for plotting
        if hasattr(plot_widget, "fig"):
            import matplotlib.colors as mcolors
            plot_widget.fig.clear()
            gs = plot_widget.fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
            ax1 = plot_widget.fig.add_subplot(gs[0, 0])
            ax2 = plot_widget.fig.add_subplot(gs[0, 1])
            ax3 = plot_widget.fig.add_subplot(gs[1, 0])
            ax4 = plot_widget.fig.add_subplot(gs[1, 1])

            strain_arr = np.array(strain_values)
            strain_min = np.min(strain_arr)
            strain_max = np.max(strain_arr)
            if strain_min > 0 and strain_max > strain_min:
                norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
            else:
                norm = plt.Normalize(vmin=strain_min, vmax=strain_max)

            from utils.plot_font import get_label_fontdict, get_title_fontdict, get_legend_fontdict, get_symbol_fontdict, get_transparency, get_marker_shape, get_marker_size
            
            label_font = get_label_fontdict()
            title_font = get_title_fontdict()
            symbol_font = get_symbol_fontdict()
            transparency = get_transparency()
            marker_shape = get_marker_shape()
            if marker_size is None:
                marker_size = get_marker_size()
            cmap = self._get_cmap('viridis')

            scatter1 = ax1.scatter(strain_values, s_values, c=strain_arr, cmap=cmap, norm=norm,
                                   s=marker_size, alpha=transparency, marker=marker_shape, edgecolors="w", linewidth=0.5)
            ax1.set_title("S vs Strain", fontdict=title_font)
            ax1.set_xscale("log")
            ax1.set_xlabel("Strain", fontdict=label_font)
            ax1.set_ylabel("S", fontdict=symbol_font)
            ax1.grid(False)
            cbar1 = plot_widget.fig.colorbar(scatter1, ax=ax1)
            cbar1.set_label("Strain", fontdict=label_font)
            format_colorbar_log(cbar1, strain_min, strain_max)
            
            scatter2 = ax2.scatter(strain_values, t_values, c=strain_arr, cmap=cmap, norm=norm,
                                   s=marker_size, alpha=transparency, marker=marker_shape, edgecolors="w", linewidth=0.5)
            ax2.set_title("T vs Strain", fontdict=title_font)
            ax2.set_xscale("log")
            ax2.set_xlabel("Strain", fontdict=label_font)
            ax2.set_ylabel("T", fontdict=symbol_font)
            ax2.grid(False)
            cbar2 = plot_widget.fig.colorbar(scatter2, ax=ax2)
            cbar2.set_label("Strain", fontdict=label_font)
            format_colorbar_log(cbar2, strain_min, strain_max)

            if g_l_values:
                scatter_gl = ax3.scatter(strain_values, g_l_values, c=strain_arr, cmap=cmap, norm=norm,
                                        marker="o", s=marker_size, alpha=transparency, edgecolors="w", linewidth=0.5, label="G′ₗ")
                scatter_gm = ax3.scatter(strain_values, g_m_values, c=strain_arr, cmap=cmap, norm=norm,
                                        marker="s", s=marker_size, alpha=transparency, edgecolors="w", linewidth=0.5, label="G′ₘ")
                ax3.set_title("Strain vs G′ₗ and G′ₘ", fontdict=title_font)
                ax3.set_xscale("log")
                ax3.set_yscale("log")
                ax3.set_xlabel("Strain", fontdict=label_font)
                ax3.set_ylabel("Modulus (Pa)", fontdict=label_font)
                ax3.grid(False)
                legend_font = get_legend_fontdict()
                ax3.legend(loc='best', prop=legend_font)
                cbar3 = plot_widget.fig.colorbar(scatter_gl, ax=ax3)
                cbar3.set_label("Strain", fontdict=label_font)
                format_colorbar_log(cbar3, strain_min, strain_max)
                
                scatter_etal = ax4.scatter(strain_values, eta_l_values, c=strain_arr, cmap=cmap, norm=norm,
                                          marker="o", s=marker_size, alpha=transparency, edgecolors="w", linewidth=0.5, label="η′ₗ")
                scatter_etam = ax4.scatter(strain_values, eta_m_values, c=strain_arr, cmap=cmap, norm=norm,
                                          marker="s", s=marker_size, alpha=transparency, edgecolors="w", linewidth=0.5, label="η′ₘ")
                ax4.set_title("Strain vs η′ₗ and η′ₘ", fontdict=title_font)
                ax4.set_xscale("log")
                ax4.set_yscale("log")
                ax4.set_xlabel("Strain", fontdict=label_font)
                ax4.set_ylabel("Viscosity (Pa·S)", fontdict=label_font)
                ax4.grid(False)
                ax4.legend(loc='best', prop=legend_font)
                cbar4 = plot_widget.fig.colorbar(scatter_etal, ax=ax4)
                cbar4.set_label("Strain", fontdict=label_font)
                format_colorbar_log(cbar4, strain_min, strain_max)

            plot_widget.fig.tight_layout()
            plot_widget.canvas.draw_idle()
            self.log_message.emit(f"Plotted ST values: {len(strain_values)} data points")
            
            self.plot_data_ready.emit('st_values', {
                'strain': np.array(strain_values),
                'S': np.array(s_values),
                'T': np.array(t_values),
                'G_l': np.array(g_l_values) if g_l_values else None,
                'G_m': np.array(g_m_values) if g_m_values else None,
                'eta_l': np.array(eta_l_values) if eta_l_values else None,
                'eta_m': np.array(eta_m_values) if eta_m_values else None
            })
        else:
            # Use pyqtgraph for plotting (fallback)
            plot_widget.clear()
            plot_widget.setTitle("S and T Values vs Strain")
            plot_widget.setLabel("left", "Value")
            plot_widget.setLabel("bottom", "Strain")
            plot_widget.showGrid(x=True, y=True)
            plot_widget.addLegend()
            plot_widget.setLogMode(x=True)
            plot_widget.plot(strain_values, s_values, pen=None, symbol="o", symbolBrush="b", name="S")
            plot_widget.plot(strain_values, t_values, pen=None, symbol="o", symbolBrush="r", name="T")

        self.plot_finished.emit()

    def _calculate_strain_amplitudes(self) -> List[float]:
        """Calculate strain amplitudes from all txt files"""
        txt_files = self._get_numbered_files()
        strain_amplitudes = []
        for file_path in txt_files:
            data = self._load_data(file_path)
            if data is not None and data.shape[1] >= 3:
                strain = data[:, 2]
                strain_amp = np.max(np.abs(strain))
                strain_amplitudes.append(strain_amp)
        return strain_amplitudes

    def plot_dissipation_rate(self, plot_widget, marker_size=None):
        """
        Plot dissipation rate vs strain - matching original script choice=="9"
        计算每个文件的耗散比率: (np.trapz(stress, strain))/(4*np.max(stress)*np.max(strain))
        
        Args:
            plot_widget: MatplotlibCanvas widget
            marker_size: Marker size for scatter plots (default 50)
        """
        try:
            # 获取所有数字命名的txt文件
            files = sorted([f for f in os.listdir(self.folder_path)
                          if f.endswith('.txt') and f[:-4].isdigit()],
                          key=lambda x: int(x[:-4]))

            if not files:
                self.plot_error.emit('No numbered txt files found.')
                return

            dissipation_ratios = []
            strain_values = []

            for file in files:
                file_path = os.path.join(self.folder_path, file)
                data = self._load_data(file_path)

                if data is None or data.shape[1] < 3:
                    continue

                stress = data[:, 1]  # 第二列
                strain = data[:, 2]  # 第三列

                # 计算耗散比率
                dissipation_ratio = np.trapz(stress, strain) / (4 * np.max(stress) * np.max(strain))
                dissipation_ratios.append(dissipation_ratio)
                strain_values.append(np.max(np.abs(strain)))

            if not dissipation_ratios:
                self.plot_error.emit('No valid data for dissipation calculation.')
                return

            if hasattr(plot_widget, 'fig'):
                # Use matplotlib - matching original script choice==9
                import matplotlib.colors as mcolors
                strain_arr = np.array(strain_values)
                cmap_name = self._get_cmap('viridis')
                
                plot_widget.fig.clear()
                ax = plot_widget.fig.add_subplot(111)
                
                # 使用对数映射（参考ST程序）
                strain_min = np.min(strain_arr)
                strain_max = np.max(strain_arr)
                if strain_min > 0 and strain_max > strain_min:
                    norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
                else:
                    norm = plt.Normalize(vmin=strain_min, vmax=strain_max)
                
                from utils.plot_font import get_label_fontdict, get_title_fontdict, get_legend_fontdict, get_symbol_fontdict, get_transparency, get_marker_shape, get_marker_size
                label_font = get_label_fontdict()
                title_font = get_title_fontdict()
                symbol_font = get_symbol_fontdict()
                transparency = get_transparency()
                marker_shape = get_marker_shape()
                
                scatter = ax.scatter(strain_values, dissipation_ratios, 
                                    c=strain_arr, cmap=cmap_name, norm=norm, s=marker_size, alpha=transparency, 
                                    marker=marker_shape, edgecolors='w', linewidth=0.5)
                
                ax.set_title('Dissipation Ratio vs Strain', fontdict=title_font)
                ax.set_xscale('log')
                ax.set_xlabel('Strain', fontdict=label_font)
                ax.set_ylabel('Dissipation Ratio', fontdict=label_font)
                ax.set_ylim(0, 1)
                ax.grid(False)
                
                cbar = plot_widget.fig.colorbar(scatter, ax=ax)
                cbar.set_label('Strain', fontdict=label_font)
                format_colorbar_log(cbar, strain_min, strain_max)
                
                plot_widget.fig.tight_layout()
                plot_widget.canvas.draw_idle()
            else:
                # Use pyqtgraph
                plot_widget.clear()
                plot_widget.setTitle('Dissipation Ratio vs Strain')
                plot_widget.setLabel('left', 'Dissipation Ratio')
                plot_widget.setLabel('bottom', 'Strain')
                plot_widget.showGrid(x=True, y=True)
                plot_widget.setLogMode(x=True)
                plot_widget.plot(strain_values, dissipation_ratios, pen=pg.mkPen('r', width=2),
                                symbol='o', symbolBrush='r')

            self.log_message.emit(f"Dissipation rate plotted: {len(dissipation_ratios)} files")
            
            # Emit data for table
            self.plot_data_ready.emit('dissipation_rate', {
                'strain': np.array(strain_values),
                'dissipation': np.array(dissipation_ratios)
            })

        except Exception as e:
            self.plot_error.emit(f'Error plotting dissipation: {str(e)}')

        self.plot_finished.emit()

    def plot_stress_bifurcation(self, plot_widget, show_bifurcation=True, marker_size=None):
        """
        Plot stress bifurcation analysis - matching original script choice=="8"
        从每个txt文件计算应力分叉数据并绘制复杂图表
        
        Args:
            plot_widget: MatplotlibCanvas widget
            show_bifurcation: Whether to show bifurcation points
            marker_size: Marker size for scatter plots (default 70)
        """
        try:
            # 获取所有数字命名的txt文件
            files = sorted([f for f in os.listdir(self.folder_path)
                          if f.endswith('.txt') and f[:-4].isdigit()],
                          key=lambda x: int(x[:-4]))

            if not files:
                self.plot_error.emit('No numbered txt files found.')
                return

            # 初始化存储数据 - 按照原始脚本
            max_a_values = []  # stress最大值
            max_b_values = []  # strain最大值
            max_c_values = []  # strain_rate最大值
            d_values = []
            e_values = []
            f_values = []
            g_values = []
            strain_values = []

            for filename in files:
                file_path = os.path.join(self.folder_path, filename)
                data = self._load_data(file_path)

                if data is None or data.shape[1] < 4:
                    continue

                # 预处理后数据格式（4列）：
                # data[:, 0] = 时间
                # data[:, 1] = 应力
                # data[:, 2] = 应变
                # data[:, 3] = 剪切速率
                stress = data[:, 1]
                strain = data[:, 2]
                strain_rate = data[:, 3]

                max_stress = np.max(stress)
                max_strain = np.max(strain)
                max_strain_rate = np.max(strain_rate)

                max_a_values.append(max_stress)
                max_b_values.append(max_strain)
                max_c_values.append(max_strain_rate)

                max_a_index = np.argmax(stress)
                max_b_index = np.argmax(strain)
                max_c_index = np.argmax(strain_rate)

                d_values.append(strain[max_a_index])
                e_values.append(stress[max_b_index])
                f_values.append(stress[max_c_index])
                g_values.append(strain_rate[max_a_index])
                strain_values.append(strain[max_b_index])

            if not max_a_values:
                self.plot_error.emit('No valid data for bifurcation calculation.')
                return

            # 保存应力分叉数据（7列）
            # 第0列：a = 最大应力
            # 第1列：b = 最大应变
            # 第2列：c = 最大剪切速率
            # 第3列：d = 应变在最大应力点的值
            # 第4列：e = 应力在最大应变点的值
            # 第5列：f = 应力在最大剪切速率点的值
            # 第6列：g = 剪切速率在最大应力点的值
            output_file = os.path.join(self.folder_path, 'stress_bifurcation.txt')
            with open(output_file, 'w') as f:
                for a, b, c, d, e, f_val, g in zip(max_a_values, max_b_values, max_c_values,
                                                    d_values, e_values, f_values, g_values):
                    f.write(f"{a} {b} {c} {d} {e} {f_val} {g}\n")
            
            # 读取数据用于绘图
            bif_data = np.loadtxt(output_file, delimiter=' ')
            
            # 提取绘图数据：
            # 第1子图（σ~γ关系）：
            x1 = bif_data[:, 3]  # 应变在最大应力点
            y1 = bif_data[:, 0]  # 最大应力
            x2 = bif_data[:, 1]  # 最大应变
            y2 = bif_data[:, 0]  # 最大应力
            x3 = bif_data[:, 1]  # 最大应变
            y3 = bif_data[:, 4]  # 应力在最大应变点
            
            # 第2子图（σ~γ̇关系）：
            x4 = bif_data[:, 6]  # 剪切速率在最大应力点
            y4 = bif_data[:, 0]  # 最大应力
            x5 = bif_data[:, 2]  # 最大剪切速率
            y5 = bif_data[:, 0]  # 最大应力
            x6 = bif_data[:, 2]  # 最大剪切速率
            y6 = bif_data[:, 5]  # 应力在最大剪切速率点

            strain_array = np.array(strain_values)

            if hasattr(plot_widget, 'fig'):
                # Use matplotlib - matching original script choice==8 style
                import matplotlib.colors as mcolors
                from matplotlib.ticker import ScalarFormatter
                from utils.plot_font import get_label_fontdict, get_title_fontdict, get_legend_fontdict, get_symbol_fontdict, get_transparency
                label_font = get_label_fontdict()
                title_font = get_title_fontdict()
                legend_font = get_legend_fontdict()
                symbol_font = get_symbol_fontdict()
                transparency = get_transparency()
                
                # 设置全局样式（匹配原始脚本）
                plot_widget.fig.clear()
                plot_widget.fig.set_facecolor('white')
                
                # 创建子图网格
                gs = plot_widget.fig.add_gridspec(1, 2, width_ratios=[1, 1], wspace=0.15)
                ax1 = plot_widget.fig.add_subplot(gs[0])
                ax2 = plot_widget.fig.add_subplot(gs[1])
                
                # 设置背景为白色
                ax1.set_facecolor('white')
                ax2.set_facecolor('white')
                
                # 设置坐标轴线加粗（原始脚本要求）
                for ax in [ax1, ax2]:
                    for spine in ax.spines.values():
                        spine.set_color('black')
                        spine.set_linewidth(1.5)
                    ax.tick_params(axis='both', colors='black', width=1.5)
                
                # 颜色映射（使用用户选择的颜色映射）
                selected_cmap = self._get_cmap()
                strain_min = max(strain_array.min(), 1e-6)
                strain_max = strain_array.max()
                norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
                cmap = plt.get_cmap(selected_cmap)
                
                # ================== 第一子图 ==================
                # Stress vs Strain相关关系（匹配原始脚本图1）
                sc1 = ax1.scatter(x1, y1, c=strain_array, cmap=cmap, norm=norm,
                                alpha=transparency, marker='o', s=marker_size, edgecolors='white',
                                linewidths=0.7, label=r'$\sigma_0 \sim \gamma_{\sigma_0}$')
                sc2 = ax1.scatter(x2, y2, c=strain_array, cmap=cmap, norm=norm,
                                alpha=transparency, marker='s', s=marker_size, edgecolors='white',
                                linewidths=0.7, label=r'$\sigma_0 \sim \gamma_0$')
                sc3 = ax1.scatter(x3, y3, c=strain_array, cmap=cmap, norm=norm,
                                alpha=transparency, marker='^', s=marker_size, edgecolors='white',
                                linewidths=0.7, label=r'$\sigma_{\gamma_0} \sim \gamma_0$')
                
                ax1.set_xlabel('Strain', fontdict=label_font)
                ax1.set_ylabel('Stress (Pa)', fontdict=label_font)
                
                legend1 = ax1.legend(prop=legend_font, loc='best', frameon=False)
                
                # 设置对数坐标
                ax1.set_xscale('log')
                ax1.set_yscale('log')
                
                # 自动调整坐标范围（匹配原始脚本）
                all_x1 = np.concatenate((x1, x2, x3))
                x1_min = max(np.min(all_x1[all_x1 > 0]), 1e-6)
                x1_max = np.max(all_x1)
                y1_min = max(np.min(y1), 1e-6)
                y1_max = np.max(y1)
                ax1.set_xlim(x1_min / 10, x1_max * 10)
                ax1.set_ylim(y1_min / 10, y1_max * 10)
                
                ax1.tick_params(axis='both', which='major', colors='black', width=1.5, length=6)
                ax1.grid(False)
                
                # ================== 分叉点检测（弹性李萨如环）==================
                elastic_bif_stress = None
                if show_bifurcation:
                    # 检测 σ₀ 和 σ_γ₀ 的相对偏差超过10%的点
                    # y1 = y2 = σ₀, y3 = σ_γ₀
                    # 跳过负值和零值数据
                    valid_mask_elastic = (y1 > 0) & (y3 > 0)
                    if np.sum(valid_mask_elastic) > 1:
                        valid_y1 = y1[valid_mask_elastic]
                        valid_y3 = y3[valid_mask_elastic]
                        valid_x2 = x2[valid_mask_elastic]
                        
                        deviation_elastic = np.abs(valid_y1 - valid_y3) / valid_y1
                        
                        # 从小应变到大应变找第一个偏差超过10%的点（从重合到偏离）
                        bifurcation_indices_elastic = np.where(deviation_elastic > 0.1)[0]
                        
                        if len(bifurcation_indices_elastic) > 0:
                            bif_idx_elastic = bifurcation_indices_elastic[0]
                            bif_x_elastic = valid_x2[bif_idx_elastic]
                            bif_y_elastic = valid_y1[bif_idx_elastic]
                            bif_deviation_elastic = deviation_elastic[bif_idx_elastic] * 100
                            
                            elastic_bif_stress = bif_y_elastic
                            
                            ax1.axvline(x=bif_x_elastic, color='red', linestyle='--', 
                                       linewidth=1.5, alpha=0.7)
                            ax1.axhline(y=bif_y_elastic, color='red', linestyle='--', 
                                       linewidth=1.5, alpha=0.7)
                            
                            ax1.scatter([bif_x_elastic], [bif_y_elastic], 
                                       color='red', s=150, marker='*', 
                                       edgecolors='black', linewidths=1.5,
                                       zorder=10, label='Bifurcation Point')
                            
                            ax1.annotate(f'Bifurcation\nγ={bif_x_elastic:.3e}\nσ={bif_y_elastic:.3e}\nDev={bif_deviation_elastic:.1f}%',
                                        xy=(bif_x_elastic, bif_y_elastic),
                                        xytext=(bif_x_elastic * 2, bif_y_elastic * 0.5),
                                        fontsize=label_font['size'], fontweight='bold',
                                        arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                                        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', 
                                                 edgecolor='red', alpha=0.8))
                            
                            self.log_message.emit(f"Elastic bifurcation: γ={bif_x_elastic:.3e}, σ={bif_y_elastic:.3e}, Dev={bif_deviation_elastic:.1f}%")
                        else:
                            self.log_message.emit("No elastic bifurcation detected (all deviations < 10%)")
                    else:
                        self.log_message.emit("No valid data for elastic bifurcation detection")
                
                # ================== 第二子图 ==================
                # Stress vs Strain Rate相关关系（匹配原始脚本图2）
                sc4 = ax2.scatter(x4, y4, c=strain_array, cmap=cmap, norm=norm,
                                alpha=transparency, marker='o', s=marker_size, edgecolors='white',
                                linewidths=0.7, label=r'$\dot{\gamma}_{\sigma_0} \sim \sigma_0$')
                sc5 = ax2.scatter(x5, y5, c=strain_array, cmap=cmap, norm=norm,
                                alpha=transparency, marker='s', s=marker_size, edgecolors='white',
                                linewidths=0.7, label=r'$\dot{\gamma}_0 \sim \sigma_0$')
                sc6 = ax2.scatter(x6, y6, c=strain_array, cmap=cmap, norm=norm,
                                alpha=transparency, marker='^', s=marker_size, edgecolors='white',
                                linewidths=0.7, label=r'$\dot{\gamma}_0 \sim \sigma_{\dot{\gamma}_0}$')
                
                ax2.set_xlabel('Strain Rate (1/s)', fontdict=label_font)
                ax2.set_ylabel('Stress (Pa)', fontdict=label_font)
                
                legend2 = ax2.legend(prop=legend_font, loc='best', frameon=False)
                
                # 设置对数坐标
                ax2.set_xscale('log')
                ax2.set_yscale('log')
                
                # 自动调整坐标范围
                all_x4 = np.concatenate((x4, x5, x6))
                x4_min = max(np.min(all_x4[all_x4 > 0]), 1e-6)
                x4_max = np.max(all_x4)
                y4_min = max(np.min(y4), 1e-6)
                y4_max = np.max(y4)
                ax2.set_xlim(x4_min / 10, x4_max * 10)
                ax2.set_ylim(y4_min / 10, y4_max * 10)
                
                ax2.tick_params(axis='both', which='major', colors='black', width=1.5, length=6)
                ax2.grid(False)
                
                # ================== 分叉点检测（粘性李萨如环）==================
                viscous_bif_stress = None
                if show_bifurcation:
                    # 检测 σ₀ 和 σ_γ̇₀ 的相对偏差超过10%的点
                    # y4 = y5 = σ₀, y6 = σ_γ̇₀
                    # 跳过负值和零值数据
                    valid_mask_viscous = (y4 > 0) & (y6 > 0) & (x5 > 0)
                    if np.sum(valid_mask_viscous) > 1:
                        valid_y4 = y4[valid_mask_viscous]
                        valid_y6 = y6[valid_mask_viscous]
                        valid_x5 = x5[valid_mask_viscous]
                        
                        deviation_viscous = np.abs(valid_y4 - valid_y6) / valid_y4
                        
                        # 从大应变到小应变找点（从后往前）
                        # 找第一个偏差超过10%的点（从重合到偏离的分叉点）
                        bifurcation_indices_viscous = np.where(deviation_viscous > 0.1)[0]
                        
                        if len(bifurcation_indices_viscous) > 0:
                            # 从后往前找，取最后一个偏差超过10%的点
                            # 这个点是从重合到偏离的分叉点
                            bif_idx_viscous = bifurcation_indices_viscous[-1]
                            bif_x_viscous = valid_x5[bif_idx_viscous]
                            bif_y_viscous = valid_y4[bif_idx_viscous]
                            bif_deviation_viscous = deviation_viscous[bif_idx_viscous] * 100
                            
                            viscous_bif_stress = bif_y_viscous
                            
                            ax2.axvline(x=bif_x_viscous, color='blue', linestyle='--', 
                                       linewidth=1.5, alpha=0.7)
                            ax2.axhline(y=bif_y_viscous, color='blue', linestyle='--', 
                                       linewidth=1.5, alpha=0.7)
                            
                            ax2.scatter([bif_x_viscous], [bif_y_viscous], 
                                       color='blue', s=150, marker='*', 
                                       edgecolors='black', linewidths=1.5,
                                       zorder=10, label='Bifurcation Point')
                            
                            ax2.annotate(f'Bifurcation\nγ̇={bif_x_viscous:.3e}\nσ={bif_y_viscous:.3e}\nDev={bif_deviation_viscous:.1f}%',
                                        xy=(bif_x_viscous, bif_y_viscous),
                                        xytext=(bif_x_viscous * 2, bif_y_viscous * 0.5),
                                        fontsize=label_font['size'], fontweight='bold',
                                        arrowprops=dict(arrowstyle='->', color='blue', lw=1.5),
                                        bbox=dict(boxstyle='round,pad=0.5', facecolor='cyan', 
                                                 edgecolor='blue', alpha=0.8))
                            
                            self.log_message.emit(f"Viscous bifurcation: γ̇={bif_x_viscous:.3e}, σ={bif_y_viscous:.3e}, Dev={bif_deviation_viscous:.1f}%")
                        else:
                            self.log_message.emit("No viscous bifurcation detected (all deviations < 10%)")
                    else:
                        self.log_message.emit("No valid data for viscous bifurcation detection")
                    
                    # 比较弹性分叉点和粘性分叉点的应力差距
                    if elastic_bif_stress is not None and viscous_bif_stress is not None:
                        if elastic_bif_stress > 0 and viscous_bif_stress > 0:
                            ratio_bif = max(elastic_bif_stress, viscous_bif_stress) / min(elastic_bif_stress, viscous_bif_stress)
                            if ratio_bif > 10:
                                warning_msg = tr("Warning: Large bifurcation stress difference detected.", "Messages")
                                detail_msg = tr("Elastic bifurcation: {:.3e} Pa, Viscous bifurcation: {:.3e} Pa, Ratio: {:.1f}x", "Messages").format(elastic_bif_stress, viscous_bif_stress, ratio_bif)
                                warning_msg_full = f"{warning_msg} {detail_msg}"
                                self.log_message.emit(warning_msg_full)
                                
                                warning_title = tr("Bifurcation Stress Warning", "Messages")
                                warning_header = tr("Large difference between bifurcation stresses detected:", "Messages")
                                elastic_msg = tr("Elastic bifurcation stress:", "Messages")
                                viscous_msg = tr("Viscous bifurcation stress:", "Messages")
                                diff_msg = tr("Ratio:", "Messages")
                                reason_msg = tr("This may indicate data quality issues affecting bifurcation detection.", "Messages")
                                advice_msg = tr("Please carefully evaluate the results.", "Messages")
                                
                                warning_text = f"{warning_header}\n\n{elastic_msg} {elastic_bif_stress:.3e} Pa\n{viscous_msg} {viscous_bif_stress:.3e} Pa\n{diff_msg} {ratio_bif:.1f}x\n\n{reason_msg}\n{advice_msg}"
                                
                                QMessageBox.warning(None, warning_title, warning_text, QMessageBox.Ok)
                
                # ================== 统一颜色条 ==================
                # 在右侧添加颜色条区域
                cbar_ax = plot_widget.fig.add_axes([0.92, 0.15, 0.02, 0.7])
                cbar = plot_widget.fig.colorbar(sc1, cax=cbar_ax, orientation='vertical')
                cbar.set_label('Strain', fontdict=label_font)
                format_colorbar_log(cbar, strain_min, strain_max)
                
                # 添加总标题
                plot_widget.fig.suptitle('Stress Bifurcation Analysis', 
                                        fontsize=title_font['size'], fontweight='bold', y=0.97)
                
                # 手动调整布局（为颜色条留出空间）
                plot_widget.fig.subplots_adjust(left=0.08, right=0.90, bottom=0.1, top=0.9, wspace=0.2)
                
                plot_widget.canvas.draw_idle()
            else:
                # Use pyqtgraph - simplified version
                plot_widget.clear()
                plot_widget.setTitle('Stress Bifurcation')
                plot_widget.setLabel('left', 'Stress')
                plot_widget.setLabel('bottom', 'Value')
                plot_widget.showGrid(x=True, y=True)
                plot_widget.addLegend()
                plot_widget.plot(x2, y2, pen=pg.mkPen('b', width=2), name='σ₀ ~ γ₀')
                plot_widget.plot(x5, y5, pen=pg.mkPen('r', width=2), name='γ̇₀ ~ σ₀')

            self.log_message.emit(f"Stress bifurcation plotted: {len(max_a_values)} files")
            self.log_message.emit(f"Data saved to {output_file}")
            
            self.plot_data_ready.emit('stress_bifurcation', {
                'sigma_0': np.array(max_a_values),
                'gamma_0': np.array(max_b_values),
                'gamma_dot_0': np.array(max_c_values),
                'gamma_sigma_0': np.array(d_values),
                'sigma_gamma_0': np.array(e_values),
                'sigma_gamma_dot_0': np.array(f_values),
                'gamma_dot_sigma_0': np.array(g_values)
            })

        except Exception as e:
            self.plot_error.emit(f'Error plotting bifurcation: {str(e)}')

        self.plot_finished.emit()

    def plot_cage_modulus(self, plot_widget, marker_size=None, plot_type='10'):
        """
        Plot cage modulus analysis (G'/G_cage and G_cage vs Strain)
        绘制笼子模量分析
        
        G_cage定义: dσ/dγ|σ=0，即应力为0时elastic Lissajous曲线的切线模量
        
        Args:
            plot_widget: MatplotlibCanvas widget
            marker_size: Marker size for scatter plots (default 50)
            plot_type: '10' for dual plots, '10a' for G'/G_cage only, '10b' for G_cage only
        """
        fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
        if not os.path.exists(fourier_folder):
            self.plot_error.emit("Fourier coefficients not found. Run Fourier transform first.")
            return
        
        txt_files = sorted([f for f in os.listdir(self.folder_path) if f.endswith(".txt") and f[:-4].isdigit()],
                          key=lambda x: int(x[:-4]))
        
        if not txt_files:
            self.plot_error.emit("No data files found.")
            return
        
        strain_amplitudes = []
        G_prime_values = []
        G_cage_values = []
        G_ratio_values = []
        
        for txt_file in txt_files:
            file_path = os.path.join(self.folder_path, txt_file)
            fourier_file_path = os.path.join(fourier_folder, txt_file)
            
            if not os.path.exists(fourier_file_path):
                self.log_message.emit(f"Fourier file not found for {txt_file}, skipping")
                continue
            
            try:
                data = np.loadtxt(file_path)
                if data.shape[1] < 4:
                    self.log_message.emit(f"Insufficient columns in {txt_file}, skipping")
                    continue
                
                time = data[:, 0]
                stress = data[:, 1]
                strain = data[:, 2]
                strain_rate = data[:, 3]
                
                strain_amp = np.max(abs(strain))
                
                n = np.argmin(np.abs(stress))
                d_sigma_d_gamma = np.gradient(stress, strain)
                G_cage = d_sigma_d_gamma[n]
                
                with open(fourier_file_path, 'r') as f:
                    first_line = f.readline().strip()
                    cols = first_line.replace(',', ' ').split()
                    
                    if len(cols) >= 3:
                        G_prime_raw = float(cols[2])
                    else:
                        self.log_message.emit(f"Invalid format in {txt_file}, skipping")
                        continue
                
                G_prime = G_prime_raw / strain_amp
                
                strain_amplitudes.append(strain_amp)
                G_prime_values.append(G_prime)
                G_cage_values.append(G_cage)
                G_ratio_values.append(G_prime / G_cage)
                
            except Exception as e:
                self.log_message.emit(f"Error processing {txt_file}: {str(e)}, skipping")
                continue
        
        if not strain_amplitudes:
            self.plot_error.emit("No valid data for cage modulus calculation.")
            return
        
        strain_array = np.array(strain_amplitudes)
        G_prime_array = np.array(G_prime_values)
        G_cage_array = np.array(G_cage_values)
        G_ratio_array = np.array(G_ratio_values)
        
        sort_idx = np.argsort(strain_array)
        strain_array = strain_array[sort_idx]
        G_prime_array = G_prime_array[sort_idx]
        G_cage_array = G_cage_array[sort_idx]
        G_ratio_array = G_ratio_array[sort_idx]
        
        if hasattr(plot_widget, 'fig'):
            import matplotlib.colors as mcolors
            from utils.plot_font import get_label_fontdict, get_title_fontdict, get_symbol_fontdict, get_symbol, get_transparency, get_marker_shape
            label_font = get_label_fontdict()
            title_font = get_title_fontdict()
            symbol_font = get_symbol_fontdict()
            transparency = get_transparency()
            marker_shape = get_marker_shape()
            cmap = self._get_cmap('viridis')
            
            plot_widget.fig.clear()
            
            strain_min = np.min(strain_array)
            strain_max = np.max(strain_array)
            if strain_min > 0 and strain_max > strain_min:
                norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
            else:
                norm = plt.Normalize(vmin=strain_min, vmax=strain_max)
            
            if plot_type == '10':
                axs = plot_widget.fig.subplots(1, 2)
                
                sc1 = axs[0].scatter(strain_array, G_ratio_array, c=strain_array, cmap=cmap, norm=norm,
                                    s=marker_size, alpha=transparency, marker=marker_shape, edgecolors='w', linewidth=0.5)
                axs[0].set_title(get_symbol('G_prime_over_G_cage') + " vs Strain", fontdict=title_font)
                axs[0].set_xlabel("Strain", fontdict=label_font)
                axs[0].set_ylabel(get_symbol('G_prime_over_G_cage'), fontdict=symbol_font)
                axs[0].set_xscale('log')
                axs[0].set_yscale('log')
                axs[0].grid(False)
                
                cbar1 = plot_widget.fig.colorbar(sc1, ax=axs[0])
                cbar1.set_label('Strain', fontdict=label_font)
                format_colorbar_log(cbar1, strain_min, strain_max)
                
                sc2 = axs[1].scatter(strain_array, G_cage_array, c=strain_array, cmap=cmap, norm=norm,
                                    s=marker_size, alpha=transparency, marker=marker_shape, edgecolors='w', linewidth=0.5)
                axs[1].set_title(get_symbol('G_cage') + " vs Strain", fontdict=title_font)
                axs[1].set_xlabel("Strain", fontdict=label_font)
                axs[1].set_ylabel(get_symbol('G_cage') + " (Pa)", fontdict=label_font)
                axs[1].set_xscale('log')
                axs[1].set_yscale('log')
                axs[1].grid(False)
                
                cbar2 = plot_widget.fig.colorbar(sc2, ax=axs[1])
                cbar2.set_label('Strain', fontdict=label_font)
                format_colorbar_log(cbar2, strain_min, strain_max)
            
            elif plot_type == '10a':
                ax = plot_widget.fig.add_subplot(111)
                
                sc1 = ax.scatter(strain_array, G_ratio_array, c=strain_array, cmap=cmap, norm=norm,
                                s=marker_size, alpha=transparency, marker=marker_shape, edgecolors='w', linewidth=0.5)
                ax.set_title(get_symbol('G_prime_over_G_cage') + " vs Strain", fontdict=title_font)
                ax.set_xlabel("Strain", fontdict=label_font)
                ax.set_ylabel(get_symbol('G_prime_over_G_cage'), fontdict=symbol_font)
                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.grid(False)
                
                cbar1 = plot_widget.fig.colorbar(sc1, ax=ax)
                cbar1.set_label('Strain', fontdict=label_font)
                format_colorbar_log(cbar1, strain_min, strain_max)
            
            elif plot_type == '10b':
                ax = plot_widget.fig.add_subplot(111)
                
                sc2 = ax.scatter(strain_array, G_cage_array, c=strain_array, cmap=cmap, norm=norm,
                                s=marker_size, alpha=transparency, marker=marker_shape, edgecolors='w', linewidth=0.5)
                ax.set_title(get_symbol('G_cage') + " vs Strain", fontdict=title_font)
                ax.set_xlabel("Strain", fontdict=label_font)
                ax.set_ylabel(get_symbol('G_cage') + " (Pa)", fontdict=label_font)
                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.grid(False)
                
                cbar2 = plot_widget.fig.colorbar(sc2, ax=ax)
                cbar2.set_label('Strain', fontdict=label_font)
                format_colorbar_log(cbar2, strain_min, strain_max)
            
            plot_widget.fig.tight_layout(pad=2.0)
            plot_widget.canvas.draw_idle()
            
            if plot_type == '10':
                self.log_message.emit(f"Cage modulus dual plots for {len(G_cage_values)} files")
            elif plot_type == '10a':
                self.log_message.emit(f"G'/G_cage plotted for {len(G_cage_values)} files")
            else:
                self.log_message.emit(f"G_cage plotted for {len(G_cage_values)} files")
            
            self.plot_data_ready.emit('cage_modulus', {
                'strain': strain_array,
                'G_cage': G_cage_array,
                'G_prime': G_prime_array,
                'G_ratio': G_ratio_array
            })
        else:
            plot_widget.clear()
            plot_widget.setTitle("Cage Modulus Analysis")
            plot_widget.setLabel("left", "$G'/G_{cage}$")
            plot_widget.setLabel("bottom", "Strain")
            plot_widget.plot(strain_array, G_ratio_array, pen=None, symbol="o", symbolBrush="b")
        
        self.plot_finished.emit()

    def plot_fourier_coefficients(self, plot_widget, harmonic_n: int, marker_size=None):
        """
        Plot In/I1 ratio vs strain for a specific harmonic number
        绘制特定谐波数下不同应变对应的In/I1比值
        
        Args:
            plot_widget: MatplotlibCanvas widget
            harmonic_n: Harmonic number
            marker_size: Marker size for scatter plots (default 50)
        """
        fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
        if not os.path.exists(fourier_folder):
            self.plot_error.emit("Fourier coefficients not found. Run Fourier transform first.")
            return
        
        files = sorted([f for f in os.listdir(fourier_folder) if f.endswith(".txt")],
                      key=lambda x: int(x.replace(".txt", "")))
        
        if not files:
            self.plot_error.emit("No Fourier coefficient files found.")
            return
        
        strain_values = []
        ratio_values = []
        
        for file_name in files:
            file_path = os.path.join(fourier_folder, file_name)
            data = self._load_fourier_data(file_path)
            
            if data is None or len(data) < 1:
                continue
            
            I1 = data[0, 0]
            if I1 <= 0:
                continue
            
            if harmonic_n <= len(data):
                I_n = data[harmonic_n - 1, 0]
                ratio = I_n / I1
                
                original_file = os.path.join(self.folder_path, file_name)
                if os.path.exists(original_file):
                    try:
                        orig_data = np.loadtxt(original_file)
                        if orig_data.shape[1] >= 3:
                            max_strain = np.max(orig_data[:, 2])
                            strain_values.append(max_strain)
                            ratio_values.append(ratio)
                    except:
                        continue
        
        if not strain_values:
            self.plot_error.emit(f"No valid data for harmonic n={harmonic_n}")
            return
        
        strain_array = np.array(strain_values)
        ratio_array = np.array(ratio_values)
        
        sort_idx = np.argsort(strain_array)
        strain_array = strain_array[sort_idx]
        ratio_array = ratio_array[sort_idx]
        
        if hasattr(plot_widget, 'fig'):
            import matplotlib.colors as mcolors
            cmap_name = self._get_cmap('viridis')
            
            plot_widget.fig.clear()
            ax = plot_widget.fig.add_subplot(111)
            
            # 使用对数映射（参考ST程序）
            strain_min = np.min(strain_array)
            strain_max = np.max(strain_array)
            if strain_min > 0 and strain_max > strain_min:
                norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
            else:
                norm = plt.Normalize(vmin=strain_min, vmax=strain_max)
            
            from utils.plot_font import get_label_fontdict, get_title_fontdict, get_symbol_fontdict, get_transparency, get_marker_shape
            label_font = get_label_fontdict()
            title_font = get_title_fontdict()
            symbol_font = get_symbol_fontdict()
            transparency = get_transparency()
            marker_shape = get_marker_shape()
            
            scatter = ax.scatter(strain_array, ratio_array,
                                c=strain_array, cmap=cmap_name, norm=norm, s=marker_size, alpha=transparency,
                                marker=marker_shape, edgecolors='w', linewidth=0.5)
            
            ax.set_xlabel('Strain', fontdict=label_font)
            ax.set_ylabel("Iₙ/I₁ (n=" + str(harmonic_n) + ")", fontdict=symbol_font)
            ax.set_title("Fourier Ratio Iₙ/I₁ vs Strain (n=" + str(harmonic_n) + ")", fontdict=title_font)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.grid(False)
            
            cbar = plot_widget.fig.colorbar(scatter, ax=ax)
            cbar.set_label('Strain', fontdict=label_font)
            format_colorbar_log(cbar, strain_min, strain_max)
            
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(1.0)
            
            plot_widget.fig.tight_layout()
            plot_widget.canvas.draw_idle()
            
        else:
            plot_widget.clear()
            plot_widget.setTitle(f"Iₙ/I₁ vs Strain (n={harmonic_n})")
            plot_widget.setLabel("left", f"Iₙ/I₁ (n={harmonic_n})")
            plot_widget.setLabel("bottom", "Strain")
            plot_widget.showGrid(x=True, y=True)
            plot_widget.setLogMode(x=True, y=True)
            plot_widget.plot(strain_array, ratio_array, pen=pg.mkPen("b", width=2),
                           symbol="o", symbolBrush="b")
        
        self.log_message.emit(f"Fourier ratio I_{harmonic_n}/I_1 plotted: {len(strain_values)} files")
        
        # Emit data for table
        self.plot_data_ready.emit('fourier_ratio', {
            'strain': strain_array,
            'ratio': ratio_array,
            'n': harmonic_n
        })
        
        self.plot_finished.emit()
    
    def plot_q_value(self, plot_widget, marker_size=None):
        """
        Plot Q value vs strain: Q = I3/I1/(strain0)^2
        绘制Q值与应变的关系图
        
        Args:
            plot_widget: MatplotlibCanvas widget
            marker_size: Marker size for scatter plots (default 50)
        """
        fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
        if not os.path.exists(fourier_folder):
            self.plot_error.emit("Fourier coefficients not found. Run Fourier transform first.")
            return
        
        files = sorted([f for f in os.listdir(fourier_folder) if f.endswith(".txt")],
                      key=lambda x: int(x.replace(".txt", "")))
        
        if not files:
            self.plot_error.emit("No Fourier coefficient files found.")
            return
        
        strain_values = []
        q_values = []
        
        for file_name in files:
            file_path = os.path.join(fourier_folder, file_name)
            data = self._load_fourier_data(file_path)
            
            if data is None or len(data) < 3:
                continue
            
            I1 = data[0, 0]
            if I1 <= 0:
                continue
            
            I3 = data[2, 0]
            
            original_file = os.path.join(self.folder_path, file_name)
            if os.path.exists(original_file):
                try:
                    orig_data = np.loadtxt(original_file)
                    if orig_data.shape[1] >= 3:
                        strain0 = np.max(np.abs(orig_data[:, 2]))
                        if strain0 > 0:
                            Q = I3 / I1 / (strain0 ** 2)
                            strain_values.append(strain0)
                            q_values.append(Q)
                except:
                    continue
        
        if not strain_values:
            self.plot_error.emit("No valid data for Q value calculation")
            return
        
        strain_array = np.array(strain_values)
        q_array = np.array(q_values)
        
        sort_idx = np.argsort(strain_array)
        strain_array = strain_array[sort_idx]
        q_array = q_array[sort_idx]
        
        if hasattr(plot_widget, 'fig'):
            import matplotlib.colors as mcolors
            cmap_name = self._get_cmap('viridis')
            
            plot_widget.fig.clear()
            ax = plot_widget.fig.add_subplot(111)
            
            strain_min = np.min(strain_array)
            strain_max = np.max(strain_array)
            if strain_min > 0 and strain_max > strain_min:
                norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
            else:
                norm = plt.Normalize(vmin=strain_min, vmax=strain_max)
            
            from utils.plot_font import get_label_fontdict, get_title_fontdict, get_symbol_fontdict, get_transparency, get_marker_shape
            label_font = get_label_fontdict()
            title_font = get_title_fontdict()
            symbol_font = get_symbol_fontdict()
            transparency = get_transparency()
            marker_shape = get_marker_shape()
            
            scatter = ax.scatter(strain_array, q_array,
                                c=strain_array, cmap=cmap_name, norm=norm, s=marker_size, alpha=transparency,
                                marker=marker_shape, edgecolors='w', linewidth=0.5)
            
            ax.set_xlabel('Strain (γ₀)', fontdict=label_font)
            ax.set_ylabel('Q Value', fontdict=symbol_font)
            ax.set_title("Q Value vs Strain", fontdict=title_font)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.grid(False)
            
            cbar = plot_widget.fig.colorbar(scatter, ax=ax)
            cbar.set_label('Strain', fontdict=label_font)
            format_colorbar_log(cbar, strain_min, strain_max)
            
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_color('black')
                spine.set_linewidth(1.0)
            
            plot_widget.fig.tight_layout()
            plot_widget.canvas.draw_idle()
            
        else:
            plot_widget.clear()
            plot_widget.setTitle("Q Value vs Strain")
            plot_widget.setLabel("left", "Q Value")
            plot_widget.setLabel("bottom", "Strain (γ₀)")
            plot_widget.showGrid(x=True, y=True)
            plot_widget.setLogMode(x=True, y=True)
            plot_widget.plot(strain_array, q_array, pen=pg.mkPen("b", width=2),
                           symbol="o", symbolBrush="b")
        
        self.log_message.emit(f"Q value plotted: {len(strain_values)} files")
        
        self.plot_data_ready.emit('q_value', {
            'strain': strain_array,
            'q_value': q_array
        })
        
        self.plot_finished.emit()

    def plot_fourier_multi(self, plot_widget, files_str: str, max_harmonic: int, line_width=None):
        """
        Plot multiple Fourier coefficients Iₙ/I₁ for selected files in 3D
        绘制选定文件的多个谐波系数对比（3D图）
        x轴：Harmonic（谐波数）
        y轴：Strain（应变，百分比）
        z轴：Iₙ/I₁（归一化傅里叶系数）
        
        Args:
            plot_widget: PlotlyWidget or Matplotlib3DWidget
            files_str: Comma-separated file indices
            max_harmonic: Maximum harmonic number
            line_width: Line width for 3D plots (default 5)
        """
        fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
        if not os.path.exists(fourier_folder):
            self.plot_error.emit("Fourier coefficients not found. Run Fourier transform first.")
            return
        
        files = sorted([f for f in os.listdir(fourier_folder) if f.endswith(".txt")],
                      key=lambda x: int(x.replace(".txt", "")))
        
        if not files:
            self.plot_error.emit("No Fourier coefficient files found.")
            return
        
        if files_str:
            indices = [int(x.strip()) for x in files_str.split(',')]
            files = [files[i] for i in indices if i < len(files)]
        
        fig = go.Figure()
        
        cmap = plt.cm.get_cmap(self._get_cmap())
        colors = cmap(np.linspace(0.1, 0.9, len(files)))
        
        valid_count = 0
        fourier_multi_data = {}
        
        for i, file_name in enumerate(files):
            file_path = os.path.join(fourier_folder, file_name)
            data = self._load_fourier_data(file_path)
            
            if data is None or len(data) < 1:
                continue
            
            I1 = data[0, 0]
            if I1 <= 0:
                continue
            
            orig_file = os.path.join(self.folder_path, file_name)
            strain_value = None
            if os.path.exists(orig_file):
                try:
                    orig_data = np.loadtxt(orig_file)
                    if orig_data.shape[1] >= 3:
                        strain_value = np.max(np.abs(orig_data[:, 2]))
                except Exception as e:
                    self.log_message.emit(f"Error loading orig file {file_name}: {str(e)}")
            else:
                self.log_message.emit(f"Original file not found: {orig_file}")
            
            if strain_value is None or strain_value <= 0:
                self.log_message.emit(f"Skipping {file_name}: strain_value={strain_value}")
                continue
            
            harmonics = np.arange(1, min(max_harmonic + 1, len(data) + 1))
            ratios = data[:max_harmonic, 0] / I1
            
            strain_percent = strain_value * 100
            
            color_hex = '#{:02x}{:02x}{:02x}'.format(
                int(colors[i][0] * 255),
                int(colors[i][1] * 255),
                int(colors[i][2] * 255)
            )
            
            fig.add_trace(go.Scatter3d(
                x=harmonics,
                y=[strain_percent] * len(harmonics),
                z=ratios,
                mode='lines+markers',
                line=dict(width=line_width, color=color_hex),
                marker=dict(size=4, color=color_hex),
                name=file_name.replace('.txt', ''),
                hovertemplate='Harmonic: %{x}<br>Strain: %{y:.2f}%<br>Iₙ/I₁: %{z:.2e}<extra></extra>'
            ))
            valid_count += 1
            
            fourier_multi_data[file_name.replace('.txt', '')] = {
                'strain': strain_value,
                'harmonics': harmonics.tolist(),
                'ratios': ratios.tolist()
            }
        
        if valid_count == 0:
            self.plot_error.emit("No valid data to plot.")
            return
        
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title='Harmonic',
                    tickmode='auto',
                    tickfont=dict(size=12, family='Times New Roman')
                ),
                yaxis=dict(
                    title='Strain (%)',
                    type='log',
                    tickmode='array',
                    tickvals=[0.1, 1, 10, 100, 1000, 2000],
                    ticktext=['0.1', '1', '10', '100', '1000', '2000'],
                    tickfont=dict(size=12, family='Times New Roman')
                ),
                zaxis=dict(
                    title='Iₙ/I₁',
                    type='log',
                    tickmode='array',
                    tickvals=[1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1],
                    ticktext=['10⁻⁵', '10⁻⁴', '10⁻³', '10⁻²', '10⁻¹', '10⁰'],
                    tickfont=dict(size=12, family='Times New Roman')
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1)
            ),
            title='Fourier Coefficients Iₙ/I₁',
            font=dict(family='Times New Roman', size=14),
            legend=dict(x=1.02, y=1, font=dict(size=10)),
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        if hasattr(plot_widget, 'set_plotly_figure'):
            plot_widget.set_plotly_figure(fig)
        else:
            fig.show()
        
        self.log_message.emit(f"Multi-file Fourier 3D plotted: {valid_count} files")
        
        self.plot_data_ready.emit('fourier_multi', {
            'data': fourier_multi_data,
            'max_harmonic': max_harmonic
        })
        
        self.plot_finished.emit()

    def _load_fourier_data(self, file_path) -> Optional[np.ndarray]:
        """Load Fourier coefficient data from file"""
        if not os.path.exists(file_path):
            self.log_message.emit(f"Fourier file not found: {file_path}")
            return None
        try:
            data = np.loadtxt(file_path, dtype=np.float64, delimiter=',')
            return data
        except Exception as e:
            self.log_message.emit(f"Error loading Fourier data: {str(e)}")
            return None

    def plot_lissajous_3d(self, gl_widget, data, title="Lissajous 3D"):
        """
        Plot 3D Lissajous curve using matplotlib or OpenGL
        """
        try:
            if data.dtype.kind in ('U', 'S', 'O'):
                data = np.asarray(data, dtype=np.float64)

            time = data[:, 0]
            stress = data[:, 1]
            strain = data[:, 2]
            strain_rate = data[:, 3] if data.shape[1] > 3 else np.gradient(strain, time)

            print(f'[DEBUG] plot_lissajous_3d widget type: {type(gl_widget).__name__}')

            colormap_name = self._get_cmap('viridis')

            # Check widget type
            if type(gl_widget).__name__ in ['Matplotlib3DWidget', 'PlotlyWidget']:
                # Use matplotlib 3D
                gl_widget.plot_lissajous_3d(strain, stress, strain_rate,
                                             title=title, colormap=colormap_name)
            else:
                # Use pyqtgraph OpenGL
                gl_widget.clear()

                # Normalize for color
                time_norm = (time - time.min()) / (time.max() - time.min())
                colors = plt.cm.get_cmap(colormap_name)(time_norm)

                # Create 3D scatter
                pos = np.column_stack([strain, stress, strain_rate])
                scatter = GLScatterPlotItem(pos=pos, color=colors, size=2)
                gl_widget.addItem(scatter)

                # Create line
                line = GLLinePlotItem(pos=pos, color=colors, width=1)
                gl_widget.addItem(line)

            self.plot_finished.emit()

        except Exception as e:
            self.plot_error.emit(f'Data conversion error: {str(e)}')

    def plot_multiple_lissajous_3d(self, plot_widget_3d, plot_widget_2d, file_indices: List[int], 
                                    legend_titles: List[str]=None, use_normalized: bool=False, line_width=5):
        """Plot 3D Lissajous curves overlayed for multiple files with 2D projections
        
        Args:
            plot_widget_3d: PlotlyWidget or Matplotlib3DWidget instance for 3D plot
            plot_widget_2d: LissajousPlotWidget instance for 2D projections
            file_indices: List of file indices to plot
            legend_titles: Optional list of custom legend titles for each curve
            use_normalized: If True, use normalized strain/stress data
            line_width: Line width for 3D plot (default 5)
        """
        txt_files = self._get_numbered_files()
        
        if legend_titles is None:
            legend_titles = [f"File {idx:03d}" for idx in file_indices]
        
        if len(legend_titles) < len(file_indices):
            legend_titles.extend([f"File {idx:03d}" for idx in file_indices[len(legend_titles):]])
        
        data_list = []
        valid_titles = []
        for i, idx in enumerate(file_indices):
            if idx >= len(txt_files):
                self.log_message.emit(f"Index {idx} out of range, skipping")
            else:
                data = self._load_data(txt_files[idx])
                if data is None:
                    self.log_message.emit(f"Failed to load data for file {idx}")
                else:
                    if use_normalized:
                        data = self.normalize_data(data)
                    data_list.append(data)
                    valid_titles.append(legend_titles[i])
        
        if not data_list:
            self.plot_error.emit("No valid data to plot")
            return
        
        colormap_name = self._get_cmap("viridis")
        
        if hasattr(plot_widget_3d, 'plot_lissajous_3d_multi'):
            plot_widget_3d.plot_lissajous_3d_multi(data_list, valid_titles, colormap=colormap_name, line_width=line_width)
            self.log_message.emit(f"3D Lissajous overlay plotted for {len(data_list)} files")
        else:
            self.log_message.emit("Warning: 3D widget does not have plot_lissajous_3d_multi method")
        
        if hasattr(plot_widget_2d, "plot_lissajous_multi"):
            plot_widget_2d.plot_lissajous_multi(data_list, valid_titles, colormap=colormap_name)
            self.log_message.emit(f"2D Projections overlay plotted for {len(data_list)} files")
        
        self.plot_finished.emit()

    def plot_spp_cole_cole(self, plot_widget: PlotWidget, file_index: int, N: int=10):
        """
        Plot SPP Cole-Cole plots

        Args:
            plot_widget: PyQtGraph PlotWidget
            file_index: Index of file to analyze
            N: Number of Fourier harmonics to use
        """
        plot_widget.clear()
        spp_folder = os.path.join(self.folder_path, "SPP Data")
        if not os.path.exists(spp_folder):
            self.plot_error.emit("SPP Data not found. Run SPP method first.")
            return
        files = [f for f in os.listdir(spp_folder) if f.endswith(".txt")]
        files.sort(key=(lambda x: int(x.split("_")[0])))
        if file_index >= len(files):
            self.plot_error.emit("File index out of range.")
            return
        file_path = os.path.join(spp_folder, files[file_index])
        data = self._load_data(file_path)
        if data is None:
            self.plot_error.emit("Failed to load SPP data file")
            return
        if data.ndim == 1:
            self.plot_error.emit("SPP data is 1-dimensional, expected 2D array")
            return
        if data.shape[1] < 2:
            self.plot_error.emit(f"SPP data has only {data.shape[1]} columns, need at least 2")
            return
        G1 = data[:, 0]
        G2 = data[:, 1]
        plot_widget.setTitle(f"Cole-Cole Plot - {files[file_index]}")
        plot_widget.setLabel("left", "$G''_t(t)$")
        plot_widget.setLabel("bottom", "$G'_t(t)$")
        plot_widget.showGrid(x=True, y=True)
        plot_widget.plot(G1, G2, pen=None, symbol="o", symbolSize=5)
        self.plot_finished.emit()

    def plot_spp_derivatives(self, plot_widget: PlotWidget, file_index: int):
        """Plot SPP derivative plots"""
        plot_widget.clear()
        spp_folder = os.path.join(self.folder_path, "SPP Data")
        if not os.path.exists(spp_folder):
            self.plot_error.emit("SPP Data not found. Run SPP method first.")
            return
        files = [f for f in os.listdir(spp_folder) if f.endswith(".txt")]
        files.sort(key=(lambda x: int(x.split("_")[0])))
        if file_index >= len(files):
            self.plot_error.emit("File index out of range.")
            return
        file_path = os.path.join(spp_folder, files[file_index])
        data = self._load_data(file_path)
        if data is None:
            self.plot_error.emit("Failed to load SPP data file")
            return
        if data.ndim == 1:
            self.plot_error.emit("SPP data is 1-dimensional, expected 2D array")
            return
        if data.shape[1] < 4:
            self.plot_error.emit(f"SPP data has only {data.shape[1]} columns, need at least 4 for derivatives")
            return
        dG1_dt = data[:, 2]
        dG2_dt = data[:, 3]
        plot_widget.setTitle(f"SPP Derivatives - {files[file_index]}")
        plot_widget.setLabel("left", "$dG''_t/dt$")
        plot_widget.setLabel("bottom", "$dG'_t/dt$")
        plot_widget.showGrid(x=True, y=True)
        plot_widget.plot(dG1_dt, dG2_dt, pen=None, symbol="o", symbolSize=5)
        self.plot_finished.emit()

    def calculate_st_value(self) -> bool:
        """Calculate ST values and save to ST.txt"""
        import pandas as pd
        
        om = self.omega
        
        strain_values = []
        txt_files = sorted([f for f in os.listdir(self.folder_path) if f.endswith('.txt') and f[:-4].isdigit()],
                          key=lambda x: int(x[:-4]))
        
        for txt_file in txt_files:
            file_path = os.path.join(self.folder_path, txt_file)
            try:
                df = pd.read_csv(file_path, sep=r'\s+|,', engine='python', header=None)
                if df.shape[1] >= 3:
                    strain_column = df.iloc[:, 2]
                    strain_amplitude = strain_column.abs().max()
                    strain_values.append(strain_amplitude)
            except Exception as e:
                self.log_message.emit(f"Error reading {txt_file}: {str(e)}")
        
        fourier_folder = os.path.join(self.folder_path, "fourier_coefficients")
        if not os.path.exists(fourier_folder):
            self.plot_error.emit("fourier_coefficients folder not found. Run preprocessing first.")
            return False
        
        S_values = []
        T_values = []
        G_l_values = []
        G_m_values = []
        eta_l_values = []
        eta_m_values = []
        
        fourier_files = sorted([f for f in os.listdir(fourier_folder) if f.endswith('.txt')],
                              key=lambda x: int(x[:-4]) if x[:-4].isdigit() else x)
        
        for idx, filename in enumerate(fourier_files):
            file_path = os.path.join(fourier_folder, filename)
            
            real = []
            imag = []
            
            strain = strain_values[idx] if idx < len(strain_values) else 1.0
            
            with open(file_path, 'r') as file:
                for line in file:
                    data = line.strip().split(',')
                    if len(data) >= 3:
                        real.append(float(data[1]))
                        imag.append(float(data[2]))
            
            eta_l = 0
            eta_m = 0
            G_m = 0
            G_l = 0
            
            for i in range(0, len(real), 2):
                eta_l += (real[i] / strain) / om
                eta_m += ((i + 1) * real[i] * ((-1) ** (i / 2)) / strain) / om
                G_m += (i + 1) * imag[i] / strain
                G_l += imag[i] * ((-1) ** (i / 2)) / strain
            
            S = (G_l - G_m) / G_l if G_l != 0 else 0
            T = (eta_l - eta_m) / eta_l if eta_l != 0 else 0
            
            S_values.append(S)
            T_values.append(T)
            G_l_values.append(G_l)
            G_m_values.append(G_m)
            eta_l_values.append(eta_l)
            eta_m_values.append(eta_m)
        
        output_file = os.path.join(self.folder_path, "ST.txt")
        with open(output_file, 'w') as f:
            f.write("Strain\tS\tT\tG_l\tG_m\teta_l\teta_m\n")
            for strain, S, T, Gl, Gm, etal, etam in zip(strain_values, S_values, T_values, G_l_values, G_m_values, eta_l_values, eta_m_values):
                f.write(f"{strain}\t{S}\t{T}\t{Gl}\t{Gm}\t{etal}\t{etam}\n")
        
        self.log_message.emit(f"ST values calculated and saved: {len(strain_values)} files")
        self.log_message.emit(f"Output saved to: {output_file}")
        
        return True

    def calculate_stress_bifurcation(self, *args, **kwargs):
        """Calculate stress bifurcation"""
        pass

    def calculate_spp(self, file_index: int, harmonics: int=15) -> bool:
        """Calculate SPP for a single file"""
        txt_files = sorted([f for f in os.listdir(self.folder_path) if f.endswith('.txt') and f[:-4].isdigit()],
                          key=lambda x: int(x[:-4]))
        
        if file_index >= len(txt_files):
            self.plot_error.emit(f"File index {file_index} out of range")
            return False
        
        file_number = txt_files[file_index].replace('.txt', '')
        return self._calculate_spp_single(file_number, harmonics)

    def calculate_spp_batch(self, harmonics: int=15, data_range: int=0) -> bool:
        """Calculate SPP batch for all files"""
        txt_files = sorted([f for f in os.listdir(self.folder_path) if f.endswith('.txt') and f[:-4].isdigit()],
                          key=lambda x: int(x[:-4]))
        
        if not txt_files:
            self.plot_error.emit("No numbered txt files found")
            return False
        
        # Use user-specified omega to support different test frequencies
        om = self.omega
        frequency = om / (2 * np.pi)  # Convert to Hz
        period = 1.0 / frequency  # Calculate period in seconds
        self.log_message.emit(f"Calculating SPP with omega={om:.4f} rad/s, frequency={frequency:.2f} Hz, period={period:.4f} s, harmonics={harmonics}")
        
        spp_folder = os.path.join(self.folder_path, "SPP Data")
        os.makedirs(spp_folder, exist_ok=True)
        
        rebuild_folder = os.path.join(self.folder_path, "rebuild")
        os.makedirs(rebuild_folder, exist_ok=True)
        
        processed_count = 0
        
        for txt_file in txt_files:
            file_number = txt_file.replace('.txt', '')
            fourier_file = os.path.join(self.folder_path, "fourier_coefficients", txt_file)
            
            if not os.path.exists(fourier_file):
                self.log_message.emit(f"Fourier file for {file_number} not found, skipping")
                continue
            
            # Read Fourier coefficients
            real_values = []
            imag_values = []
            with open(fourier_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= harmonics:
                        break
                    data = line.strip().split(',')
                    if len(data) >= 3:
                        real_values.append(float(data[1]))
                        imag_values.append(float(data[2]))
            
            # Read original strain and strain_rate to get data length
            original_file = os.path.join(self.folder_path, txt_file)
            data = np.loadtxt(original_file)
            strain = data[:, 2]
            strain_rate = data[:, 3]
            
            # Dynamic data length (not fixed 1024)
            data_length = len(strain)
            
            # Create time array based on user frequency
            # Time range: [0, period] instead of fixed [0, 1]
            # For 1Hz: period=1s, t∈[0,1]
            # For 2Hz: period=0.5s, t∈[0,0.5]
            t = np.linspace(0, period, data_length)
            
            # Rebuild stress using Fourier series with dynamic length
            stress_rebuilt = np.zeros(data_length)
            for n in range(0, min(harmonics, len(real_values)), 2):
                stress_rebuilt += real_values[n] * np.cos((n + 1) * om * t) + imag_values[n] * np.sin((n + 1) * om * t)
            
            # Save rebuild file
            rebuild_file = os.path.join(rebuild_folder, f"{file_number}_rebuild.txt")
            with open(rebuild_file, 'w') as f:
                for i in range(data_length):
                    f.write(f"{t[i]}\t{stress_rebuilt[i]}\t{strain[i]}\t{strain_rate[i]}\n")
            
            # Build vector P
            P = np.column_stack([strain, strain_rate, stress_rebuilt])
            
            # Calculate P derivative
            P_prime = np.gradient(P, t, axis=0)
            
            # Calculate unit vector T
            norm_P_prime = np.linalg.norm(P_prime, axis=1)
            norm_P_prime[norm_P_prime == 0] = np.finfo(float).eps
            T = P_prime / norm_P_prime[:, np.newaxis]
            
            # Calculate unit vector N
            T_prime = np.gradient(T, t, axis=0)
            norm_T_prime = np.linalg.norm(T_prime, axis=1)
            norm_T_prime[norm_T_prime == 0] = np.finfo(float).eps
            N_vec = T_prime / norm_T_prime[:, np.newaxis]
            
            # Calculate vector B
            B = np.cross(T, N_vec)
            
            # Calculate B projections
            B_strain = np.dot(B, np.array([1, 0, 0]))
            B_strain_rate = np.dot(B, np.array([0, 1, 0]))
            B_stress = np.dot(B, np.array([0, 0, 1]))
            
            # Calculate G1 and G2
            G1 = -B_strain / B_stress
            G2 = -B_strain_rate / B_stress
            
            # Calculate derivatives
            G1_prime = np.gradient(G1, t)
            G2_prime = np.gradient(G2, t)
            
            # Save SPP data
            spp_file = os.path.join(spp_folder, f"{file_number}_spp data.txt")
            with open(spp_file, 'w') as f:
                for i in range(len(G1)):
                    f.write(f"{G1[i]}\t{G2[i]}\t{G1_prime[i]}\t{G2_prime[i]}\n")
            
            processed_count += 1
            self.log_message.emit(f"SPP calculated for file {file_number}")
        
        self.log_message.emit(f"SPP batch calculation complete: {processed_count} files")
        return processed_count > 0

    def calculate_contact_stress_single(self, file_index: int) -> Optional[Dict]:
        """
        Calculate contact stress decomposition for a single file
        Following the exact logic from LAOS数据处理 0416.py choice == "12"

        Returns:
            Dictionary with contact stress parameters and data
        """
        from scipy.optimize import minimize
        txt_files = sorted([f for f in os.listdir(self.folder_path) if f.endswith(".txt") if f[:-4].isdigit()],
          key=(lambda x: int(x[:-4])))
        if file_index >= len(txt_files):
            self.plot_error.emit(f"File index {file_index} out of range")
            return
        file_path = os.path.join(self.folder_path, txt_files[file_index])
        filename = txt_files[file_index]
        try:
            data = np.loadtxt(file_path, dtype=(np.float64))
        except ValueError:
            try:
                data = np.loadtxt(file_path, skiprows=1, dtype=(np.float64))
            except ValueError:
                data = np.genfromtxt(file_path, skip_header=1, filling_values=(np.nan), dtype=(np.float64))
                data = data[~np.any((np.isnan(data)), axis=1)]

        else:
            if data.shape[1] < 4:
                self.plot_error.emit("Data has insufficient columns")
                return
            stress = np.asarray((data[:, 1]), dtype=(np.float64))
            strain = np.asarray((data[:, 2]), dtype=(np.float64))
            strain_rate = np.asarray((data[:, 3]), dtype=(np.float64))
            N = len(strain_rate)

            def calculate_slope(sr, s, center_idx, window_size=5):
                indices = np.arange(center_idx - window_size, center_idx + window_size + 1)
                indices = indices % len(sr)
                x_window = sr[indices]
                y_window = s[indices]
                slope, intercept = np.polyfit(x_window, y_window, 1)
                return slope

            eta_t = np.array([calculate_slope(strain_rate, stress, i) for i in range(N)])
            idx_start_HC = N // 2
            idx_end_HC = 3 * N // 4
            idx_HC = idx_start_HC + np.argmax(eta_t[idx_start_HC:idx_end_HC])
            idx_start_H = 3 * N // 4
            idx_end_H = N
            idx_H = idx_start_H + np.argmin(eta_t[idx_start_H:idx_end_H])
            eta_HC = eta_t[idx_HC]
            eta_H = eta_t[idx_H]
            x0_HC, y0_HC = strain_rate[idx_HC], stress[idx_HC]
            x0_H, y0_H = strain_rate[idx_H], stress[idx_H]
            sigma_H = eta_H * strain_rate
            sigma_C_exp = stress - sigma_H

            def model_xi_evolution(params, strain_data, strain_rate_data):
                k1, k2 = params
                xi = np.zeros_like(strain_data)
                for i in range(len(strain_data) - 1):
                    dgamma = strain_data[i + 1] - strain_data[i]
                    current_xi = xi[i]
                    current_rate = strain_rate_data[i]
                    sgn_rate = np.sign(current_rate) if current_rate != 0 else 0
                    dxidgamma = -k1 * (1 - abs(current_xi)) + k2 * (1 - sgn_rate * current_xi)
                    xi_next = current_xi + dxidgamma * dgamma
                    xi_next = np.clip(xi_next, 0.0, 1.0)
                    xi[i + 1] = xi_next
                else:
                    return xi

            def objective_function(params, strain_data, strain_rate_data, sigma_c_target, eta_c_model):
                k1, k2 = params
                if not 0 < k1 < k2:
                    return 10000000000.0
                xi = model_xi_evolution([k1, k2], strain_data, strain_rate_data)
                dxi_dgamma = np.gradient(xi, strain_data)
                val = (strain_data * dxi_dgamma + xi) * strain_rate_data
                theta = np.where(val > 0, 1.0, 0.0)
                sigma_c_pred = theta * eta_c_model * np.abs(strain_rate_data) * np.sign(xi) * xi ** 2
                error = np.mean((sigma_c_pred - sigma_c_target) ** 2)
                return error

            initial_k1 = 0.1
            initial_k2 = 0.5
            res = minimize(objective_function, x0=[
             initial_k1, initial_k2],
              args=(
             strain, strain_rate, sigma_C_exp, eta_HC),
              method="SLSQP",
              bounds=[
             (0.0001, 10), (0.0001, 20)],
              options={"maxiter": 200})
            k1_opt, k2_opt = res.x
            xi_final = model_xi_evolution([k1_opt, k2_opt], strain, strain_rate)
            xi_max = np.max(np.abs(xi_final))
            strain_amplitude = np.max(np.abs(strain))
            sigma_C_max = np.max(np.abs(sigma_C_exp))
            return {'eta_H':eta_H, 
             'eta_HC':eta_HC, 
             'eta_t':eta_t, 
             'idx_H':idx_H, 
             'idx_HC':idx_HC, 
             'k1':k1_opt, 
             'k2':k2_opt, 
             'sigma_H':sigma_H, 
             'sigma_C_exp':sigma_C_exp, 
             'xi_final':xi_final, 
             'xi_max':xi_max, 
             'strain_amplitude':strain_amplitude, 
             'sigma_C_max':sigma_C_max, 
             'x0_H':x0_H, 
             'y0_H':y0_H, 
             'x0_HC':x0_HC,
             'y0_HC':y0_HC,
             'strain':strain,
             'stress':stress,
             'strain_rate':strain_rate,
             'filename':filename}

    def calculate_contact_stress_batch(self, *args, **kwargs):
        """Calculate contact stress batch"""
        return []

    def normalize_data(self, data):
        """Normalize stress-strain data to [-1, 1] range"""
        import numpy as np
        if data is None or data.shape[1] < 3:
            self.log_message.emit("Invalid data for normalization")
            return data
        normalized_data = data.copy()
        for col in [1, 2, 3]:
            if data.shape[1] > col:
                max_val = np.max(np.abs(data[:, col]))
                if max_val > 0:
                    normalized_data[:, col] = data[:, col] / max_val
        self.log_message.emit("Data normalized to [-1, 1] range")
        return normalized_data

    def plot_lissajous_3d_with_projections(self, plot_widget_3d, plot_widget_2d, data: np.ndarray, file_number: int, line_width=None):
        """Plot 3D Lissajous curve and 2D projections (Elastic and Viscous)

        Args:
            plot_widget_3d: PlotlyWidget or Matplotlib3DWidget instance for 3D plot
            plot_widget_2d: LissajousPlotWidget instance for 2D projections
            data: numpy array with columns [time, stress, strain, strain_rate]
            file_number: File number for title
            line_width: Line width for 3D plot (default 5)
        """
        if data.dtype.kind in ('U', 'S', 'O'):
            data = np.asarray(data, dtype=np.float64)
        
        time = data[:, 0]
        stress = data[:, 1]
        strain = data[:, 2]
        strain_rate = data[:, 3] if data.shape[1] > 3 else np.gradient(strain, time)
        
        colormap_name = self._get_cmap("viridis")
        title = f"Lissajous 3D - File {file_number}"
        
        if hasattr(plot_widget_3d, 'plot_lissajous_3d'):
            plot_widget_3d.plot_lissajous_3d(strain, stress, strain_rate, 
                                              title=title, colormap=colormap_name, line_width=line_width)
            self.log_message.emit(f"3D Lissajous plotted for File {file_number}")
        else:
            self.log_message.emit("Warning: 3D widget does not have plot_lissajous_3d method")
        
        if hasattr(plot_widget_2d, "plot_lissajous"):
            plot_widget_2d.plot_lissajous(data, colormap=colormap_name, line_width=line_width)
            self.log_message.emit(f"2D Projections plotted for File {file_number}")
        else:
            self.log_message.emit("Warning: Projections widget does not have plot_lissajous method")
        
        self.plot_data_ready.emit('lissajous', {
            'file_number': file_number,
            'data': data
        })
        
        self.plot_finished.emit()

    def plot_lissajous_projections_multi(self, plot_widget, file_indices: List[int], legend_titles: List[str]=None, use_normalized: bool=False, plot_subtype: str=None, line_width=5):
        """Plot 2D Lissajous projections overlayed (Elastic and/or Viscous) for multiple files

        Args:
            plot_widget: LissajousPlotWidget instance
            file_indices: List of file indices to plot
            legend_titles: Optional list of custom legend titles for each curve
            use_normalized: If True, use normalized strain/stress data
            plot_subtype: Optional, '3b' for elastic only, '3c' for viscous only, None for both
            line_width: Line width for 2D projections (default 5)
        """
        txt_files = self._get_numbered_files()
        
        if legend_titles is None:
            legend_titles = [f"File {idx:03d}" for idx in file_indices]
        elif len(legend_titles) < len(file_indices):
            legend_titles.extend([f"File {idx:03d}" for idx in file_indices[len(legend_titles):]])

        # Load data for each file
        data_list = []
        valid_titles = []
        for i, idx in enumerate(file_indices):
            if idx >= len(txt_files):
                self.log_message.emit(f"Index {idx} out of range, skipping")
            else:
                data = self._load_data(txt_files[idx])
                if data is None:
                    self.log_message.emit(f"Failed to load data for file {idx}")
                else:
                    if use_normalized:
                        data = self.normalize_data(data)
                    data_list.append(data)
                    valid_titles.append(legend_titles[i])

        # Plot the overlay
        if hasattr(plot_widget, "plot_lissajous_multi") and data_list:
            colormap_name = self._get_cmap("viridis")
            if plot_subtype == '3b':
                if hasattr(plot_widget, "plot_lissajous_elastic_multi"):
                    plot_widget.plot_lissajous_elastic_multi(data_list, valid_titles, colormap=colormap_name, line_width=line_width)
                    self.log_message.emit(f"Elastic Lissajous overlay plotted for {len(data_list)} files")
                else:
                    plot_widget.plot_lissajous_multi(data_list, valid_titles, colormap=colormap_name, line_width=line_width)
                    self.log_message.emit(f"Projections overlay plotted for {len(data_list)} files")
            elif plot_subtype == '3c':
                if hasattr(plot_widget, "plot_lissajous_viscous_multi"):
                    plot_widget.plot_lissajous_viscous_multi(data_list, valid_titles, colormap=colormap_name, line_width=line_width)
                    self.log_message.emit(f"Viscous Lissajous overlay plotted for {len(data_list)} files")
                else:
                    plot_widget.plot_lissajous_multi(data_list, valid_titles, colormap=colormap_name, line_width=line_width)
                    self.log_message.emit(f"Projections overlay plotted for {len(data_list)} files")
            else:
                plot_widget.plot_lissajous_multi(data_list, valid_titles, colormap=colormap_name, line_width=line_width)
                self.log_message.emit(f"Projections overlay plotted for {len(data_list)} files")
        elif hasattr(plot_widget, "clear_plot"):
            plot_widget.clear_plot()
            self.log_message.emit("Warning: Projections widget does not have plot_lissajous_multi method")
        else:
            self.log_message.emit("Warning: Projections widget not properly initialized")
        self.plot_finished.emit()

    def plot_same_strain_in_i1(self):
        """Placeholder method"""
        pass

    def plot_different_strain_in_i1(self):
        """Placeholder method"""
        pass

    def plot_spp_multi(self, plot_widget, file_indices: List[int], legend_titles: List[str]=None, harmonics: int=15, data_range: int=0, marker_size=50):
        """
        Plot SPP method overlay for multiple files
        多文件SPP方法叠加绘图
        
        Args:
            plot_widget: MatplotlibCanvas widget
            file_indices: List of file indices to plot
            legend_titles: Optional list of custom legend titles for each curve
            harmonics: Number of Fourier harmonics (N)
            data_range: 0=Full Data, 1=First Half, 2=Second Half
            marker_size: Marker size for scatter plots (default 50)
        """
        self.log_message.emit(f"Processing all files with N={harmonics}...")
        success = self.calculate_spp_batch(harmonics, data_range)
        if not success:
            self.plot_error.emit("Failed to calculate SPP data for all files.")
            return
        
        spp_folder = os.path.join(self.folder_path, "SPP Data")
        if not os.path.exists(spp_folder):
            self.plot_error.emit("SPP Data not found.")
            return
        
        if legend_titles is None:
            legend_titles = [f"File {idx:03d}" for idx in file_indices]
        elif len(legend_titles) < len(file_indices):
            legend_titles.extend([f"File {idx:03d}" for idx in file_indices[len(legend_titles):]])
        
        data_list = []
        valid_titles = []
        strain_list = []
        
        for i, file_number in enumerate(file_indices):
            file_number_str = str(file_number)
            possible_names = [
                f"{file_number_str}_spp data.txt",
                f"{file_number_str.zfill(3)}_spp data.txt",
                f"{file_number_str.zfill(2)}_spp data.txt"
            ]
            spp_file = None
            for name in possible_names:
                path = os.path.join(spp_folder, name)
                if os.path.exists(path):
                    spp_file = path
                    break
            
            if spp_file is None:
                self.log_message.emit(f"SPP file for number {file_number} not found, skipping")
                continue
            
            data = self._load_data(spp_file)
            if data is None:
                self.log_message.emit(f"Failed to load SPP data for file {file_number}, skipping")
                continue
            
            if data.ndim == 1 or data.shape[1] < 4:
                self.log_message.emit(f"Invalid SPP data format for file {file_number}, skipping")
                continue
            
            n_points = len(data)
            if data_range == 0:
                start_idx = 0
                end_idx = n_points
            elif data_range == 1:
                start_idx = 0
                end_idx = n_points // 2
            else:
                start_idx = n_points // 2
                end_idx = n_points
            
            data_list.append(data[start_idx:end_idx, :4])
            valid_titles.append(legend_titles[i])
            
            orig_data_file = self._get_file_by_number(file_number)
            if orig_data_file is not None:
                orig_data = self._load_data(orig_data_file)
                if orig_data is not None and len(orig_data) >= end_idx:
                    strain = orig_data[start_idx:end_idx, 2]
                    strain_list.append(strain)
        
        if not data_list:
            self.plot_error.emit("No valid SPP data files found.")
            return
        
        if hasattr(plot_widget, "fig"):
            import matplotlib.colors as mcolors
            import matplotlib.cm as cm
            
            plot_widget.fig.clear()
            axs = plot_widget.fig.subplots(1, 2)
            
            # Use user-selected colormap if available, otherwise use custom gradient
            cmap_name = self._get_cmap('jet_r')
            if cmap_name and cmap_name != 'jet_r':
                # User selected a different colormap
                cmap = cm.get_cmap(cmap_name)
                colors = cmap(np.linspace(0.1, 0.9, len(data_list)))
            else:
                # Use custom autumn+cool gradient as default for SPP overlay
                cmap1 = cm.get_cmap('autumn', 256)
                cmap2 = cm.get_cmap('cool', 256)
                colors1 = cmap1(np.linspace(1, 0, 200))
                colors2 = cmap2(np.linspace(0.25, 1, 220))
                combined_colors = np.vstack((colors1, colors2))
                n_colors = len(combined_colors)
                color_indices = np.linspace(0, n_colors-1, len(data_list)).astype(int)
                colors = combined_colors[color_indices]
            
            from utils.plot_font import get_label_fontdict, get_title_fontdict, get_legend_fontdict, get_symbol_fontdict, get_transparency, get_marker_shape
            label_font = get_label_fontdict()
            title_font = get_title_fontdict()
            legend_font = get_legend_fontdict()
            symbol_font = get_symbol_fontdict()
            transparency = get_transparency()
            marker_shape = get_marker_shape()
            
            for i, (data, title, color) in enumerate(zip(data_list, valid_titles, colors)):
                G1 = data[:, 0]
                G2 = data[:, 1]
                dG1_dt = data[:, 2]
                dG2_dt = data[:, 3]
                
                axs[0].scatter(G1, G2, c=[color], s=marker_size, alpha=transparency, 
                              marker=marker_shape, edgecolors='w', linewidth=0.5, label=title)
                axs[1].scatter(dG1_dt, dG2_dt, c=[color], s=marker_size, alpha=transparency,
                              marker=marker_shape, edgecolors='w', linewidth=0.5, label=title)
            
            axs[0].set_title("Cole-Cole plots overlay", fontdict=title_font)
            axs[0].set_xlabel("G′ₜ(t) (Pa)", fontdict=symbol_font)
            axs[0].set_ylabel("G″ₜ(t) (Pa)", fontdict=symbol_font)
            axs[0].grid(False)
            axs[0].legend(prop=legend_font, loc='best')
            
            axs[1].set_title("Time-derivatives overlay", fontdict=title_font)
            axs[1].set_xlabel("dG′ₜ(t)/dt", fontdict=symbol_font)
            axs[1].set_ylabel("dG″ₜ(t)/dt", fontdict=symbol_font)
            axs[1].grid(False)
            axs[1].legend(prop=legend_font, loc='best')
            
            plot_widget.fig.tight_layout(pad=2.0)
            plot_widget.canvas.draw_idle()
            
            self.log_message.emit(f"SPP overlay plotted for {len(data_list)} files")
        else:
            plot_widget.clear()
            plot_widget.setTitle("SPP Method Overlay")
            plot_widget.setLabel("left", "$G_2$ (Pa)")
            plot_widget.setLabel("bottom", "$G_1$ (Pa)")
            for i, (data, title) in enumerate(zip(data_list, valid_titles)):
                G1 = data[:, 0]
                G2 = data[:, 1]
                plot_widget.plot(G1, G2, pen=None, symbol="o", symbolBrush=(i, len(data_list)), name=title)
        
        self.plot_finished.emit()

    def plot_spp_method(self, plot_widget, file_number: int, harmonics: int, data_range: int=0, marker_size=None):
        """
        Plot SPP method results using matplotlib - matching LAOS数据处理 0417.py choice=="7"

        First processes ALL files, then plots the specified file.

        Args:
            plot_widget: MatplotlibCanvas widget
            file_number: File number to plot (e.g., 30 for '030.txt')
            harmonics: Number of Fourier harmonics (N)
            data_range: 0=Full Data, 1=First Half, 2=Second Half
            marker_size: Marker size for scatter plots (default 50)
        """
        self.log_message.emit(f"Processing all files with N={harmonics}...")
        success = self.calculate_spp_batch(harmonics, data_range)
        if not success:
            self.plot_error.emit("Failed to calculate SPP data for all files.")
            return

        spp_folder = os.path.join(self.folder_path, "SPP Data")
        if not os.path.exists(spp_folder):
            self.plot_error.emit("SPP Data not found.")
            return

        file_number_str = str(file_number)
        possible_names = [
            f"{file_number_str}_spp data.txt",
            f"{file_number_str.zfill(3)}_spp data.txt",
            f"{file_number_str.zfill(2)}_spp data.txt"
        ]
        spp_file = None
        for name in possible_names:
            path = os.path.join(spp_folder, name)
            if os.path.exists(path):
                spp_file = path
                break

        if spp_file is None:
            self.plot_error.emit(f"SPP file for number {file_number} not found.")
            return

        data = self._load_data(spp_file)
        if data is None:
            self.plot_error.emit("Failed to load SPP data.")
            return

        if data.ndim == 1 or data.shape[1] < 4:
            self.plot_error.emit("Invalid SPP data format.")
            return

        n_points = len(data)
        if data_range == 0:
            start_idx = 0
            end_idx = n_points
        elif data_range == 1:
            start_idx = 0
            end_idx = n_points // 2
        else:
            start_idx = n_points // 2
            end_idx = n_points

        G1 = data[start_idx:end_idx, 0]
        G2 = data[start_idx:end_idx, 1]
        dG1_dt = data[start_idx:end_idx, 2]
        dG2_dt = data[start_idx:end_idx, 3]

        if hasattr(plot_widget, "fig"):
            import matplotlib.colors as mcolors
            plot_widget.fig.clear()
            axs = plot_widget.fig.subplots(1, 2)

            # Get strain from original data file
            orig_data_file = self._get_file_by_number(file_number)
            strain = None
            if orig_data_file is not None:
                orig_data = self._load_data(orig_data_file)
                if orig_data is not None and len(orig_data) >= end_idx:
                    strain = orig_data[start_idx:end_idx, 2]

            from utils.plot_font import get_label_fontdict, get_title_fontdict, get_symbol_fontdict
            label_font = get_label_fontdict()
            title_font = get_title_fontdict()
            symbol_font = get_symbol_fontdict()

            # Set up normalization
            if strain is not None and len(strain) > 0:
                strain_min = np.min(strain)
                strain_max = np.max(strain)
                if strain_min > 0 and strain_max > strain_min:
                    norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
                else:
                    norm = plt.Normalize(vmin=strain_min, vmax=strain_max)
            else:
                strain = np.linspace(1, len(G1), len(G1))
                strain_min = np.min(strain)
                strain_max = np.max(strain)
                if strain_min > 0 and strain_max > strain_min:
                    norm = mcolors.LogNorm(vmin=strain_min, vmax=strain_max)
                else:
                    norm = plt.Normalize(vmin=strain_min, vmax=strain_max)

            scatter1 = axs[0].scatter(G1, G2, c=strain, cmap=self._get_cmap(), norm=norm, s=marker_size,
                                       alpha=0.8, edgecolors="w", linewidth=0.5)
            axs[0].set_title("Cole-Cole plots of G′ₜ(t) and G″ₜ(t)", fontdict=title_font)
            axs[0].set_xlabel("G′ₜ(t) (Pa)", fontdict=symbol_font)
            axs[0].set_ylabel("G″ₜ(t) (Pa)", fontdict=symbol_font)
            cbar1 = plot_widget.fig.colorbar(scatter1, ax=axs[0])
            cbar1.set_label('Strain', fontdict=label_font)
            format_colorbar_log(cbar1, strain_min, strain_max)
            
            scatter2 = axs[1].scatter(dG1_dt, dG2_dt, c=strain, cmap=self._get_cmap(), norm=norm, s=marker_size,
                                       alpha=0.8, edgecolors="w", linewidth=0.5)
            axs[1].set_title("Time-derivatives of transient moduli", fontdict=title_font)
            axs[1].set_xlabel("dG′ₜ(t)/dt", fontdict=symbol_font)
            axs[1].set_ylabel("dG″ₜ(t)/dt", fontdict=symbol_font)
            axs[1].grid(False)
            cbar2 = plot_widget.fig.colorbar(scatter2, ax=axs[1])
            cbar2.set_label('Strain', fontdict=label_font)
            format_colorbar_log(cbar2, strain_min, strain_max)
            
            plot_widget.fig.tight_layout()
            plot_widget.canvas.draw_idle()
            
            self.log_message.emit(f"SPP method plotted for file {file_number}")
        else:
            plot_widget.clear()
            plot_widget.setTitle("SPP Method")
            plot_widget.setLabel("left", "$G_2$ (Pa)")
            plot_widget.setLabel("bottom", "$G_1$ (Pa)")
            plot_widget.plot(G1, G2, pen=None, symbol="o", symbolBrush="b")
        
        # Emit data for table display
        self.plot_data_ready.emit("spp", {
            "file_number": str(file_number),
            "data": data
        })
        
        self.plot_finished.emit()