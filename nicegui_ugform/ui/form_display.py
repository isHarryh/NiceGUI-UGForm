"""Form display component for rendering and submitting forms."""

import inspect
from typing import Any, Awaitable, Callable, Optional, Tuple, Union

from nicegui import ui

from ..core.fields import (
    BaseFormField,
    BooleanField,
    FloatField,
    IntegerField,
    TextField,
    ValidationResultType,
)
from ..core.form import Form
from ..i18n.helper import I18nHelper


class FormDisplay:
    """Component for displaying and submitting forms."""

    def __init__(
        self,
        form: Form,
        on_submit: Optional[Union[Callable[[], None], Callable[[], Awaitable[None]]]] = None,
        locale: Optional[str] = None,
    ):
        """Initializes the form display.

        Args:
            form: The form to display.
            on_submit: Optional callback (sync or async) when form is submitted.
            locale: The locale code (e.g., 'en', 'zh_cn'). If None, uses form.locale or auto-detects from system.
        """
        self.form = form
        self.on_submit = on_submit
        self._input_elements = {}
        # Use provided locale, or fall back to form's locale, or auto-detect
        display_locale = locale or form.locale
        self._t = I18nHelper(display_locale).translations

    def set_on_submit(self, callback: Union[Callable[[], None], Callable[[], Awaitable[None]]]) -> None:
        """Sets the callback for when the form is submitted.

        Args:
            callback: The callback function (sync or async) to set.
        """
        self.on_submit = callback

    def render(self) -> None:
        """Renders the form display component in the NiceGUI application."""
        with ui.card().classes("w-full max-w-2xl mx-auto"):
            # Form header
            ui.label(self.form.title).classes("text-2xl font-bold mb-2")
            if self.form.description:
                ui.label(self.form.description).classes("text-gray-600 mb-4")

            # Form fields
            with ui.column().classes("w-full gap-4 mt-4"):
                for field in self.form.fields:
                    if isinstance(field, BaseFormField):
                        self._render_field(field)

            # Buttons
            with ui.row().classes("w-full justify-end gap-2 mt-6"):

                async def submit_form():
                    """Submits the form after validation."""
                    # Trigger validation for all input fields and collect normalized values
                    has_errors = False
                    pending_values = {}
                    for field_name, input_elem in self._input_elements.items():
                        field = self.form.get_field(field_name)
                        if not field or not isinstance(field, BaseFormField):
                            continue

                        # Normalize once so we reuse for assignment after validation
                        normalized_ok, normalized_value = self._normalize_input(field, input_elem.value)
                        pending_values[field_name] = normalized_value

                        if hasattr(input_elem, "validate"):
                            result = input_elem.validate()
                            if result is False:
                                has_errors = True

                        # If normalization already failed, mark error
                        if not normalized_ok:
                            has_errors = True

                    if has_errors:
                        ui.notify(self._t.pleaseFixValidationErrors, type="negative")
                        return

                    # Update field values from normalized inputs
                    for field_name, value in pending_values.items():
                        field = self.form.get_field(field_name)
                        if field and isinstance(field, BaseFormField):
                            field.set_value(value)

                    # Call submit callback
                    if self.on_submit:
                        if inspect.iscoroutinefunction(self.on_submit):
                            await self.on_submit()
                        else:
                            self.on_submit()
                    ui.notify(self._t.formSubmittedSuccessfully, type="positive")

                def reset_form():
                    """Resets the form to default values."""
                    for field in self.form.fields:
                        if isinstance(field, BaseFormField):
                            field.set_value(field.default_value)

                    # Update UI
                    for field_name, input_elem in self._input_elements.items():
                        field = self.form.get_field(field_name)
                        if field and isinstance(field, BaseFormField):
                            if isinstance(input_elem, ui.checkbox):
                                input_elem.value = field.default_value or False
                            else:
                                input_elem.value = field.default_value

                    ui.notify(self._t.formReset, type="info")

                if self.form.show_reset_button:
                    ui.button(self._t.reset, on_click=reset_form, icon="refresh", color="warning")
                if self.form.show_submit_button:
                    ui.button(self._t.submit, on_click=submit_form, icon="send", color="primary")

    def _render_field(self, field: BaseFormField) -> None:
        label_text = field.label
        if field.required:
            label_text += " *"

        if isinstance(field, TextField):
            input_elem = ui.input(
                label=label_text,
                placeholder=field.description or "",
                value=field.get_value() or field.default_value or "",
                validation=lambda value, f=field: self._validate_internal(f, value),
            ).classes("w-full")

            if field.max_length:
                input_elem.props(f"maxlength={field.max_length}")

            self._input_elements[field.name] = input_elem

        elif isinstance(field, IntegerField):
            input_elem = ui.number(
                label=label_text,
                placeholder=field.description or "",
                value=field.get_value() or field.default_value,
                format="%.0f",
                validation=lambda value, f=field: self._validate_internal(f, value),
            ).classes("w-full")

            if field.min_value is not None:
                input_elem.props(f"min={field.min_value}")
            if field.max_value is not None:
                input_elem.props(f"max={field.max_value}")

            self._input_elements[field.name] = input_elem

        elif isinstance(field, FloatField):
            input_elem = ui.number(
                label=label_text,
                placeholder=field.description or "",
                value=field.get_value() or field.default_value,
                format="%.2f",
                validation=lambda value, f=field: self._validate_internal(f, value),
            ).classes("w-full")

            if field.min_value is not None:
                input_elem.props(f"min={field.min_value}")
            if field.max_value is not None:
                input_elem.props(f"max={field.max_value}")

            self._input_elements[field.name] = input_elem

        elif isinstance(field, BooleanField):
            input_elem = ui.checkbox(text=label_text, value=field.get_value() or field.default_value or False)

            if field.description:
                ui.label(field.description).classes("text-sm text-gray-500 -mt-4 mb-2 ml-2")

            self._input_elements[field.name] = input_elem

    def _validate_internal(self, field: BaseFormField, raw_value: Any) -> Optional[str]:
        normalized_ok, normalized_value = self._normalize_input(field, raw_value)
        if not normalized_ok:
            return self._t.invalidTypeTemplate.format(field.label)

        result = field.validate(normalized_value)
        return self._convert_validation_message(result, field)

    def _normalize_input(self, field: BaseFormField, raw_value: Any) -> Tuple[bool, Any]:
        if isinstance(field, IntegerField):
            if raw_value is None or str(raw_value).strip() == "":
                return True, None
            try:
                return True, int(raw_value)
            except (ValueError, TypeError):
                return False, None

        if isinstance(field, FloatField):
            if raw_value is None or str(raw_value).strip() == "":
                return True, None
            try:
                return True, float(raw_value)
            except (ValueError, TypeError):
                return False, None

        if isinstance(field, BooleanField):
            if raw_value is None:
                return True, None
            return True, bool(raw_value)

        # Text and other fields: keep as-is
        return True, raw_value

    def _convert_validation_message(
        self, result: ValidationResultType, field: Optional[BaseFormField] = None
    ) -> Optional[str]:
        if result == ValidationResultType.okay:
            return None

        if result == ValidationResultType.invalid_type:
            return self._t.invalidTypeTemplate.format(field.label if field else "")

        if result == ValidationResultType.required_missing:
            return self._t.requiredField

        if result == ValidationResultType.too_short and isinstance(field, TextField):
            if field.min_length is not None:
                return self._t.tooShortTemplate.format(field.min_length)

        if result == ValidationResultType.to_long and isinstance(field, TextField):
            if field.max_length is not None:
                return self._t.tooLongTemplate.format(field.max_length)

        if result == ValidationResultType.regex_mismatch:
            return self._t.regexPatternMismatch

        if result == ValidationResultType.too_small and isinstance(field, (IntegerField, FloatField)):
            min_val = getattr(field, "min_value", None)
            if min_val is not None:
                return self._t.tooSmallTemplate.format(min_val)

        if result == ValidationResultType.too_large and isinstance(field, (IntegerField, FloatField)):
            max_val = getattr(field, "max_value", None)
            if max_val is not None:
                return self._t.tooLargeTemplate.format(max_val)

        # Fallback
        return self._t.invalidValueTemplate.format(field.label if field else "")
