# decompyle3 version 3.9.3
"""
LAOS Analysis GUI Application
PyQt5 + PyQtGraph implementation for LAOS data analysis

Usage:
    python main.py
"""
import sys, os, logging
from pathlib import Path
if getattr(sys, "frozen", False):
    application_path = sys._MEIPASS
    qt_bin_path = os.path.join(application_path, "PyQt5", "Qt5", "bin")
    qt_internal_path = application_path
    
    webengine_process = os.path.join(qt_bin_path, "QtWebEngineProcess.exe")
    if os.path.exists(webengine_process):
        os.environ["QTWEBENGINEPROCESS_PATH"] = webengine_process
    
    dll_paths = [qt_bin_path, qt_internal_path]
    for dll_path in dll_paths:
        if os.path.exists(dll_path):
            os.environ["PATH"] = dll_path + ";" + os.environ.get("PATH", "")
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(dll_path)
                except Exception as e:
                    pass
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, application_path)
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from ui.main_window import MainWindow
from utils.config import Config
from utils.i18n import init_translator, tr
from utils.settings import get_settings

def setup_logging():
    """Configure logging system"""
    log_format = Config.LOG_FORMAT
    if getattr(sys, "frozen", False):
        log_dir = os.path.join(os.path.expanduser("~"), "LAOS_Analysis", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, Config.LOG_FILE)
    else:
        log_file = os.path.join(os.path.dirname(__file__), Config.LOG_FILE)
    logging.basicConfig(level=(getattr(logging, Config.LOG_LEVEL)),
      format=log_format,
      handlers=[
     logging.StreamHandler(),
     logging.FileHandler(log_file, encoding="utf-8")])
    return logging.getLogger(__name__)


def check_dependencies():
    """Check that all required dependencies are installed"""
    missing = []
    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import pandas
    except ImportError:
        missing.append("pandas")

    try:
        import scipy
    except ImportError:
        missing.append("scipy")

    try:
        from PyQt5 import QtWidgets
    except ImportError:
        missing.append("PyQt5")

    try:
        import pyqtgraph
    except ImportError:
        missing.append("pyqtgraph")
    else:
        try:
            from pyqtgraph import opengl
        except ImportError:
            missing.append("PyOpenGL")
        else:
            return missing


def create_directories():
    """Create necessary directories"""
    if getattr(sys, "frozen", False):
        base_path = Path(os.path.join(os.path.expanduser("~"), "LAOS_Analysis"))
    else:
        base_path = Path(__file__).parent
    directories = ["output", "logs"]
    for directory in directories:
        try:
            (base_path / directory).mkdir(exist_ok=True, parents=True)
        except Exception as e:
            try:
                alt_path = Path(os.path.join(os.path.expanduser("~"), "LAOS_Analysis"))
                (alt_path / directory).mkdir(exist_ok=True, parents=True)
            except Exception as inner_e:
                pass


def set_application_style(app: QApplication):
    """Set application style and font for modern look"""
    app.setStyle("Fusion")
    from utils.responsive import get_ui_scale
    ui_scale = get_ui_scale()
    try:
        saved_size = get_settings().get_font_size()
    except Exception:
        saved_size = 10
    ui_scale.set_from_font_point_size(saved_size)
    font = QFont("Segoe UI")
    font.setPointSizeF(ui_scale.font_point_size())
    font.setStyleStrategy(QFont.PreferAntialias)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)
    from PyQt5.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(33, 33, 33))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(250, 250, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(33, 33, 33))
    palette.setColor(QPalette.Text, QColor(33, 33, 33))
    palette.setColor(QPalette.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(33, 33, 33))
    palette.setColor(QPalette.BrightText, QColor(255, 87, 34))
    palette.setColor(QPalette.Link, QColor(33, 150, 243))
    palette.setColor(QPalette.Highlight, QColor(33, 150, 243))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(158, 158, 158))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(158, 158, 158))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(158, 158, 158))
    app.setPalette(palette)


def main():
    """Main entry point"""
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    logger = setup_logging()
    logger.info("LAOS Analysis starting...")
    logger.info(f"Application path: {application_path}")
    logger.info(f'Frozen: {getattr(sys, "frozen", False)}')
    missing = check_dependencies()
    if missing:
        error_msg = f'Missing required dependencies:\n{chr(10).join(("- " + m for m in missing))}\n\nPlease install them with:\npip install {" ".join(missing)}'
        print(error_msg)
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Missing Dependencies", error_msg)
        except Exception as e:
            pass
        sys.exit(1)
    logger.info("Dependencies checked OK")
    try:
        create_directories()
        logger.info("Directories created")
    except Exception as e:
        logger.warning(f"Could not create directories: {e}")

    else:
        logger.info("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("LAOS Analysis")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("LAOS Analysis")
        icon_path_png = os.path.join(application_path, "resources", "icons", "icon_64.png")
        icon_path_svg = os.path.join(application_path, "resources", "icons", "icon_64.svg")
        icon_path = icon_path_png if os.path.exists(icon_path_png) else icon_path_svg
        logger.info(f"Icon path: {icon_path}")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            logger.info("Icon loaded")
        else:
            logger.warning("Icon not found")
        logger.info("Initializing translator...")
        try:
            settings = get_settings()
            saved_language = settings.get_language()
            logger.info(f"Saved language setting: {saved_language}")
            init_translator(saved_language)
            logger.info("Translator initialized")
        except Exception as e:
            logger.warning(f"Translator init failed: {e}")
        
        logger.info("Setting application style...")
        set_application_style(app)
        import pyqtgraph as pg
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        pg.setConfigOption("antialias", True)
        logger.info("PyQtGraph configured")
        
        logger.info("Initializing matplotlib fonts...")
        try:
            from utils.plot_font import init_matplotlib_fonts
            init_matplotlib_fonts()
            logger.info("Matplotlib fonts initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize fonts: {e}")
        
        try:
            logger.info("Creating MainWindow...")
            logger.info("Step 1: Importing MainWindow class...")
            from ui.main_window import MainWindow
            logger.info("Step 2: MainWindow class imported successfully")
            logger.info("Step 3: Creating MainWindow instance...")
            window = MainWindow()
            logger.info("Step 4: MainWindow instance created successfully")
            logger.info("MainWindow created")
            screen = app.primaryScreen()
            screen_geometry = screen.availableGeometry()
            window_width = window.width()
            window_height = window.height()
            x = (screen_geometry.width() - window_width) // 2
            y = (screen_geometry.height() - window_height) // 2
            window.move(x, y)
            window.show()
            logger.info("Window shown")
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}", exc_info=True)
            QMessageBox.critical(None, "Startup Error", f"Failed to start application:\n{str(e)}")
            sys.exit(1)
        
        logger.info("Starting event loop...")
        exit_code = app.exec_()
        logger.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
