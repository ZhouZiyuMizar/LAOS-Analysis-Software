'''
Font utilities for consistent plot styling in LAOS Analysis
Provides Times New Roman Bold for labels/titles
Only physical variable symbols use italic (via LaTeX $...$ notation)
'''

import matplotlib.pyplot as plt
from matplotlib import font_manager
import logging

logger = logging.getLogger(__name__)

SUBSCRIPT_DIGITS = ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
SUBSCRIPT_LETTERS = {
    'a': 'ₐ', 'e': 'ₑ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ᵢ', 'k': 'ₖ', 'l': 'ₗ', 
    'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ', 'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ', 'x': 'ₓ'
}
PRIME = '′'
DOUBLE_PRIME = '″'

AVAILABLE_FONT_FAMILIES = [
    "Times New Roman", 
    "Arial", 
    "SimHei",
    "Calibri",
    "Georgia",
    "Verdana",
    "Tahoma",
    "Palatino Linotype",
    "Cambria",
    "Courier New"
]


def init_matplotlib_fonts():
    '''
    Initialize matplotlib font system to ensure all required fonts are available.
    This rebuilds the font cache and registers common fonts.
    
    Call this at application startup to avoid font-related issues.
    '''
    try:
        font_manager._rebuild()
        logger.info("Matplotlib font cache rebuilt")
        
        available_fonts = [f.name for f in font_manager.fontManager.ttflist]
        logger.info(f"Total fonts available: {len(available_fonts)}")
        
        for font_family in AVAILABLE_FONT_FAMILIES:
            if font_family in available_fonts:
                logger.info(f"Font '{font_family}' is available")
            else:
                similar_fonts = [f for f in available_fonts if font_family.lower() in f.lower()]
                if similar_fonts:
                    logger.warning(f"Font '{font_family}' not found exactly, but found similar: {similar_fonts[:3]}")
                else:
                    logger.warning(f"Font '{font_family}' not found in system fonts")
        
        plt.rcParams['font.family'] = 'sans-serif'
        
        plt.rcParams['mathtext.fontset'] = 'stix'
        
        logger.info("Default font family set to sans-serif")
        logger.info("Mathtext fontset set to custom")
        logger.info("Matplotlib fonts initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing fonts: {e}")


def get_available_fonts():
    '''
    Get list of available font families in the system
    
    Returns:
        list: Available font family names
    '''
    return [f.name for f in font_manager.fontManager.ttflist]


def subscript_number(n: int) -> str:
    '''Convert number to Unicode subscript'''
    return ''.join(SUBSCRIPT_DIGITS[int(d)] for d in str(n))


def get_plot_settings():
    """Get current plot settings from settings manager"""
    try:
        from utils.settings import get_settings
        settings = get_settings()
        return {
            'font_family': settings.get_plot_setting("font_family", "Times New Roman"),
            'title_font_size': settings.get_plot_setting("title_font_size", 14),
            'label_font_size': settings.get_plot_setting("label_font_size", 12),
            'annotation_font_size': settings.get_plot_setting("annotation_font_size", 12),
            'legend_font_size': settings.get_plot_setting("legend_font_size", 10),
            'transparency': settings.get_plot_setting("transparency", 0.8),
            'legend_position': settings.get_plot_setting("legend_position", "upper right"),
            'marker_shape': settings.get_plot_setting("marker_shape", "o"),
            'marker_size': settings.get_plot_setting("marker_size", 50),
            'line_width': settings.get_plot_setting("line_width", 5),
            'colormap': settings.get_plot_setting("colormap", "viridis"),
        }
    except Exception:
        return {
            'font_family': 'Times New Roman',
            'title_font_size': 14,
            'label_font_size': 12,
            'annotation_font_size': 12,
            'legend_font_size': 10,
            'transparency': 0.8,
            'legend_position': 'upper right',
            'marker_shape': 'o',
            'marker_size': 50,
            'line_width': 5,
            'colormap': 'viridis',
        }


def get_transparency():
    '''Get current transparency setting'''
    return get_plot_settings()['transparency']


def get_marker_shape():
    '''Get current marker shape setting'''
    return get_plot_settings()['marker_shape']


def get_marker_size():
    '''Get current marker size setting'''
    return get_plot_settings()['marker_size']


def get_line_width():
    '''Get current line width setting'''
    return get_plot_settings()['line_width']


def get_colormap():
    '''Get current colormap setting'''
    return get_plot_settings()['colormap']


def get_legend_position():
    '''Get current legend position setting'''
    return get_plot_settings()['legend_position']


# Plot font settings - Times New Roman, Bold (NOT italic for labels)
PLOT_FONT_FAMILY = 'Times New Roman'
PLOT_FONT_SIZE_LABEL = 12
PLOT_FONT_SIZE_TITLE = 14
PLOT_FONT_SIZE_TICK = 10
PLOT_FONT_SIZE_LEGEND = 9
PLOT_FONT_SIZE_ANNOTATION = 12


