# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: utils\settings.py
"""
Settings Manager - Persistent user settings for LAOS Analysis
"""
import json, os, sys
from pathlib import Path
from typing import Any, Dict, List, Optional

def get_user_data_dir():
    """Get user data directory (works for both source and packaged exe)"""
    if getattr(sys, "frozen", False):
        return Path.home() / "LAOS_Analysis"
    return Path.home() / ".laos_analysis"


class SettingsManager:
    __doc__ = "\n    User settings manager for persistent application preferences\n\n    Handles:\n    - Window geometry (position, size, maximized state)\n    - Recent folders\n    - Plot settings (colormap, line width, etc.)\n    - Language and theme preferences\n    "
    DEFAULT_SETTINGS = {'window':{
      'width': 1400, 
      'height': 900, 
      'x': 100, 
      'y': 100, 
      'maximized': False}, 
     'recent_folders':[],  'max_recent_folders':10, 
     'plot':{
      'colormap': 'viridis',
      'colormap_2d': 'viridis', 
      'colormap_3d': 'jet', 
      'line_width': 5, 
      'marker_size': 50, 
      'marker_shape': 'o',
      'transparency': 0.8,
      'export_dpi': 300, 
      'export_format': 'png',
      'font_family': 'Times New Roman',
      'title_font_size': 14,
      'label_font_size': 12,
      'legend_font_size': 10,
      'annotation_font_size': 12,
      'legend_position': 'upper right'}, 
     'language':"auto", 
     'theme':"light", 
     'font_size':10, 
     'last_plot_type':"1", 
     'last_folder':""}

    def __init__(self, config_path: Optional[str]=None):
        """
        Initialize settings manager

        Args:
            config_path: Optional custom path for settings file.
                        Default: ~/LAOS_Analysis/settings.json (packaged) or ~/.laos_analysis/settings.json (source)
        """
        if config_path is None:
            self.config_path = get_user_data_dir() / "settings.json"
        else:
            self.config_path = Path(config_path)
        self.settings = self._load()

    def _load(self) -> Dict[(str, Any)]:
        """
        Load settings from file

        Returns:
            Dictionary with settings, merged with defaults
        """
        if self.config_path.exists():
            try:
                with open((self.config_path), "r", encoding="utf-8") as f:
                    saved = json.load(f)
                return self._merge_settings(self.DEFAULT_SETTINGS.copy(), saved)
            except (json.JSONDecodeError, IOError, KeyError) as e:
                try:
                    print(f"Warning: Failed to load settings: {e}")
                finally:
                    e = None
                    del e

        return self.DEFAULT_SETTINGS.copy()

    def _merge_settings(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries

        Args:
            base: Base dictionary (defaults)
            override: Override dictionary (saved settings)

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        else:
            return result

    def save(self):
        """Save current settings to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Warning: Failed to save settings: {e}")

    def add_recent_folder(self, folder_path: str) -> None:
        """
        Add a folder to recent folders list

        Args:
            folder_path: Path to add
        """
        recent = self.settings.get("recent_folders", [])
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        max_count = self.settings.get("max_recent_folders", 10)
        self.settings["recent_folders"] = recent[:max_count]
        self.save()

    def get_recent_folders(self) -> List[str]:
        """
        Get list of recent folders

        Returns:
            List of folder paths (most recent first)
        """
        return self.settings.get("recent_folders", [])

    def clear_recent_folders(self) -> None:
        """Clear recent folders list"""
        self.settings["recent_folders"] = []
        self.save()

    def get_window_geometry(self) -> Dict[(str, Any)]:
        """
        Get saved window geometry

        Returns:
            Dictionary with x, y, width, height, maximized
        """
        return self.settings.get("window", self.DEFAULT_SETTINGS["window"])

    def set_window_geometry(self, x, y, width, height, maximized=False):
        """
        Save window geometry

        Args:
            x: Window X position
            y: Window Y position
            width: Window width
            height: Window height
            maximized: Whether window is maximized
        """
        self.settings["window"] = {
         'x': x, 'y': y, 
         'width': width, 'height': height, 
         'maximized': maximized}
        self.save()

    def get_plot_setting(self, key: str, default: Any=None) -> Any:
        """
        Get a plot setting

        Args:
            key: Setting key (e.g., 'colormap_2d')
            default: Default value if not found

        Returns:
            Setting value
        """
        plot_settings = self.settings.get("plot", {})
        return plot_settings.get(key, default)

    def set_plot_setting(self, key: str, value: Any) -> None:
        """
        Set a plot setting

        Args:
            key: Setting key
            value: Setting value
        """
        if "plot" not in self.settings:
            self.settings["plot"] = {}
        self.settings["plot"][key] = value
        self.save()

    def get_plot_settings(self) -> Dict[(str, Any)]:
        """
        Get all plot settings

        Returns:
            Dictionary of plot settings
        """
        return self.settings.get("plot", self.DEFAULT_SETTINGS["plot"])

    def get_language(self) -> str:
        """Get current language setting"""
        return self.settings.get("language", "auto")

    def set_language(self, language: str) -> None:
        """
        Set language

        Args:
            language: Language code ('auto', 'en', 'zh')
        """
        self.settings["language"] = language
        self.save()

    def get_theme(self) -> str:
        """Get current theme"""
        return self.settings.get("theme", "light")

    def set_theme(self, theme: str) -> None:
        """
        Set theme

        Args:
            theme: Theme name ('light', 'dark')
        """
        self.settings["theme"] = theme
        self.save()

    def get_font_size(self) -> int:
        """Get current font size"""
        return self.settings.get("font_size", 10)

    def set_font_size(self, size: int) -> None:
        """
        Set font size

        Args:
            size: Font size in points (8, 10, 12, 14)
        """
        self.settings["font_size"] = size
        self.save()

    def get_last_folder(self) -> str:
        """Get last opened folder"""
        return self.settings.get("last_folder", "")

    def set_last_folder(self, folder: str) -> None:
        """Save last opened folder"""
        self.settings["last_folder"] = folder
        self.save()

    def get_last_plot_type(self) -> str:
        """Get last used plot type"""
        return self.settings.get("last_plot_type", "1")

    def set_last_plot_type(self, plot_type: str) -> None:
        """Save last used plot type"""
        self.settings["last_plot_type"] = plot_type
        self.save()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()

    def get_all(self) -> Dict[(str, Any)]:
        """Get all settings"""
        return self.settings.copy()

    def get_config_path(self) -> Path:
        """Get the path to the settings file"""
        return self.config_path


_settings_instance: Optional[SettingsManager] = None

def get_settings() -> SettingsManager:
    """
    Get the global SettingsManager instance

    Returns:
        SettingsManager singleton instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance