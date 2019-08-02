from python_schema import exception

from .base_field import BaseField


class CollectionField(BaseField):
    def __init__(self, name, type_, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        # self.type_ can be passed as instance of type, after this point we
        # will consistently expect it to be an instance
        if isinstance(type_, type):
            type_ = type_(name=self.name)

        self.type_ = type_

    def normalise(self, value):
        value = super().normalise(value)

        if value is None:
            return value

        message = (
            f"CollectionField cannot be populated with value: {value}. "
            "Value is not iterable."
        )

        try:
            # check if we can iterate over value, it has to be list-like object
            [elm for elm in value]
        except (TypeError, ValueError):
            self.errors.append(message)

            raise exception.NormalisationError(message)

        return value

    def update_defaults(self, **kwargs):
        kwargs = super().update_defaults(**kwargs)

        kwargs.setdefault('type_', self.type_)

        return kwargs

    def load_collection(self, payload):
        collection = []
        normalisation_errors = {}
        validation_errors = {}

        for idx, val in enumerate(payload):
            name = f"{self.name}[{idx}]"

            instance = self.type_.make_new(name=name)

            try:
                instance.loads(val)
            except (exception.NormalisationError,):
                normalisation_errors[idx] = instance.errors

                continue
            except (exception.ValidationError,):
                validation_errors[idx] = instance.errors

                continue

            instance.parent = self

            collection.append(instance)

        if normalisation_errors:
            self.errors = [normalisation_errors]

            raise exception.PayloadError(
                "Unable to load items in collection: {}".format(self.errors))

        if validation_errors:
            self.errors = [validation_errors]

            raise exception.ValidationError('Validation error')

        return collection

    def loads(self, payload):
        self.reset_state()

        payload = self.normalise(payload)

        self.validate(payload)

        self.value = payload if payload is None else \
            self.load_collection(payload)

    def __eq__(self, values):
        if len(self) != len(values):
            return False

        for idx, value in enumerate(values):
            if self[idx] != value:
                return False

        return True

    def __str__(self):
        prefix = '\t' * self.total_parents

        output = [
            f'<CollectionField({self.name}=[',
        ]

        for value in self.value:
            output.append('\t{},'.format(value))

        output.append(
            f'{prefix}])>',
        )

        return '\n'.join(output)

    def __repr__(self):
        return super().__str__()

    def __getitem__(self, idx):
        return self.value[idx]

    def __len__(self):
        return len(self.value)

    def as_json(self):
        val = self.value

        if self.is_set:
            return None if val is None else [elm.as_json() for elm in val]

        return val

    def as_python(self):
        val = self.value

        if self.is_set:
            return None if val is None else [elm.as_python() for elm in val]

        return val
