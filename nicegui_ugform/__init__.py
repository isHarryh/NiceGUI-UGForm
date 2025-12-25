"""NiceGUI-UGForm: A form builder and display library for NiceGUI."""

from .core import (
    BaseFormField,
    BaseFormNode,
    BooleanField,
    FloatField,
    Form,
    IntegerField,
    TextField,
)
from .ui import FormDisplay, FormEditor

__version__ = "1.0.0"

__all__ = [
    "BaseFormNode",
    "BaseFormField",
    "TextField",
    "FloatField",
    "IntegerField",
    "BooleanField",
    "Form",
    "FormEditor",
    "FormDisplay",
]
