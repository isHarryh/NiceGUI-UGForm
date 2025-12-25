"""Internationalization helper for NiceGUI-UGForm."""

import locale
from typing import NamedTuple, Optional

from . import locale_en, locale_zh_cn
from .keys import TranslationMap


class LocaleInfo(NamedTuple):
    code: str
    name: str
    native_name: str
    translations: TranslationMap


class I18nHelper:
    """Helper class for internationalization support."""

    _LOCALES = [
        LocaleInfo(
            code="en",
            name="English",
            native_name="English",
            translations=locale_en.TRANSLATIONS,
        ),
        LocaleInfo(
            code="zh_cn",
            name="Chinese (Simplified)",
            native_name="简体中文",
            translations=locale_zh_cn.TRANSLATIONS,
        ),
    ]

    def __init__(self, locale_code: Optional[str] = None):
        """Initializes the I18n helper.

        Args:
            locale_code: The locale code (e.g., 'en', 'zh_cn'). If None, auto-detects from system.
        """
        if locale_code is None:
            locale_code = self._detect_locale()

        self.locale = locale_code
        # Find the locale info from the list
        locale_info = next((loc for loc in self._LOCALES if loc.code == locale_code), None)
        self.translations: TranslationMap = locale_info.translations if locale_info else locale_en.TRANSLATIONS

    def _detect_locale(self) -> str:
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Convert 'zh_CN' to our supported format
                if system_locale.startswith("zh"):
                    return "zh_cn"
                elif system_locale.startswith("en"):
                    return "en"
        except Exception:
            pass

        # Default to English
        return "en"

    @classmethod
    def get_available_locales(cls) -> list[LocaleInfo]:
        """Gets all available locales.

        Returns:
            List of available LocaleInfo objects.
        """
        return cls._LOCALES
