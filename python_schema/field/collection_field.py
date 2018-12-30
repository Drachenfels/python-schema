from python_schema import exception

from .base_field import BaseField


class CollectionField(BaseField):
    def __init__(self, name, type_, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        # self.type_ we expect that after this point is going to be fully
        # fleshed out
        if isinstance(type_, type):
            type_ = type_(name=self.name, parent=self)

        self.type_ = type_

    def get_inheritable_attributes(self):
        attributes = super().get_inheritable_attributes()

        attributes.append('type_')

        return attributes

    def normalise(self, value):
        value = super().normalise(value)

        if value is None:
            return value

        message = (
            f"CollectionField cannot be populated with value: {value}. "
            "Value is not considered iterable."
        )

        # first check if we can iterate over value
        try:
            for elm in value:
                pass
        except (TypeError, ValueError):
            self.errors.append(message)

            raise exception.NormalisationError(message)

        normalised_values = []

        for elm in value:
            try:
                normalised_values.append(self.type_.normalise(elm))
            except exception.NormalisationError as err:
                self.errors.append(str(err))

        if self.errors:
            raise exception.NormalisationError(self.errors)

        return normalised_values

    def create_instance(self, idx):
        kwargs = {
            'name': f"{self.name}[{idx}]",
        }

        for attribute in self.type_.get_inheritable_attributes():
            kwargs[attribute] = getattr(self.type_, attribute)

        return self.type_.__class__(**kwargs)

    def prepare_value(self, value):
        value = super().prepare_value(value)

        # when value is not iterable, finish early
        if value is None:
            return value

        collection = []
        collection_errors = {}

        for idx, val in enumerate(value):
            instance = self.create_instance(idx)

            try:
                instance.loads(val)
            except (exception.PayloadError,):
                collection_errors[idx] = instance.errors

                continue

            collection.append(instance)

        if collection_errors:
            self.errors = [collection_errors]

        if self.errors:
            raise exception.ValidationError(errors=self.errors)

        return collection

    def as_json(self):
        if not self.is_set:
            return self.default

        if self.value is None:
            return self.value

        return [
            elm.as_json() for elm in self.value
        ]

    def as_dictionary(self):
        if not self.is_set:
            return self.default

        if self.value is None:
            return self.value

        return [
            elm.as_dictionary() for elm in self.value
        ]
