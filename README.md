NiceGUI-UGForm
==========
Form Builder Component for NiceGUI Framework  
适用于 NiceGUI 框架的表单构建器组件

![PyPI - Version](https://img.shields.io/pypi/v/nicegui_ugform?label=PyPI%20version)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nicegui_ugform?label=PyPI%20downloads)

## Introduction

This Python library provides a flexible **form builder** for the NiceGUI framework. It allows the user to create a **user-generated form (UGForm)** via [NiceGUI](https://nicegui.io/), easily serialize/deserialize form schemas and display them.

### Features

- **Easy Serialization**: Export/import form schemas as JSON or compressed Base64 strings.
- **Interactive UI**: Built-in form editor and display components for NiceGUI.
- **Built-in I18N**: Supports multiple languages (currently English and Chinese).
- **Well-Designed**: Follows best practices such as type annotations.

Currently supported field types:

|  Field Type  | Validation Approaches         |
| :----------: | :---------------------------- |
|  TextField   | min/max length, regex pattern |
| IntegerField | min/max value                 |
|  FloatField  | min/max value                 |
| BooleanField | -                             |

### Demo

See [demo.py](demo.py) for a complete example about what can it do.

|                  Form Editor                   |                   Form Display                   |
| :--------------------------------------------: | :----------------------------------------------: |
| ![Form Editor Demo](docs/imgs/demo_editor.png) | ![Form Display Demo](docs/imgs/demo_display.png) |

### Changelog

See [CHANGELOG.md](CHANGELOG.md) to understand the changes of every release version.

## Get Started

### Installation

Install from PyPI:

```bash
pip install nicegui_ugform
```

### Minimal Example

Here's a simple example to get started:

```python
from nicegui import ui
from nicegui_ugform import Form, FormEditor, FormDisplay, TextField, IntegerField

# Create a form
form = Form(
    title="Registration Form",
    description="Please fill out your information",
    locale="en"  # or "zh_cn" for Chinese
)

# Add fields
form.add_field(TextField(
    name="username",
    label="Username",
    required=True,
    min_length=3,
    max_length=20
))

form.add_field(IntegerField(
    name="age",
    label="Age",
    required=True,
    min_value=18,
    max_value=120
))

# Create pages
@ui.page('/')
def index():
    # Form Editor - allows users to modify form structure
    editor = FormEditor(form)
    editor.render()

@ui.page('/display')
def display():
    # Form Display - shows the form to end users
    def on_submit():
        data = form.dump_data()
        print("Submitted data:", data)
    
    display = FormDisplay(form, on_submit=on_submit)
    display.render()

ui.run()
```

## Usage

### Schema Serialization

You can export and import form schemas:

```python
# Export as JSON
schema = form.dump_schema()

# Export as compressed Base64
schema_b64 = form.dump_schema_b64(compression_flag=1)

# Import from JSON
loaded_form = Form.load_schema(schema)

# Import from Base64
loaded_form = Form.load_schema_b64(schema_b64)
```

### I18N Support

You can use different locales for the form editor and display:

```python
from nicegui_ugform import FormEditor, I18nHelper

# Get available locales
locales = I18nHelper.get_available_locales()
for loc in locales:
    print(f"{loc.name}: {loc.code}")  # English: en, Chinese (Simplified): zh_cn

# Use specific locale
editor = FormEditor(form, locale="zh_cn")

# Form locale is saved in schema and auto-applied on display
form.locale = "zh_cn"
display = FormDisplay(form)  # Will use zh_cn automatically
```

### Field Types

**TextField** - Text input with validation
```python
TextField(
    name="email",
    label="Email",
    required=True,
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)
```

**IntegerField** - Integer number input
```python
IntegerField(
    name="age",
    label="Age",
    min_value=0,
    max_value=150
)
```

**FloatField** - Decimal number input
```python
FloatField(
    name="height",
    label="Height (m)",
    min_value=0.0,
    max_value=3.0
)
```

**BooleanField** - Checkbox input
```python
BooleanField(
    name="subscribe",
    label="Subscribe to newsletter",
    default_value=False
)
```

## Licensing

This project is licensed under the MIT License. See the [License](https://github.com/isHarryh/NiceGUI-UGForm/blob/main/LICENSE) file for more details.
