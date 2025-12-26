"""Tests for field types and validation."""

import pytest
from nicegui_ugform import TextField, IntegerField, FloatField, BooleanField


class TestTextField:
    """Tests for TextField."""

    def test_creation(self):
        field = TextField(name="username", label="Test")
        assert field.name == "username"
        assert field.label == "Test"
        assert field.required is False
        assert field.default_value is None

    def test_set_get_value(self):
        field = TextField(name="username", label="Test")
        field.set_value("hello")
        assert field.get_value() == "hello"

    def test_required_validation(self):
        field = TextField(name="username", label="Test", required=True)
        assert not field.validate(None)
        assert field.validate("hello")

    def test_min_max_length_validation(self):
        field = TextField(name="username", label="Test", min_length=3, max_length=5)
        assert not field.validate("")
        assert not field.validate("ab")
        assert field.validate("abc")
        assert field.validate("abcd")
        assert field.validate("abcde")
        assert not field.validate("abcdef")

    def test_regex_validation(self):
        field = TextField(name="email", label="Email", regex=r"^[a-z]+@[a-z]+\.[a-z]+$")
        assert field.validate("test@example.com")
        assert not field.validate("invalid-email")
        assert not field.validate("test@")

    def test_to_dict(self):
        field = TextField(
            name="test",
            label="Test",
            description="A test field",
            required=True,
            min_length=3,
            max_length=5,
            regex=r"^[a-z]+$",
        )
        data = field.to_dict()
        assert data["type"] == "TextField"
        assert data["name"] == "test"
        assert data["label"] == "Test"
        assert data["description"] == "A test field"
        assert data["required"] is True
        assert data["min_length"] == 3
        assert data["max_length"] == 5
        assert data["regex"] == r"^[a-z]+$"


class TestIntegerField:
    """Tests for IntegerField."""

    def test_creation(self):
        field = IntegerField(name="age", label="Age")
        assert field.name == "age"
        assert field.label == "Age"

    def test_common_validation(self):
        """Test integer validation with different value types."""
        field = IntegerField(name="age", label="Age")
        assert field.validate(None)
        assert field.validate(25)
        assert not field.validate("not a number")
        assert not field.validate(25.5)

    def test_required_validation(self):
        """Test required field validation."""
        field = IntegerField(name="age", label="Age", required=True)
        assert not field.validate(None)
        assert field.validate(25)

    def test_min_max_value_validation(self):
        field = IntegerField(name="age", label="Age", min_value=18, max_value=120)
        assert not field.validate(17)
        assert field.validate(18)
        assert field.validate(100)
        assert field.validate(120)
        assert not field.validate(121)

    def test_to_dict(self):
        field = IntegerField(name="age", label="Age", min_value=18, max_value=120)
        data = field.to_dict()
        assert data["type"] == "IntegerField"
        assert data["min_value"] == 18
        assert data["max_value"] == 120


class TestFloatField:
    """Tests for FloatField."""

    def test_creation(self):
        field = FloatField(name="height", label="Height")
        assert field.name == "height"
        assert field.label == "Height"

    def test_validation(self):
        field = FloatField(name="height", label="Height")
        assert field.validate(None)
        assert field.validate(1.75)
        assert field.validate(2)  # int is acceptable
        assert not field.validate("not a number")

    def test_min_max_value_validation(self):
        field = FloatField(name="height", label="Height", min_value=0.5, max_value=3.0)
        assert not field.validate(0.4)
        assert field.validate(0.5)
        assert field.validate(2.0)
        assert field.validate(3.0)
        assert not field.validate(3.1)

    def test_to_dict(self):
        field = FloatField(name="height", label="Height", min_value=0.0, max_value=3.0)
        data = field.to_dict()
        assert data["type"] == "FloatField"
        assert data["min_value"] == 0.0
        assert data["max_value"] == 3.0


class TestBooleanField:
    """Tests for BooleanField."""

    def test_creation(self):
        field = BooleanField(name="subscribe", label="Subscribe")
        assert field.name == "subscribe"
        assert field.label == "Subscribe"

    def test_validation(self):
        field = BooleanField(name="subscribe", label="Subscribe")
        assert field.validate(None)
        assert field.validate(True)
        assert field.validate(False)

    def test_default_value(self):
        field = BooleanField(name="subscribe", label="Subscribe", default_value=True)
        assert field.default_value is True
        assert field.get_value() is True

    def test_to_dict(self):
        field = BooleanField(name="subscribe", label="Subscribe", default_value=False)
        data = field.to_dict()
        assert data["type"] == "BooleanField"
        assert data["default_value"] is False
