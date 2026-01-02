"""Form class for managing form structure and data."""

import base64
import gzip
import json
import uuid
from typing import List, Literal, Optional

from .fields import (
    BaseFormField,
    BaseFormNode,
    BooleanField,
    FloatField,
    IntegerField,
    TextField,
)


class Form:
    """Represents a form with fields and validation logic."""

    _SCHEMA_VERSION = 1

    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        fields: Optional[List[BaseFormNode]] = None,
        form_uuid: Optional[str] = None,
        locale: Optional[str] = None,
        show_reset_button: bool = True,
        show_submit_button: bool = True,
    ):
        """Initializes the form.

        Args:
            title: The title of the form.
            description: Optional description of the form.
            fields: List of form fields.
            form_uuid: Optional UUID for the form. If not provided, generates one.
            locale: The locale code for form display (e.g., 'en', 'zh_cn').
            show_reset_button: Whether to show the reset button (default: True).
            show_submit_button: Whether to show the submit button (default: True).
        """
        self.uuid = form_uuid or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.locale = locale
        self.show_reset_button = show_reset_button
        self.show_submit_button = show_submit_button
        self.fields: List[BaseFormNode] = fields or []

    def add_field(self, field: BaseFormNode) -> None:
        """Adds a field to the form.

        Args:
            field: The field to add.
        """
        self.fields.append(field)

    def remove_field(self, name: str) -> None:
        """Removes a field from the form by name.

        Args:
            name: The name of the field to remove.
        """
        self.fields = [f for f in self.fields if f.name != name]

    def get_field(self, name: str) -> Optional[BaseFormNode]:
        """Gets a field by name.

        Args:
            name: The name of the field to get.

        Returns:
            The field if found, None otherwise.
        """
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def validate(self) -> bool:
        """Validates the form data for completeness and correctness.

        Returns:
            True if all fields are valid, False otherwise.
        """
        for field in self.fields:
            if isinstance(field, BaseFormField):
                value = field.get_value()
                if field.required and value is None:
                    return False
                if value is not None and not field.is_validated(value):
                    return False
        return True

    def dump_data(self, allow_invalid: bool = False) -> dict:
        """Returns the JSON representation of form data.

        Args:
            allow_invalid: If False, raises ValueError if validation fails.

        Returns:
            Dictionary containing form data.

        Raises:
            ValueError: If validation fails and allow_invalid is False.
        """
        if not allow_invalid and not self.validate():
            raise ValueError("Form validation failed")

        data = {}
        for field in self.fields:
            if isinstance(field, BaseFormField):
                data[field.name] = field.get_value()
        return data

    def dump_schema(self) -> dict:
        """Returns the JSON representation of the form schema.

        Returns:
            Dictionary containing form schema.
        """
        schema = {
            "uuid": self.uuid,
            "title": self.title,
            "fields": [],
            "show_reset_button": self.show_reset_button,
            "show_submit_button": self.show_submit_button,
        }

        if self.description:
            schema["description"] = self.description

        if self.locale:
            schema["locale"] = self.locale

        for field in self.fields:
            if isinstance(field, BaseFormField):
                schema["fields"].append(field.to_dict())

        return schema

    def dump_schema_bin(self, compression_flag: Literal[0, 1] = 1) -> bytes:
        """Returns binary representation of the form schema.

        Args:
            compression_flag: Compression type (0 = no compression, 1 = gzip compression).

        Returns:
            Binary representation with the following encoding:
            - 0x00~0x03: Magic number 'UGFS' (User Generated Form Schema)
            - 0x04: Schema version number
            - 0x05: Compression flag
            - 0x06~0x07: Reserved (0x00)
            - 0x08~: UTF-8 encoded JSON schema, compressed if flag is 1
        """
        schema = self.dump_schema()
        json_str = json.dumps(schema, separators=(",", ":"))
        json_bytes = json_str.encode("utf-8")

        # Apply compression if requested
        if compression_flag == 1:
            json_bytes = gzip.compress(json_bytes)

        # Build binary format
        magic = b"UGFS"  # 0x00~0x03
        version = bytes([self._SCHEMA_VERSION])  # 0x04
        compression = bytes([compression_flag])  # 0x05
        reserved = b"\x00\x00"  # 0x06~0x07

        return magic + version + compression + reserved + json_bytes

    def dump_schema_b64(self, compression_flag: Literal[0, 1] = 1) -> str:
        """Returns Base64-encoded binary representation of the form schema.

        Args:
            compression_flag: Compression type (0 = no compression, 1 = gzip compression).

        Returns:
            Base64-encoded string of the binary schema.
        """
        binary_data = self.dump_schema_bin(compression_flag)
        return base64.b64encode(binary_data).decode("ascii")

    @classmethod
    def load_schema(cls, schema: dict) -> "Form":
        """Loads form definition from JSON.

        Args:
            schema: Dictionary containing form schema.

        Returns:
            A new Form instance.
        """
        form = cls(
            title=schema["title"],
            description=schema.get("description"),
            form_uuid=schema.get("uuid"),
            locale=schema.get("locale"),
            show_reset_button=schema.get("show_reset_button", True),
            show_submit_button=schema.get("show_submit_button", True),
        )

        field_map = {
            "TextField": TextField,
            "FloatField": FloatField,
            "IntegerField": IntegerField,
            "BooleanField": BooleanField,
        }

        for field_data in schema.get("fields", []):
            field_type = field_data.pop("type")
            if field_type in field_map:
                field_class = field_map[field_type]
                field = field_class(**field_data)
                form.add_field(field)

        return form

    @classmethod
    def load_schema_bin(cls, schema_bin: bytes) -> "Form":
        """Loads form definition from binary data.

        Args:
            schema_bin: Binary data with the schema encoding.

        Returns:
            A new Form instance.

        Raises:
            ValueError: If the binary data format is invalid.
        """
        # Validate minimum length
        if len(schema_bin) < 8:
            raise ValueError("Invalid binary schema: too short")

        # Validate magic number
        if schema_bin[0:4] != b"UGFS":
            raise ValueError("Invalid binary schema: magic number mismatch")

        # Extract metadata
        version = schema_bin[4]
        compression_flag = schema_bin[5]
        # reserved = schema_bin[6:8]  # Not used currently

        # Extract and decompress JSON data
        json_bytes = schema_bin[8:]

        if compression_flag == 1:
            json_bytes = gzip.decompress(json_bytes)
        elif compression_flag != 0:
            raise ValueError(f"Invalid compression flag: {compression_flag}")

        # Parse JSON
        json_str = json_bytes.decode("utf-8")
        schema = json.loads(json_str)

        return cls.load_schema(schema)

    @classmethod
    def load_schema_b64(cls, schema_b64: str) -> "Form":
        """Loads form definition from Base64-encoded string.

        Args:
            schema_b64: Base64-encoded binary schema string.

        Returns:
            A new Form instance.
        """
        binary_data = base64.b64decode(schema_b64.encode("ascii"))
        return cls.load_schema_bin(binary_data)

    def load_data(self, data: dict) -> None:
        """Loads form data from dictionary.

        Args:
            data: Dictionary containing field values.
        """
        for field in self.fields:
            if isinstance(field, BaseFormField):
                if field.name in data:
                    field.set_value(data[field.name])
