from python_schema import exception

from .base_field import BaseField


class IntField(BaseField):
    def normalise(self, value):
        """BaseField accepts all values as-is
        """
        value = super().normalise(value)

        if value is None:
            return value

        message = f"IntField cannot be populated with value: {value}"

        try:
            # first convert to str so that 12.2 won't be accepted as integer
            value = int(str(value))
        except (TypeError, ValueError):
            self.errors.append(message)

            raise exception.NormalisationError(message)

        return value
