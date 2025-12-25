"""Form editor component for creating and configuring forms."""

import copy
from typing import Callable, NamedTuple, Optional

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


class FieldTypeInfo(NamedTuple):
    """Information about a field type."""

    field_class: type
    icon: str


class FormEditor:
    """Component for editing form structure and configuration."""

    def __init__(self, form: Form, on_complete: Optional[Callable] = None, editor_locale: Optional[str] = None):
        """Initializes the form editor.

        Args:
            form: The form to edit.
            on_complete: Optional callback when editing is complete.
            editor_locale: The locale code (e.g., 'en', 'zh_cn'). If None, auto-detects from system.
        """
        self.form = form
        self.on_complete = on_complete
        self._t = I18nHelper(editor_locale).translations
        self._field_types = {
            self._t.text: FieldTypeInfo(TextField, "text_fields"),
            self._t.integer: FieldTypeInfo(IntegerField, "123"),
            self._t.float: FieldTypeInfo(FloatField, "numbers"),
            self._t.boolean: FieldTypeInfo(BooleanField, "check_box"),
        }

    def set_on_complete(self, callback: Callable) -> None:
        """Sets the callback for when editing is complete.

        Args:
            callback: The callback function to set.
        """
        self.on_complete = callback

    def render(self) -> None:
        """Renders the form editor component in the NiceGUI application."""
        with ui.card().classes("w-full max-w-4xl mx-auto"):
            ui.label(self._t.formEditor).classes("text-2xl font-bold mb-4")

            # Form metadata editor
            with ui.card().classes("w-full mb-4"):
                ui.label(self._t.formInformation).classes("text-lg font-semibold mb-2")

                title_input = ui.input(
                    self._t.formTitle,
                    value=self.form.title,
                    on_change=lambda e: setattr(self.form, "title", e.value),
                ).classes("w-full")

                desc_input = ui.textarea(
                    self._t.formDescription,
                    value=self.form.description or "",
                    on_change=lambda e: setattr(self.form, "description", e.value or None),
                ).classes("w-full")

                # Locale selector
                available_locales = I18nHelper.get_available_locales()
                locale_options = {loc.native_name: loc.code for loc in available_locales}

                # Find current locale display name
                current_locale_label = None
                for loc in available_locales:
                    if loc.code == self.form.locale:
                        current_locale_label = loc.native_name
                        break
                if current_locale_label is None:
                    # Default to first locale (English)
                    current_locale_label = available_locales[0].native_name if available_locales else "English"

                ui.select(
                    options=list(locale_options.keys()),
                    value=current_locale_label,
                    label=self._t.formLocale,
                    on_change=lambda e: setattr(self.form, "locale", locale_options.get(e.value)),
                ).classes("w-full")

                ui.label(f"{self._t.uuid}: {self.form.uuid}").classes("text-sm text-gray-500")

            # Fields editor
            with ui.card().classes("w-full mb-4"):
                ui.label(self._t.formFields).classes("text-lg font-semibold mb-2")

                fields_container = ui.column().classes("w-full gap-2")

                def refresh_fields():
                    """Refreshes the fields display."""
                    fields_container.clear()
                    with fields_container:
                        for idx, field in enumerate(self.form.fields):
                            if isinstance(field, BaseFormField):
                                self._render_field_editor(field, idx, refresh_fields)

                refresh_fields()

                # Add field controls
                with ui.row().classes("gap-2"):
                    field_type_select = ui.select(
                        options=list(self._field_types.keys()),
                        value=list(self._field_types.keys())[0],
                        label=self._t.fieldType,
                    ).classes("w-64")

                    def add_field():
                        """Adds a new field to the form."""
                        field_type = field_type_select.value
                        assert isinstance(field_type, str)
                        field_info = self._field_types[field_type]
                        field_class = field_info.field_class
                        new_field_name = f"field_{len(self.form.fields)}"
                        # Get the original field type name for the template
                        original_type = None
                        for k, v in self._field_types.items():
                            if v.field_class == field_class:
                                original_type = k
                                break
                        new_field = field_class(
                            name=new_field_name, label=self._t.newFieldTemplate.format(original_type)
                        )
                        self.form.add_field(new_field)
                        refresh_fields()

                    ui.button(self._t.addField, on_click=add_field, icon="add")

            # Action buttons
            with ui.row().classes("w-full gap-2 justify-between mt-4"):
                with ui.row().classes("gap-2"):

                    def export_schema():
                        """Exports the form schema."""
                        schema = self.form.dump_schema()
                        ui.clipboard.write(str(schema))
                        ui.notify(self._t.jsonSchemaCopied)

                    def export_schema_b64():
                        """Exports the form schema as base64."""
                        schema_b64 = self.form.dump_schema_b64(compression_flag=1)
                        ui.clipboard.write(schema_b64)
                        ui.notify(self._t.base64SchemaCopied)

                    ui.button(self._t.exportJson, on_click=export_schema, icon="data_object", color="secondary")
                    ui.button(self._t.exportBase64, on_click=export_schema_b64, icon="code", color="secondary")

                if self.on_complete:
                    ui.button(self._t.complete, on_click=self.on_complete, icon="check")

    def _move_field(self, index: int, direction: int, refresh_callback: Callable) -> None:
        new_index = index + direction
        if 0 <= new_index < len(self.form.fields):
            self.form.fields[index], self.form.fields[new_index] = (
                self.form.fields[new_index],
                self.form.fields[index],
            )
            refresh_callback()

    def _delete_field(self, field_name: str, refresh_callback: Callable) -> None:
        self.form.remove_field(field_name)
        refresh_callback()

    def _duplicate_field(self, index: int, refresh_callback: Callable) -> None:
        original_field = self.form.fields[index]
        new_field = copy.deepcopy(original_field)

        # Ensure unique name
        base_name = original_field.name
        counter = 1
        new_name = f"{base_name}_copy"
        while self.form.get_field(new_name):
            new_name = f"{base_name}_copy_{counter}"
            counter += 1
        new_field.name = new_name

        self.form.fields.insert(index + 1, new_field)
        refresh_callback()

    def _render_field_editor(self, field: BaseFormField, index: int, refresh_callback: Callable) -> None:
        # Get the icon for this field type
        field_icon = "edit"
        for type_name, type_info in self._field_types.items():
            if isinstance(field, type_info.field_class):
                field_icon = type_info.icon
                break

        with ui.expansion(group="fields").classes("w-full") as expansion:
            with expansion.add_slot("header"):
                with ui.row().classes("w-full items-center gap-2"):
                    ui.icon(field_icon).classes("text-xl")

                    # Name and Label (reactive)
                    with ui.row().classes("items-baseline gap-0 flex-grow"):
                        ui.label().bind_text_from(field, "name").classes("font-medium")
                        ui.label("*").classes("text-red font-bold text-sm ml-1").bind_visibility_from(field, "required")
                        ui.label().bind_text_from(
                            field, "label", backward=lambda v: f"{v[:18]}..." if len(v) > 20 else v
                        ).classes("text-gray-500 text-sm ml-2")

                    # Sort buttons
                    with ui.row().classes("gap-0 items-center mr-1"):
                        up_btn = ui.button(
                            icon="arrow_upward", on_click=lambda: self._move_field(index, -1, refresh_callback)
                        ).props("flat dense color=grey")
                        if index == 0:
                            up_btn.disable()

                        down_btn = ui.button(
                            icon="arrow_downward", on_click=lambda: self._move_field(index, 1, refresh_callback)
                        ).props("flat dense color=grey")
                        if index == len(self.form.fields) - 1:
                            down_btn.disable()

                        # Duplicate button
                        ui.button(
                            icon="content_copy", on_click=lambda: self._duplicate_field(index, refresh_callback)
                        ).props("flat dense color=grey")

                        # Delete button
                        ui.button(
                            icon="delete", on_click=lambda: self._delete_field(field.name, refresh_callback)
                        ).props("flat dense color=red")

            with ui.column().classes("w-full gap-2 p-2"):
                with ui.row().classes("w-full items-center gap-4"):
                    ui.input(
                        self._t.fieldName, value=field.name, on_change=lambda e, f=field: setattr(f, "name", e.value)
                    ).classes("flex-grow")

                    ui.checkbox(
                        self._t.required,
                        value=field.required,
                        on_change=lambda e, f=field: setattr(f, "required", e.value),
                    ).classes("mt-4")

                ui.input(
                    self._t.label, value=field.label, on_change=lambda e, f=field: setattr(f, "label", e.value)
                ).classes("w-full")

                ui.input(
                    self._t.description,
                    value=field.description or "",
                    on_change=lambda e, f=field: setattr(f, "description", e.value or None),
                ).classes("w-full")

                # Type-specific fields
                if isinstance(field, TextField):
                    # Min and Max length in the same row
                    with ui.row().classes("w-full gap-2"):
                        ui.number(
                            self._t.minLength,
                            value=field.min_length,
                            on_change=lambda e, f=field: setattr(f, "min_length", int(e.value) if e.value else None),
                        ).classes("flex-1")

                        ui.number(
                            self._t.maxLength,
                            value=field.max_length,
                            on_change=lambda e, f=field: setattr(f, "max_length", int(e.value) if e.value else None),
                        ).classes("flex-1")

                    ui.input(
                        self._t.regexPattern,
                        value=field.regex or "",
                        on_change=lambda e, f=field: setattr(f, "regex", e.value or None),
                    ).classes("w-full")

                elif isinstance(field, (IntegerField, FloatField)):
                    # Min and Max value in the same row
                    with ui.row().classes("w-full gap-2"):
                        ui.number(
                            self._t.minValue,
                            value=field.min_value,
                            on_change=lambda e, f=field: setattr(f, "min_value", e.value),
                        ).classes("flex-1")

                        ui.number(
                            self._t.maxValue,
                            value=field.max_value,
                            on_change=lambda e, f=field: setattr(f, "max_value", e.value),
                        ).classes("flex-1")
