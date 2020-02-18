from python_schema import exception, misc

from .base_field import BaseField


class CollectionField(BaseField):
    field_type = None

    def __init__(self, name, field_type=None, **kwargs):
        """CollectionField as name suggest is a collection of other
        python-schema fields.

            name :: mandatory name of this field

            field_type :: instance of the python-schema field that should be
                used as a template for consecutive elements of the collection

            kwargs :: remaining configuration options that super-class
                `BaseField` defines

        """
        super().__init__(name, **kwargs)

        if field_type is not None:
            if isinstance(field_type, type):
                raise exception.SchemaConfigurationError(
                    f'CollectionField requires that argument field_type is an '
                    f'instance and not type, got {field_type}'
                )

            self.field_type = field_type

        if self.field_type is None:
            raise exception.SchemaConfigurationError(
                "CollectionField requires to have field_type to be not None"
            )

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

        kwargs.setdefault('field_type', self.field_type)

        return kwargs

    def loads(self, payload):
        self.reset_state()

        payload = self.normalise(payload)

        self.validate(payload)

        if payload is None:
            self.value = None

            return

        collection = []
        normalisation_errors = {}
        validation_errors = {}

        for idx, val in enumerate(payload):
            name = f"{self.name}[{idx}]"

            instance = self.field_type.make_new(name=name)

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

        self.value = collection

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

        value = self.get_final_value()

        if value is misc.NotSet:
            value = ['NotSet']

        for value in value:
            output.append('\t{},'.format(value))

        output.append(
            f'{prefix}])>',
        )

        return '\n'.join(output)

    def __getitem__(self, idx):
        return self.value[idx]

    def __len__(self):
        return len(self.value)

    def as_json(self):
        val = self.get_final_value()
        if self.get_final_value() is None:
            return None

        return [elm.as_json() for elm in self.value]

    def as_python(self):
        if self.value is None:
            return None

        return [elm.as_python() for elm in self.value]
