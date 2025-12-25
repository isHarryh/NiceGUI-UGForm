"""Field classes for form construction."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
import re


class BaseFormNode(ABC):
    """Base class for all form nodes."""

    def __init__(self, name: str):
        """Initializes the form node.

        Args:
            name: Unique identifier for this form node.
        """
        self.name = name


T = TypeVar("T")


class BaseFormField(BaseFormNode, Generic[T], ABC):
    """Base class for all form fields with type safety."""

    def __init__(
        self,
        name: str,
        label: str,
        description: Optional[str] = None,
        required: bool = False,
        default_value: Optional[T] = None,
    ):
        """Initializes the form field.

        Args:
            name: Unique identifier for this field.
            label: Display label for the field.
            description: Optional small description for the field.
            required: Whether the field is required.
            default_value: Default value for the field.
        """
        super().__init__(name)
        self.label = label
        self.description = description
        self.required = required
        self.default_value = default_value
        self.current_value: Optional[T] = default_value

    def set_value(self, value: Optional[T]) -> None:
        """Sets the current value of the field.

        Args:
            value: The value to set.
        """
        self.current_value = value

    def get_value(self) -> Optional[T]:
        """Gets the current value of the field.

        Returns:
            The current value of the field.
        """
        return self.current_value

    @abstractmethod
    def validate(self, value: T) -> bool:
        """Validates the given value.

        Args:
            value: The value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        pass

    def to_dict(self) -> dict:
        """Converts the field to a dictionary representation.

        Returns:
            Dictionary containing field configuration.
        """
        result = {
            "type": self.__class__.__name__,
            "name": self.name,
            "label": self.label,
            "required": self.required,
        }
        if self.description:
            result["description"] = self.description
        if self.default_value is not None:
            result["default_value"] = self.default_value
        return result


class TextField(BaseFormField[str]):
    """Text field for string input."""

    def __init__(
        self,
        name: str,
        label: str,
        description: Optional[str] = None,
        required: bool = False,
        default_value: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
    ):
        """Initializes the text field.

        Args:
            name: Unique identifier for this field.
            label: Display label for the field.
            description: Optional small description for the field.
            required: Whether the field is required.
            default_value: Default value for the field.
            min_length: Minimum length for the text.
            max_length: Maximum length for the text.
            regex: Regular expression pattern for validation.
        """
        super().__init__(name, label, description, required, default_value)
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex

    def validate(self, value: str) -> bool:
        """Validates the given string value.

        Args:
            value: The string value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        if value is None:
            return not self.required

        if not isinstance(value, str):
            return False

        if self.min_length is not None and len(value) < self.min_length:
            return False

        if self.max_length is not None and len(value) > self.max_length:
            return False

        if self.regex is not None:
            if not re.match(self.regex, value):
                return False

        return True

    def to_dict(self) -> dict:
        """Converts the field to a dictionary representation.

        Returns:
            Dictionary containing field configuration.
        """
        result = super().to_dict()
        if self.min_length is not None:
            result["min_length"] = self.min_length
        if self.max_length is not None:
            result["max_length"] = self.max_length
        if self.regex is not None:
            result["regex"] = self.regex
        return result


class FloatField(BaseFormField[float]):
    """Float field for decimal number input."""

    def __init__(
        self,
        name: str,
        label: str,
        description: Optional[str] = None,
        required: bool = False,
        default_value: Optional[float] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ):
        """Initializes the float field.

        Args:
            name: Unique identifier for this field.
            label: Display label for the field.
            description: Optional small description for the field.
            required: Whether the field is required.
            default_value: Default value for the field.
            min_value: Minimum value for the field.
            max_value: Maximum value for the field.
        """
        super().__init__(name, label, description, required, default_value)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: float) -> bool:
        """Validates the given float value.

        Args:
            value: The float value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        if value is None:
            return not self.required

        if not isinstance(value, (int, float)):
            return False

        value = float(value)

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True

    def to_dict(self) -> dict:
        """Converts the field to a dictionary representation.

        Returns:
            Dictionary containing field configuration.
        """
        result = super().to_dict()
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        return result


class IntegerField(BaseFormField[int]):
    """Integer field for whole number input."""

    def __init__(
        self,
        name: str,
        label: str,
        description: Optional[str] = None,
        required: bool = False,
        default_value: Optional[int] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ):
        """Initializes the integer field.

        Args:
            name: Unique identifier for this field.
            label: Display label for the field.
            description: Optional small description for the field.
            required: Whether the field is required.
            default_value: Default value for the field.
            min_value: Minimum value for the field.
            max_value: Maximum value for the field.
        """
        super().__init__(name, label, description, required, default_value)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: int) -> bool:
        """Validates the given integer value.

        Args:
            value: The integer value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        if value is None:
            return not self.required

        if not isinstance(value, int) or isinstance(value, bool):
            return False

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True

    def to_dict(self) -> dict:
        """Converts the field to a dictionary representation.

        Returns:
            Dictionary containing field configuration.
        """
        result = super().to_dict()
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        return result


class BooleanField(BaseFormField[bool]):
    """Boolean field for true/false input."""

    def __init__(
        self,
        name: str,
        label: str,
        description: Optional[str] = None,
        required: bool = False,
        default_value: Optional[bool] = None,
    ):
        """Initializes the boolean field.

        Args:
            name: Unique identifier for this field.
            label: Display label for the field.
            description: Optional small description for the field.
            required: Whether the field is required.
            default_value: Default value for the field.
        """
        super().__init__(name, label, description, required, default_value)

    def validate(self, value: bool) -> bool:
        """Validates the given boolean value.

        Args:
            value: The boolean value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        if value is None:
            return not self.required

        return isinstance(value, bool)
