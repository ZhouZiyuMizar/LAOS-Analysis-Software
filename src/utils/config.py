# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: utils\config.py
"""
Configuration settings for LAOS Analysis GUI Application
PyQt5 + PyQtGraph implementation
"""

class Config:
    __doc__ = "Application configuration class"
    WINDOW_TITLE = "LAOS Analysis"
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 800
    LEFT_PANEL_MIN_WIDTH = 250
    RIGHT_PANEL_MIN_WIDTH = 280
    MIDDLE_PANEL_MIN_WIDTH = 500
    THEME = "light"
    COLORS = {
        'primary': '"#2196F3"',
        'secondary': '"#FF5722"',
        'accent': '"#4CAF50"',
        'background': '"#FAFAFA"',
        'text': '"#212121"',
        'grid': '"#E0E0E0"'
    }
    PLOT_SETTINGS = {
        'colormap_2d': '"viridis"',
        'colormap_3d': '"jet"',
        'line_width': 2,
        'marker_size': 8,
        'font_family': '"Arial"',
        'font_size': 12,
        'title_font_size': 14
    }
    COLORMAP_GENERAL = [
        ('viridis', 'Viridis'),
        ('plasma', 'Plasma'),
        ('inferno', 'Inferno'),
        ('magma', 'Magma'),
        ('cividis', 'Cividis'),
        ('Greys', 'Greys'),
        ('Purples', 'Purples'),
        ('Blues', 'Blues'),
        ('Greens', 'Greens'),
        ('Oranges', 'Oranges'),
        ('Reds', 'Reds'),
        ('YlOrBr', 'Yellow-Orange-Brown'),
        ('YlOrRd', 'Yellow-Orange-Red'),
        ('YlGn', 'Yellow-Green'),
        ('YlGnBu', 'Yellow-Green-Blue'),
        ('GnBu', 'Green-Blue'),
        ('PuBu', 'Purple-Blue'),
        ('PuBuGn', 'Purple-Blue-Green'),
        ('BuGn', 'Blue-Green'),
        ('BuPu', 'Blue-Purple'),
        ('hot', 'Hot'),
        ('afmhot', 'AFM Hot'),
        ('gist_heat', 'Gist Heat'),
        ('copper', 'Copper'),
        ('coolwarm', 'Coolwarm'),
        ('RdBu', 'RdBu'),
        ('RdGy', 'RdGy'),
        ('RdYlBu', 'RdYlBu'),
        ('RdYlGn', 'RdYlGn'),
        ('PiYG', 'PiYG'),
        ('PRGn', 'PRGn'),
        ('BrBG', 'BrBG'),
        ('PuOr', 'PuOr'),
        ('Spectral', 'Spectral'),
        ('seismic', 'Seismic'),
        ('bwr', 'BWR'),
        ('rainbow', 'Rainbow'),
        ('jet', 'Jet'),
        ('turbo', 'Turbo'),
        ('gist_rainbow', 'Gist Rainbow'),
        ('nipy_spectral', 'Nipy Spectral'),
        ('twilight', 'Twilight'),
        ('hsv', 'HSV'),
        ('gnuplot', 'Gnuplot'),
        ('gnuplot2', 'Gnuplot 2'),
        ('CMRmap', 'CMRmap'),
        ('cubehelix', 'Cubehelix'),
        ('ocean', 'Ocean'),
        ('gist_earth', 'Gist Earth'),
        ('terrain', 'Terrain'),
        ('gist_ncar', 'Gist NCAR')
    ]
    
    COLORMAP_NOT_3D = [
        ('OrRd', 'Orange-Red'),
        ('PuRd', 'Purple-Red'),
        ('RdPu', 'Red-Purple'),
        ('binary', 'Binary'),
        ('gist_yarg', 'Gist Yarg'),
        ('gist_gray', 'Gist Gray'),
        ('gray', 'Gray'),
        ('bone', 'Bone'),
        ('pink', 'Pink'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
        ('cool', 'Cool'),
        ('Wistia', 'Wistia'),
        ('twilight_shifted', 'Twilight Shifted'),
        ('Pastel1', 'Pastel 1'),
        ('Pastel2', 'Pastel 2'),
        ('Paired', 'Paired'),
        ('Accent', 'Accent'),
        ('Dark2', 'Dark 2'),
        ('Set1', 'Set 1'),
        ('Set2', 'Set 2'),
        ('Set3', 'Set 3'),
        ('tab10', 'Tab 10'),
        ('tab20', 'Tab 20'),
        ('tab20b', 'Tab 20b'),
        ('tab20c', 'Tab 20c'),
        ('flag', 'Flag'),
        ('prism', 'Prism'),
        ('gist_stern', 'Gist Stern'),
        ('brg', 'BRG')
    ]
    COLORMAP_REVERSE_OPTIONS = [
        ('viridis_r', 'Viridis (Reverse)'),
        ('plasma_r', 'Plasma (Reverse)'),
        ('inferno_r', 'Inferno (Reverse)'),
        ('magma_r', 'Magma (Reverse)'),
        ('cividis_r', 'Cividis (Reverse)'),
        ('turbo_r', 'Turbo_r (Recommended for Stress Bifurcation)'),
        ('jet_r', 'Jet_r (Recommended for SPP Overlay)'),
        ('rainbow_r', 'Rainbow (Reverse)'),
        ('hot_r', 'Hot (Reverse)'),
        ('coolwarm_r', 'Coolwarm (Reverse)'),
        ('RdBu_r', 'RdBu (Reverse)'),
        ('seismic_r', 'Seismic (Reverse)')
    ]
    
    @classmethod
    def get_all_colormaps_grouped(cls):
        """Get all colormaps grouped by 3D compatibility"""
        general_colormaps = cls.COLORMAP_GENERAL + cls.COLORMAP_REVERSE_OPTIONS
        not_3d_colormaps = cls.COLORMAP_NOT_3D
        return general_colormaps, not_3d_colormaps
    DEFAULT_INPUT_PATH = ""
    DEFAULT_OUTPUT_PATH = "output"
    DATA_PROCESSING = {
        'points_per_cycle': 512,
        'phase_correction_index': 128,
        'fourier_harmonics': 14
    }
    PLOT_TYPES = [
        ('1', '李萨如曲线'),
        ('4', 'S-T值曲线'),
        ('5', '相同应变不同谐波'),
        ('6', '不同应变相同谐波'),
        ('8', '应力分叉分析'),
        ('9', '耗散率曲线'),
        ('10', '笼子模量曲线')
    ]
    SPP_SUBTYPES = [
        ('7a', '计算并绘图'),
        ('7b', '多文件叠加')
    ]

    @classmethod
    def get_translated_plot_types(cls):
        """Get plot types with translated names"""
        from utils.i18n import tr
        return [(code, tr(name, "PlotTypes")) for code, name in cls.PLOT_TYPES]

    FILE_FILTERS = {
        'txt': "Text Files (*.txt)",
        'excel': "Excel Files (*.xlsx *.xls)",
        'all': "All Files (*.*)"
    }
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "laos_analysis.log"
    LOG_LEVEL = "INFO"