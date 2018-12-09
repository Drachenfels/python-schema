from python_schema import exception

from .base_field import BaseField


class StrField(BaseField):
    def normalise(self, value):
        value = super().normalise(value)

        if value is None:
            return value

        message = f"StrField cannot be populated with value: {value}"

        try:
            value = str(value)
        except (TypeError, ValueError):
            self.errors.append(message)

            raise exception.NormalisationError(message)

        return value
