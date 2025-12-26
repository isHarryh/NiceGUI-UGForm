"""Tests for Form class."""

import pytest
from nicegui_ugform import Form, TextField, IntegerField


class TestForm:
    """Tests for Form class."""

    def test_creation(self):
        form = Form(title="Test Form", description="A test form")
        assert form.title == "Test Form"
        assert form.description == "A test form"
        assert len(form.fields) == 0
        assert form.uuid is not None

    def test_creation_with_uuid(self):
        uuid = "test-uuid-1234"
        form = Form(title="Test", form_uuid=uuid)
        assert form.uuid == uuid

    def test_creation_with_locale(self):
        form = Form(title="Test", locale="zh_cn")
        assert form.locale == "zh_cn"

    def test_add_field(self):
        form = Form(title="Test")
        field1 = TextField(name="field1", label="Field 1")
        field2 = IntegerField(name="field2", label="Field 2")

        form.add_field(field1)
        form.add_field(field2)

        assert len(form.fields) == 2
        assert form.fields[0] == field1
        assert form.fields[1] == field2

    def test_remove_field(self):
        form = Form(title="Test")
        field1 = TextField(name="field1", label="Field 1")
        field2 = TextField(name="field2", label="Field 2")

        form.add_field(field1)
        form.add_field(field2)
        form.remove_field("field1")

        assert len(form.fields) == 1
        assert form.fields[0] == field2

    def test_get_field(self):
        form = Form(title="Test")
        field = TextField(name="test", label="Test")
        form.add_field(field)

        assert form.get_field("test") == field
        assert form.get_field("nonexistent") is None

    def test_validation_success(self):
        form = Form(title="Test")
        field1 = TextField(name="name", label="Name", required=True)
        field2 = IntegerField(name="age", label="Age", min_value=0)
        form.add_field(field1)
        form.add_field(field2)
        field1.set_value("John")
        field2.set_value(25)

        assert form.validate() is True

    def test_validation_failure_required(self):
        form = Form(title="Test")
        field = TextField(name="name", label="Name", required=True)
        form.add_field(field)

        assert form.validate() is False

    def test_validation_failure_invalid_value(self):
        form = Form(title="Test")
        field = IntegerField(name="age", label="Age", min_value=18)
        form.add_field(field)
        field.set_value(15)

        assert form.validate() is False

    def test_dump_data(self):
        form = Form(title="Test")
        field1 = TextField(name="name", label="Name")
        field2 = IntegerField(name="age", label="Age")

        form.add_field(field1)
        form.add_field(field2)

        field1.set_value("John")
        field2.set_value(25)

        data = form.dump_data()
        assert data["name"] == "John"
        assert data["age"] == 25

    def test_dump_data_invalid(self):
        form = Form(title="Test")
        field = TextField(name="name", label="Name", required=True)
        form.add_field(field)

        with pytest.raises(ValueError):
            form.dump_data()

    def test_dump_data_allow_invalid(self):
        form = Form(title="Test")
        field = TextField(name="name", label="Name", required=True)
        form.add_field(field)

        data = form.dump_data(allow_invalid=True)
        assert data["name"] is None

    def test_load_data(self):
        form = Form(title="Test")
        field1 = TextField(name="name", label="Name")
        field2 = IntegerField(name="age", label="Age")

        form.add_field(field1)
        form.add_field(field2)

        data = {"name": "John", "age": 25}
        form.load_data(data)

        assert field1.get_value() == "John"
        assert field2.get_value() == 25

    def test_dump_schema(self):
        form = Form(title="Test Form", description="Test", locale="en")
        field = TextField(name="name", label="Name", required=True)
        form.add_field(field)

        schema = form.dump_schema()
        assert schema["title"] == "Test Form"
        assert schema["description"] == "Test"
        assert schema["locale"] == "en"
        assert schema["uuid"] == form.uuid
        assert len(schema["fields"]) == 1
        assert schema["fields"][0]["name"] == "name"

    def test_load_schema(self):
        schema = {
            "uuid": "test-uuid",
            "title": "Test Form",
            "description": "A test",
            "locale": "zh_cn",
            "fields": [
                {
                    "type": "TextField",
                    "name": "name",
                    "label": "Name",
                    "required": True,
                    "min_length": 2,
                },
                {
                    "type": "IntegerField",
                    "name": "age",
                    "label": "Age",
                    "min_value": 0,
                    "max_value": 150,
                },
            ],
        }

        form = Form.load_schema(schema)
        assert form.title == "Test Form"
        assert form.description == "A test"
        assert form.locale == "zh_cn"
        assert form.uuid == "test-uuid"
        assert len(form.fields) == 2

        field1 = form.fields[0]
        assert isinstance(field1, TextField)
        assert field1.name == "name"
        assert field1.required is True

        field2 = form.fields[1]
        assert isinstance(field2, IntegerField)
        assert field2.name == "age"
