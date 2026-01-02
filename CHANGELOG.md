# Changelog

All notable changes to NiceGUI-UGForm will be documented in this file.

## v1.1.0 - 2026-01-02

### Added
- Support for asynchronous callbacks in `FormEditor` (`on_complete`) and `FormDisplay` (`on_submit`).
- Add `ValidationResultType` enum for fields for granular validation feedback.
- Add configuration options `show_reset_button` and `show_submit_button` in form schema.

### Changed
- Refactor `BaseFormField` validation logic to use `validate_with_result` for detailed error reporting.
- Improve validation error display by utilizing NiceGUI's native `validation` property to show errors directly on input fields.
- Improve input normalization and type conversion for `IntegerField` and `FloatField`.
- Update `Form` serialization to include button visibility settings.

### Removed
- Remove redundant "Form submitted successfully" notification.

## v1.0.1 - 2025-12-36

### Added
- Add comprehensive tests for core functionalities.

### Changed
- Update type hints for `BaseFormField.validate`.
- Update `locale.getlocale` invocation.

## v1.0.0 - 2025-12-25

### Added
- Add core field types: `TextField`, `IntegerField`, `FloatField`, `BooleanField`.
- Add core class`Form` class with JSON and binary serialization support.
- Add `FormEditor` UI component for interactive form building.
- Add `FormDisplay` UI component for rendering forms.
- Support internationalization with English and Simplified Chinese locales.
