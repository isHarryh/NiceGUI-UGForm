"""Tests for form serialization and deserialization."""

import pytest
from nicegui_ugform import Form, TextField, IntegerField, FloatField


class TestSerialization:
    """Tests for form serialization."""

    def test_roundtrip_json(self):
        """Test JSON serialization roundtrip."""
        form = Form(title="Test", description="Description", locale="en")
        form.add_field(TextField(name="name", label="Name", required=True, min_length=2))
        form.add_field(IntegerField(name="age", label="Age", min_value=18, max_value=120))

        schema = form.dump_schema()
        loaded_form = Form.load_schema(schema)

        assert loaded_form.title == form.title
        assert loaded_form.description == form.description
        assert loaded_form.locale == form.locale
        assert len(loaded_form.fields) == len(form.fields)

        field1 = loaded_form.fields[0]
        assert field1.name == "name"
        assert getattr(field1, "required") is True
        assert getattr(field1, "min_length") == 2

        field2 = loaded_form.fields[1]
        assert field2.name == "age"
        assert getattr(field2, "min_value") == 18
        assert getattr(field2, "max_value") == 120

    def test_roundtrip_binary_uncompressed(self):
        form = Form(title="Test Form")
        form.add_field(TextField(name="field", label="Field"))

        binary = form.dump_schema_bin(compression_flag=0)
        loaded_form = Form.load_schema_bin(binary)

        assert loaded_form.title == form.title
        assert len(loaded_form.fields) == 1

    def test_roundtrip_binary_compressed(self):
        form = Form(title="Test Form")
        form.add_field(TextField(name="field", label="Field"))

        binary = form.dump_schema_bin(compression_flag=1)
        loaded_form = Form.load_schema_bin(binary)

        assert loaded_form.title == form.title
        assert len(loaded_form.fields) == 1

    def test_roundtrip_base64(self):
        form = Form(title="Test Form", locale="zh_cn")
        form.add_field(FloatField(name="value", label="Value", min_value=0.0, max_value=100.0))

        b64_string = form.dump_schema_b64(compression_flag=1)
        loaded_form = Form.load_schema_b64(b64_string)

        assert loaded_form.title == form.title
        assert len(loaded_form.fields) == 1

    def test_invalid_binary_magic(self):
        with pytest.raises(ValueError, match="magic number"):
            Form.load_schema_bin(b"FUCK\x01\x00\x00\x00" + b"{}")

    def test_invalid_binary_too_short(self):
        with pytest.raises(ValueError, match="too short"):
            Form.load_schema_bin(b"")
        with pytest.raises(ValueError, match="too short"):
            Form.load_schema_bin(b"UGFS")
        with pytest.raises(ValueError, match="too short"):
            Form.load_schema_bin(b"UGFS\x01\x00")

    def test_invalid_compression_flag(self):
        with pytest.raises(ValueError, match="compression flag"):
            Form.load_schema_bin(b"UGFS\x01\xff\x00\x00" + b"{}")
