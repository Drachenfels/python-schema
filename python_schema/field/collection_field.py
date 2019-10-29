from python_schema import exception, misc

from .base_field import BaseField


class CollectionField(BaseField):
    # after materialisation collection will consist elements of this typer
    _computed_type= None

    def __init__(self, name, type_, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

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

    def materialise(self):
        if isinstance(self.type_, str):
            instance = misc.ImportModule(self.type_).get_class()(
                name=self.name)
        elif isinstance(self.type_, type):
            instance = self.type_(name=self.name)
        else:
            instance = self.type_

        self._computed_type = instance

        super().materialise()

    def _loads(self, payload):
        collection = []
        normalisation_errors = {}
        validation_errors = {}

        for idx, val in enumerate(payload):
            name = f"{self.name}[{idx}]"

            instance = self._computed_type.make_new(name=name)

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

        value = self.computed_value

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
        if self.value is None:
            return None

        return [elm.as_json() for elm in self.value]

    def as_python(self):
        if self.value is None:
            return None

        return [elm.as_python() for elm in self.value]
