class BasePythonSchemaError(Exception):
    """Base class in order to catch all python-schema easily
    """


class SchemaConfigurationError(BasePythonSchemaError):
    """When schema or element of it is misconfigured and cannot work in such
    shape.
    """
    pass


class PayloadError(BasePythonSchemaError):
    """Base exception fo for all payload related problems.
    """
    pass


class NormalisationError(PayloadError):
    """Base exception for group of errors that happen during normalisation.
    """


class ValidationError(PayloadError):
    """Base exception for group of errors that happen during validation.

    Raising ValidationError inside validating function causes short-circuit
    validation, in contrast to returning anything but string.
    """


class NoneNotAllowedError(NormalisationError):
    """Normalisation error when object is fed with None but it's not allowed
    value.
    """


class UnknownFieldError(NormalisationError):
    """Normalisation error when schema is fed with pair key=value that is not
    expected to have.
    """
    pass


class ReadValueError(BasePythonSchemaError):
    """Exception happens when attempting to read a field that was never
    populated with data.
    """
    pass