def set_font_family_setting(family: str):
    '''
    Set global font family for plots and save to settings
    
    Args:
        family: Font family name (e.g., 'Times New Roman', 'Arial')
    '''
    global PLOT_FONT_FAMILY
    PLOT_FONT_FAMILY = family
    try:
        from utils.settings import get_settings
        settings = get_settings()
        settings.set_plot_setting("font_family", family)
        configure_mathtext()
    except Exception:
        pass


def set_font_size_setting(font_type: str, size: int):
    '''
    Set global font size for specific plot element and save to settings
    
    Args:
        font_type: 'title', 'label', 'tick', or 'legend'
        size: Font size in points
    '''
    global PLOT_FONT_SIZE_TITLE, PLOT_FONT_SIZE_LABEL, PLOT_FONT_SIZE_TICK, PLOT_FONT_SIZE_LEGEND, PLOT_FONT_SIZE_ANNOTATION
    if font_type == "title":
        PLOT_FONT_SIZE_TITLE = size
    elif font_type == "label":
        PLOT_FONT_SIZE_LABEL = size
    elif font_type == "tick":
        PLOT_FONT_SIZE_TICK = size
    elif font_type == "legend":
        PLOT_FONT_SIZE_LEGEND = size
    elif font_type == "annotation":
        PLOT_FONT_SIZE_ANNOTATION = size
    
    try:
        from utils.settings import get_settings
        settings = get_settings()
        settings.set_plot_setting(f"{font_type}_font_size", size)
    except Exception:
        pass


def get_label_fontdict():
    '''
    Get font dictionary for axis labels (Times New Roman, Bold, NOT italic)

    Returns:
        dict: Font properties for matplotlib set_xlabel/set_ylabel
    '''
    settings = get_plot_settings()
    return {
        'family': settings['font_family'],
        'size': settings['label_font_size'],
        'weight': 'bold',
        'style': 'normal'
    }


def get_symbol_fontdict():
    '''
    Get font dictionary for variable symbols (Bold + Italic)

    Returns:
        dict: Font properties for math symbols (bold italic)
    '''
    settings = get_plot_settings()
    return {
        'family': settings['font_family'],
        'size': settings['label_font_size'],
        'weight': 'bold',
        'style': 'italic'
    }


def apply_axis_font(ax, axis='both', fontdict=None):
    '''
    Apply font settings to axis labels
    
    Args:
        ax: Matplotlib axis
        axis: 'x', 'y', or 'both'
        fontdict: Font dictionary (default: label_fontdict)
    '''
    if fontdict is None:
        fontdict = get_label_fontdict()
    
    if axis == 'x' or axis == 'both':
        ax.xaxis.label.set_fontfamily(fontdict['family'])
        ax.xaxis.label.set_fontsize(fontdict['size'])
        ax.xaxis.label.set_fontweight(fontdict['weight'])
    if axis == 'y' or axis == 'both':
        ax.yaxis.label.set_fontfamily(fontdict['family'])
        ax.yaxis.label.set_fontsize(fontdict['size'])
        ax.yaxis.label.set_fontweight(fontdict['weight'])


def get_title_fontdict():
    '''
    Get font dictionary for titles (Times New Roman, Bold, NOT italic)

    Returns:
        dict: Font properties for matplotlib set_title
    '''
    settings = get_plot_settings()
    return {
        'family': settings['font_family'],
        'size': settings['title_font_size'],
        'weight': 'bold',
        'style': 'normal'
    }


def get_tick_fontdict():
    '''
    Get font dictionary for tick labels (Times New Roman, Bold)

    Returns:
        dict: Font properties for tick labels
    '''
    settings = get_plot_settings()
    return {
        'family': settings['font_family'],
        'size': 10,
        'weight': 'bold'
    }


def get_legend_fontdict():
    '''
    Get font dictionary for legends (Times New Roman, Bold)

    Returns:
        dict: Font properties for legends
    '''
    settings = get_plot_settings()
    return {
        'family': settings['font_family'],
        'size': settings['legend_font_size'],
        'weight': 'bold'
    }


def get_annotation_fontdict():
    '''
    Get font dictionary for in-plot annotations (e.g. bifurcation point info)

    Independent from the axis label font so it can be sized separately.

    Returns:
        dict: Font properties for matplotlib annotate()
    '''
    settings = get_plot_settings()
    return {
        'family': settings['font_family'],
        'size': settings['annotation_font_size'],
        'weight': 'bold'
    }


def get_annotation_fontsize():
    '''Get the in-plot annotation font size in points.'''
    return get_plot_settings()['annotation_font_size']


