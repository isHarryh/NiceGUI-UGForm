"""Translation keys."""

from typing import NamedTuple


class TranslationMap(NamedTuple):
    # Button texts
    submit: str
    reset: str
    addField: str
    deleteField: str
    complete: str
    exportJson: str
    exportBase64: str

    # Field type texts
    text: str
    integer: str
    float: str
    boolean: str

    # Property label texts
    label: str
    description: str
    required: str
    defaultValue: str
    fieldName: str
    fieldType: str

    # Section headers
    formEditor: str
    formInformation: str
    formDescription: str
    formFields: str
    formTitle: str
    formLocale: str
    uuid: str
    showResetButton: str
    showSubmitButton: str

    # Field-specific properties
    minLength: str
    maxLength: str
    regexPattern: str
    minValue: str
    maxValue: str

    # Validation messages
    requiredField: str
    invalidTypeTemplate: str
    invalidValueTemplate: str
    tooShortTemplate: str
    tooLongTemplate: str
    regexPatternMismatch: str
    tooSmallTemplate: str
    tooLargeTemplate: str

    # Template texts
    newFieldTemplate: str

    # Notification messages
    jsonSchemaCopied: str
    base64SchemaCopied: str
    pleaseFixValidationErrors: str
    formReset: str
    fieldRequiredTemplate: str
    fieldInvalidValueTemplate: str
