"""Tests for internationalization."""

import pytest
from nicegui_ugform.i18n.helper import I18nHelper, LocaleInfo
from nicegui_ugform.i18n.keys import TranslationMap


class TestI18nHelper:
    """Tests for I18nHelper."""

    def test_creation_with_locale(self):
        helper = I18nHelper(locale_code="en")
        assert helper.locale == "en"
        assert isinstance(helper.translations, TranslationMap)

    def test_auto_detect_locale(self):
        locale_keys = [loc.code for loc in I18nHelper.get_available_locales()]
        helper = I18nHelper()
        assert len(locale_keys) > 0
        assert all(isinstance(loc, LocaleInfo) for loc in I18nHelper.get_available_locales())
        assert helper.locale in locale_keys

    def test_fallback_to_english(self):
        helper = I18nHelper(locale_code="unknown_locale")
        assert helper.translations is I18nHelper(locale_code="en").translations