def format_variable(name: str) -> str:
    '''
    Format physical variable name with LaTeX bold italic style
    Variables are bold italic, subscripts are non-italic (Roman)

    Args:
        name: Variable name (e.g., 'gamma', 'sigma', 'G_prime')

    Returns:
        LaTeX formatted string with bold italic variable and Roman subscript
    '''
    var_map = {
        'gamma': r'$\gamma$',
        'gamma_dot': r'$\dot{\gamma}$',
        'sigma': r'$\sigma$',
        'G_prime': "G′",
        'G_double_prime': "G″",
        'Gt_prime': "G′ₜ",
        'Gt_double_prime': "G″ₜ",
        'eta_prime': "η′",
        'xi': r'$\xi$',
        'eta': r'$\eta$',
        'omega': r'$\omega$',
        'n': 'n',
        'I_n': 'Iₙ',
        'I_1': 'I₁',
        'G_L': "G′ₗ",
        'G_M': "G′ₘ",
        'G_cage': r'$\rm{G}_{\rm{cage}}$',
        'G_prime_over_G_cage': r"$\rm{G}'/\rm{G}_{\rm{cage}}$",
        'In_I1': 'Iₙ/I₁',
    }
    return var_map.get(name, f'$\boldsymbol{name}$')


def get_symbol(name: str) -> str:
    '''
    Get LaTeX formatted symbol for a variable name (alias for format_variable)
    
    Args:
        name: Variable name (e.g., 'gamma', 'sigma', 'G_cage')
    
    Returns:
        LaTeX formatted string with bold italic variable and Roman subscript
    '''
    return format_variable(name)


def set_axis_label(ax, axis: str, label: str, fontsize=None):
    '''
    Set axis label with Times New Roman Bold font
    Use $...$ for italic variables within the label

    Args:
        ax: Matplotlib axis object
        axis: 'x', 'y', or 'z'
        label: Label text (use $...$ for italic variables)
        fontsize: Optional custom font size (default: 12)
    '''
    fontdict = get_label_fontdict()
    if fontsize:
        fontdict['size'] = fontsize

    if axis == 'x':
        ax.set_xlabel(label, fontdict=fontdict)
    elif axis == 'y':
        ax.set_ylabel(label, fontdict=fontdict)
    elif axis == 'z':
        ax.set_zlabel(label, fontdict=fontdict)


def set_plot_title(ax, title: str, fontsize=None, pad=None):
    '''
    Set plot title with Times New Roman Bold font

    Args:
        ax: Matplotlib axis object
        title: Title text
        fontsize: Optional custom font size (default: 14)
        pad: Optional padding from top
    '''
    fontdict = get_title_fontdict()
    if fontsize:
        fontdict['size'] = fontsize

    ax.set_title(title, fontdict=fontdict, pad=pad if pad else 15)


def set_tick_style(ax, axis='both'):
    '''
    Set tick label style to Times New Roman Bold

    Args:
        ax: Matplotlib axis object
        axis: 'x', 'y', 'z', or 'both'
    '''
    tick_font = get_tick_fontdict()

    if axis == 'both' or axis == 'x':
        plt.setp(ax.get_xticklabels(),
                 family=tick_font['family'],
                 size=tick_font['size'],
                 weight=tick_font['weight'])
    if axis == 'both' or axis == 'y':
        plt.setp(ax.get_yticklabels(),
                 family=tick_font['family'],
                 size=tick_font['size'],
                 weight=tick_font['weight'])
    if axis == 'z' and hasattr(ax, 'get_zticklabels'):
        plt.setp(ax.get_zticklabels(),
                 family=tick_font['family'],
                 size=tick_font['size'],
                 weight=tick_font['weight'])


def configure_legend(ax, **kwargs):
    '''
    Configure legend with Times New Roman font

    Args:
        ax: Matplotlib axis object
        **kwargs: Additional legend kwargs
    '''
    fontdict = get_legend_fontdict()
    ax.legend(prop=fontdict, **kwargs)


def apply_plot_style(ax, xlabel=None, ylabel=None, zlabel=None, title=None,
                     fontsize_label=None, fontsize_title=None):
    '''
    Apply consistent plot style to an axis

    Args:
        ax: Matplotlib axis object
        xlabel: X-axis label text
        ylabel: Y-axis label text
        zlabel: Z-axis label text (for 3D plots)
        title: Plot title
        fontsize_label: Custom label font size
        fontsize_title: Custom title font size
    '''
    if xlabel:
        set_axis_label(ax, 'x', xlabel, fontsize_label)
    if ylabel:
        set_axis_label(ax, 'y', ylabel, fontsize_label)
    if zlabel:
        set_axis_label(ax, 'z', zlabel, fontsize_label)
    if title:
        set_plot_title(ax, title, fontsize_title)

    set_tick_style(ax)


def set_colorbar_label(cbar, label: str, fontsize=None):
    '''
    Set colorbar label with Times New Roman Bold font

    Args:
        cbar: Matplotlib colorbar object
        label: Label text
        fontsize: Optional custom font size
    '''
    fontdict = get_label_fontdict()
    if fontsize:
        fontdict['size'] = fontsize
    cbar.set_label(label, fontdict=fontdict)


def configure_mathtext():
    '''
    Configure matplotlib mathtext to use current font family
    This ensures math symbols use the same font as regular text
    Call this after changing font settings
    '''
    settings = get_plot_settings()
    font_family = settings['font_family']
    
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    logger.info(f"Mathtext configured with font: {font_family}")