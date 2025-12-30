"""Form display component for rendering and submitting forms."""

import inspect
from typing import Awaitable, Callable, Optional, Union

from nicegui import ui

from ..core.fields import (
    BaseFormField,
    BooleanField,
    FloatField,
    IntegerField,
    TextField,
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
                    # Update field values from inputs
                    for field_name, input_elem in self._input_elements.items():
                        field = self.form.get_field(field_name)
                        if field and isinstance(field, BaseFormField):
                            value = input_elem.value
                            # Convert value based on field type
                            if isinstance(field, IntegerField):
                                try:
                                    value = int(value) if value is not None and str(value).strip() != "" else None
                                    field.set_value(value)
                                except (ValueError, TypeError):
                                    field.set_value(None)
                            elif isinstance(field, FloatField):
                                try:
                                    value = float(value) if value is not None and str(value).strip() != "" else None
                                    field.set_value(value)
                                except (ValueError, TypeError):
                                    field.set_value(None)
                            elif isinstance(field, BooleanField):
                                value = bool(value)
                                field.set_value(value)
                            else:  # TextField and others
                                field.set_value(value)

                    # Validate
                    if self.form.validate():
                        if self.on_submit:
                            if inspect.iscoroutinefunction(self.on_submit):
                                await self.on_submit()
                            else:
                                self.on_submit()
                            ui.notify(self._t.formSubmittedSuccessfully, type="positive")
                    else:
                        ui.notify(self._t.pleaseFixValidationErrors, type="negative")
                        self._show_validation_errors()

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

                ui.button(self._t.reset, on_click=reset_form, icon="refresh", color="warning")
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

    def _show_validation_errors(self) -> None:
        for field in self.form.fields:
            if isinstance(field, BaseFormField):
                value = field.get_value()
                if field.required and value is None:
                    ui.notify(self._t.fieldRequiredTemplate.format(field.label), type="warning")
                elif value is not None and not field.validate(value):
                    ui.notify(self._t.fieldInvalidValueTemplate.format(field.label), type="warning")
