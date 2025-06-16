"""
Translation Manager for Free AugmentCode.

This module provides internationalization support for the application,
allowing users to switch between Chinese and English languages.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class TranslationManager:
    """
    Manages translations and language switching for the application.
    """

    def __init__(self):
        """Initialize the translation manager."""
        self.current_language = "zh_CN"  # Default to Chinese
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.translations_dir = self._get_translations_dir()
        self.config_file = self._get_config_file()
        
        # Load saved language preference
        self._load_language_preference()
        
        # Load all available translations
        self._load_translations()

    def _get_translations_dir(self) -> Path:
        """Get the translations directory path."""
        current_dir = Path(__file__).parent.parent
        return current_dir / "translations"

    def _get_config_file(self) -> Path:
        """Get the language config file path."""
        try:
            # Use user's home directory for config
            home_dir = Path.home()
            config_dir = home_dir / ".augment_free"
            config_dir.mkdir(exist_ok=True)
            return config_dir / "language.json"
        except Exception:
            # Fallback to current directory
            return Path(".") / "language.json"

    def _load_language_preference(self) -> None:
        """Load the saved language preference."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.current_language = config.get("language", "zh_CN")
        except Exception:
            # Use default language if loading fails
            self.current_language = "zh_CN"

    def _save_language_preference(self) -> None:
        """Save the current language preference."""
        try:
            config = {"language": self.current_language}
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            # Silently fail if saving is not possible
            pass

    def _load_translations(self) -> None:
        """Load all available translation files."""
        if not self.translations_dir.exists():
            return

        for file_path in self.translations_dir.glob("*.json"):
            try:
                lang_code = file_path.stem
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load translation file {file_path}: {e}")

    def get_available_languages(self) -> Dict[str, str]:
        """
        Get available languages.
        
        Returns:
            dict: Language codes mapped to display names
        """
        return {
            "zh_CN": "中文",
            "en_US": "English"
        }

    def get_current_language(self) -> str:
        """
        Get the current language code.
        
        Returns:
            str: Current language code
        """
        return self.current_language

    def set_language(self, lang_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            lang_code (str): Language code (e.g., "zh_CN", "en_US")
            
        Returns:
            bool: True if language was set successfully
        """
        available_languages = self.get_available_languages()
        if lang_code not in available_languages:
            return False
            
        self.current_language = lang_code
        self._save_language_preference()
        return True

    def get_translation(self, key: str, lang_code: Optional[str] = None) -> str:
        """
        Get a translation for a specific key.
        
        Args:
            key (str): Translation key (supports dot notation, e.g., "ui.header.title")
            lang_code (str, optional): Language code. Uses current language if not specified.
            
        Returns:
            str: Translated text or the key itself if translation not found
        """
        if lang_code is None:
            lang_code = self.current_language
            
        if lang_code not in self.translations:
            return key
            
        # Support dot notation for nested keys
        translation_data = self.translations[lang_code]
        keys = key.split(".")
        
        try:
            for k in keys:
                translation_data = translation_data[k]
            return str(translation_data)
        except (KeyError, TypeError):
            return key

    def get_all_translations(self, lang_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all translations for a language.
        
        Args:
            lang_code (str, optional): Language code. Uses current language if not specified.
            
        Returns:
            dict: All translations for the specified language
        """
        if lang_code is None:
            lang_code = self.current_language
            
        return self.translations.get(lang_code, {})

    def translate_dict(self, data: Dict[str, Any], lang_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate a dictionary containing translation keys.
        
        Args:
            data (dict): Dictionary with translation keys as values
            lang_code (str, optional): Language code. Uses current language if not specified.
            
        Returns:
            dict: Dictionary with translated values
        """
        if not isinstance(data, dict):
            return data
            
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("t:"):
                # Translation key format: "t:ui.header.title"
                translation_key = value[2:]  # Remove "t:" prefix
                result[key] = self.get_translation(translation_key, lang_code)
            elif isinstance(value, dict):
                result[key] = self.translate_dict(value, lang_code)
            elif isinstance(value, list):
                result[key] = [
                    self.translate_dict(item, lang_code) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
                
        return result


# Global translation manager instance
_translation_manager = None


def get_translation_manager() -> TranslationManager:
    """
    Get the global translation manager instance.
    
    Returns:
        TranslationManager: Global translation manager
    """
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def t(key: str, lang_code: Optional[str] = None) -> str:
    """
    Shorthand function for getting translations.
    
    Args:
        key (str): Translation key
        lang_code (str, optional): Language code
        
    Returns:
        str: Translated text
    """
    return get_translation_manager().get_translation(key, lang_code)
