"""Test script demonstrating the form editor and form display components."""

import asyncio
from nicegui import ui

from nicegui_ugform import BooleanField, FloatField, Form, FormDisplay, FormEditor, IntegerField, TextField, __version__


def main():
    """Runs the test application."""

    # Create a sample form
    form = Form(title="Sample Registration Form", description="Please fill out this registration form", locale="en")

    # Add fields to the form
    form.add_field(
        TextField(
            name="username",
            label="Username",
            description="Enter your username",
            required=True,
            min_length=3,
            max_length=20,
        )
    )

    form.add_field(
        TextField(
            name="email",
            label="Email",
            description="Enter your email address",
            required=True,
            regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        )
    )

    form.add_field(
        IntegerField(
            name="age",
            label="Age",
            description="Enter your age",
            required=True,
            min_value=18,
            max_value=120,
        )
    )

    form.add_field(
        FloatField(
            name="height",
            label="Height (meters)",
            description="Enter your height in meters",
            required=False,
            min_value=0.5,
            max_value=3.0,
        )
    )

    form.add_field(
        BooleanField(
            name="subscribe",
            label="Subscribe to newsletter",
            description="Check to receive our newsletter",
            required=False,
            default_value=False,
        )
    )

    # Create the pages
    def menu():
        """Navigation menu with title and version."""
        with ui.column().classes("w-full items-center gap-2 mb-4"):
            with ui.row().classes("w-full justify-center items-baseline gap-2"):
                ui.label("NiceGUI-UGForm Demo").classes("text-3xl font-bold")
                ui.label(__version__).classes("text-sm text-gray-500")
            with ui.row().classes("w-full justify-center gap-8 p-4 bg-gray-100 rounded"):
                ui.link("Editor", "/editor").classes("text-lg font-bold")
                ui.link("Display", "/display").classes("text-lg font-bold")
                ui.link("Schema", "/schema").classes("text-lg font-bold")

    @ui.page("/")
    @ui.page("/index")
    def index():
        """Redirect to editor."""
        ui.navigate.to("/editor")

    @ui.page("/editor")
    def editor_page():
        """Form editor page."""

        async def on_complete():
            ui.notify("Processing...", type="info")
            await asyncio.sleep(1)
            ui.notify("Form editing completed!", type="positive")

        menu()
        editor = FormEditor(form, editor_locale="en")
        editor.set_on_complete(on_complete)
        editor.render()

    @ui.page("/display")
    def display_page():
        """Form display page."""
        menu()

        with ui.column().classes("w-full gap-4"):

            async def on_submit():
                data = form.dump_data()
                globals()["last_submission_data"] = data
                print("Form submitted:", data)
                result_editor.properties["content"]["json"].update(data)
                ui.notify("Submitting...", type="info")
                await asyncio.sleep(1)
                ui.notify("Submitted!", type="positive")

            display = FormDisplay(form, on_submit=on_submit)
            display.render()

            # Result display (initially hidden)
            with (
                ui.card()
                .classes("w-full max-w-2xl mx-auto mb-4")
                .bind_visibility_from(globals(), "last_submission_data", backward=lambda x: x is not None)
            ):
                ui.label("Submission Result").classes("text-xl font-bold mb-2")
                result_editor = ui.json_editor({"content": {"json": {}}}).classes("w-full")

    # Initialize global state for submission data
    globals()["last_submission_data"] = None

    @ui.page("/schema")
    def schema_page():
        """Schema view page."""
        menu()
        with ui.card().classes("w-full max-w-4xl mx-auto"):
            # JSON Schema
            with ui.expansion("JSON Schema", icon="data_object").classes("w-full"):
                schema = form.dump_schema()
                ui.json_editor({"content": {"json": schema}}).classes("w-full")

            # Base64 Schema
            with ui.expansion("Base64 Compressed Schema", icon="compress").classes("w-full"):
                schema_b64 = form.dump_schema_b64(compression_flag=1)
                ui.textarea(value=schema_b64).classes("w-full").props("readonly")

                def copy_b64():
                    ui.clipboard.write(schema_b64)
                    ui.notify("Copied to clipboard!")

                ui.button("Copy to Clipboard", on_click=copy_b64, icon="content_copy")

            # Load from Base64
            with ui.expansion("Load from Base64", icon="download").classes("w-full"):
                b64_input = ui.textarea(
                    label="Paste Base64 Schema", placeholder="Paste a base64 encoded schema here"
                ).classes("w-full")

                def load_b64():
                    try:
                        loaded_form = Form.load_schema_b64(b64_input.value)
                        ui.notify(f"Loaded form: {loaded_form.title}", type="positive")
                        print("Loaded form schema:", loaded_form.dump_schema())
                    except Exception as e:
                        ui.notify(f"Error loading schema: {str(e)}", type="negative")

                ui.button("Load Schema", on_click=load_b64, icon="download")

    # Run the application
    ui.run(title="NiceGUI-UGForm Demo", port=8000, reload=True)


if __name__ in {"__main__", "__mp_main__"}:
    main()
