# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.8 (default, Apr 13 2021, 15:08:03) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: utils\i18n.py
"""
Internationalization (i18n) support for LAOS Analysis GUI
Provides translation loading and management
"""
import os, sys
import xml.etree.ElementTree as ET
from typing import Optional, Dict
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo, QCoreApplication

def get_application_path():
    """Get application base path (works for both source and packaged exe)"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TSTranslator:
    __doc__ = "\n    Translator that loads translations from Qt .ts (XML) files\n    "

    def __init__(self):
        self._translations = {}

    def load_from_ts(self, ts_file):
        """
        Load translations from a .ts file

        Args:
            ts_file: Path to the .ts file

        Returns:
            bool: True if loaded successfully
        """
        try:
            print(f"[DEBUG] Loading translation file: {ts_file}")
            print(f"[DEBUG] File exists: {os.path.exists(ts_file)}")
            tree = ET.parse(ts_file)
            root = tree.getroot()

            translation_count = 0
            for context in root.findall('context'):
                context_name = context.find('name')
                if context_name is None:
                    continue
                context_name = context_name.text
                self._translations[context_name] = {}

                for message in context.findall('message'):
                    source = message.find('source')
                    translation = message.find('translation')

                    if source is not None and translation is not None:
                        source_text = source.text or ''
                        trans_text = translation.text or source_text
                        self._translations[context_name][source_text] = trans_text
                        translation_count += 1

            print(f"[DEBUG] Loaded {translation_count} translations from {ts_file}")
            print(f"[DEBUG] Contexts: {list(self._translations.keys())}")
            return True
        except Exception as e:
            print(f"Error loading TS file: {e}")
            import traceback
            traceback.print_exc()
            return False



    def translate(self, context: str, text: str) -> str:
        """
        Translate text in given context

        Args:
            context: Translation context
            text: Text to translate

        Returns:
            Translated text or original if not found
        """
        if context in self._translations:
            return self._translations[context].get(text, text)
        return text


class Translator:
    __doc__ = "\n    Translation manager for ChemicalStrain GUI\n    Handles loading and switching between languages\n    "
    LANGUAGES = {'en':"English", 
     'zh_CN':"简体中文", 
     'ja':"日本語"}
    DEFAULT_LANGUAGE = "zh_CN"

    def __init__(self):
        self._ts_translator = None
        self._qt_translator = None
        self._current_language = "en"
        self._translations_dir = self._get_translations_dir()

    def _get_translations_dir(self) -> str:
        """Get translations directory path"""
        return os.path.join(get_application_path(), "translations")

    def get_current_language(self) -> str:
        """Get current language code"""
        return self._current_language

    def get_language_name(self, lang_code: str) -> str:
        """Get display name for language code"""
        return self.LANGUAGES.get(lang_code, lang_code)

    def get_available_languages(self) -> list:
        """Get list of available language codes"""
        return list(self.LANGUAGES.keys())

    def detect_system_language(self) -> str:
        """Detect system language and return matching language code"""
        system_locale = QLocale.system().name()
        if system_locale in self.LANGUAGES:
            return system_locale
        lang = system_locale.split("_")[0]
        for code in self.LANGUAGES:
            if code.startswith(lang):
                return code
        return "en"

    def load_language(self, lang_code: str) -> bool:
        """
        Load translation for specified language

        Args:
            lang_code: Language code (e.g., 'zh_CN', 'en', 'auto')

        Returns:
            bool: True if translation loaded successfully
        """
        if lang_code == "auto":
            lang_code = self.detect_system_language()
        elif lang_code not in self.LANGUAGES:
            print(f"Warning: Unsupported language '{lang_code}'")
            return False
        
        # Remove old translators
        if self._qt_translator:
            QCoreApplication.removeTranslator(self._qt_translator)
            self._qt_translator = None
        self._ts_translator = None
        
        # English doesn't need translation files
        if lang_code == "en":
            self._current_language = "en"
            return True
        
        # Load Qt base translations
        self._qt_translator = QTranslator()
        qt_trans_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        if self._qt_translator.load(QLocale(lang_code), "qtbase", "_", qt_trans_path):
            QCoreApplication.installTranslator(self._qt_translator)
        
        # Load application translations
        ts_file = os.path.join(self._translations_dir, f"{lang_code}.ts")
        if os.path.exists(ts_file):
            self._ts_translator = TSTranslator()
            if self._ts_translator.load_from_ts(ts_file):
                self._current_language = lang_code
                print(f"Loaded translation: {lang_code}")
                return True
            else:
                print(f"Warning: Failed to load translation file: {ts_file}")
        else:
            print(f"Warning: Translation file not found: {ts_file}")
        
        self._current_language = lang_code
        return False

    def load_default_language(self) -> bool:
        """Load default or detected system language"""
        return self.load_language("auto")

    def translate(self, context: str, text: str) -> str:
        """
        Translate text in given context

        Args:
            context: Translation context
            text: Text to translate

        Returns:
            Translated text or original if not found
        """
        if self._ts_translator:
            result = self._ts_translator.translate(context, text)
            # Debug: only print for specific context to avoid too much output
            if context == "LAOSAnalysis" and result != text:
                pass  # Translation successful, no debug output needed
            return result
        return text


_translator: Optional[Translator] = None

def get_translator() -> Translator:
    """Get global translator instance"""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


def tr(text: str, context: str='LAOSAnalysis') -> str:
    """
    Translate text using global translator

    Args:
        text: Text to translate
        context: Translation context

    Returns:
        Translated text (or original if no translation available)
    """
    translator = get_translator()
    return translator.translate(context, text)


def init_translator(lang_code: str='auto') -> Translator:
    """Initialize and return global translator

    Args:
        lang_code: Language code to load ('auto', 'en', 'zh_CN')
                   If 'auto', detects system language
    """
    translator = get_translator()
    translator.load_language(lang_code)
    return translator