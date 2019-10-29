from python_schema import exception, misc

from .base_field import BaseField


class SchemaField(BaseField):
    # configuration of the object:
    exception_on_unknown = True
    fields = None

    # state of the object:

    # fields are all fields set on that schema
    fields = None

    # _computed_fields are all fields set on that schema + everything that is
    # inherited from parent classes
    _computed_fields = None

    # if _class is not none we are lazy loading SchemaField
    _class = None

    def __init__(
            self, name=None, class_=None, fields=None,
            *args, **kwargs):  # NOQA
        """Initialises new instance of the Schema.

        name - optional name for the schema if not given it will be taken from
            __class__.__name__ what is usually enough but if class Schema is
            created `inline` probably makes sense to override it

        fields - optional list of fields that should be added to this schema,
            allows to modyfy on the fly content of SchemaField
        """
        # name is mandatory, but SchemaField is a class and as such we
        # can take class name as a name
        if name is None:
            name = self.__class__.__name__

        super().__init__(name, *args, **kwargs)

        if fields is None:
            fields = []

        if self.fields is None:
            self.fields = []

        new_fields = {field.name: field for field in fields}

        base_fields = {field.name: field for field in self.fields}

        base_fields.update(new_fields)

        self.fields = list(base_fields.values())

        self._class = class_

    def materialise(self):
        if self.is_materialised:
            return

        super().materialise()

        if self._class is None:
            class_type = self.__class__
        elif isinstance(self._class, str):
            class_type = misc.ImportModule(self._class).get_instance()
        elif isinstance(self._class, SchemaField):
            class_type = self._class.__class__
        else:
            class_type = self._class

        if self._class is not None:
            self.fields = class_type.fields

        # self.fields might be injected on __init__ level thus this special
        # case
        different_fields = [self.fields] + [
            getattr(some_class, 'fields')
            for some_class in class_type.mro()[:-1]
            if getattr(some_class, 'fields', None)
        ]

        self._computed_fields = {}

        # reads all parents with exception of base Object type
        for fields in different_fields:
            for field in fields:
                if field.name in self._computed_fields:
                    continue

                self._computed_fields[field.name] = field.make_new()

    def normalise(self, value):
        value = super().normalise(value)

        if value is None:
            return value

        if self.exception_on_unknown:
            unknown_keys = set(value.keys()).difference(
                set(self._computed_fields.keys()))

            if unknown_keys:
                message = "Unexpected payload with key(s): {}".format(
                    ', '.join(unknown_keys))

                self.errors.append(message)

                raise exception.UnknownFieldError(message)

        return value

    def update_defaults(self, **kwargs):
        kwargs = super().update_defaults(**kwargs)

        kwargs.setdefault('class_', self._class)

        return kwargs

    def loads(self, payload):
        self.reset_state()

        self.materialise()

        payload = self.normalise(payload)

        self.validate(payload)

        # when value is not dict-like, finish early
        if payload is None:
            return

        schema = {}

        for key, field in self._computed_fields.items():
            schema[key] = field.make_new()

            if key in payload:
                schema[key].loads(payload[key])

            schema[key].parent = self

        self.value = schema

    def as_json(self):
        if not self.is_set:
            return self.default

        output = {}

        for key, value in self.value.items():
            output[key] = value.as_json()

        return output

    def as_python(self):
        if not self.is_set:
            return self.default

        output = {}

        for key, value in self.value.items():
            output[key] = value.as_python()

        return output

    def __str__(self):
        prefix = '\t' * self.total_parents

        output = [
            f'<SchemaField({self.name}={{',
        ]

        for key, value in self.value.items():
            output.append(f'{prefix}\t{key}: {value}')

        output.append(
            f'{prefix}}})>'
        )

        return '\n'.join(output)

    def __repr__(self):
        return (
            f'<SchemaField({self.name}={self.value})>'
        )

    def __eq__(self, dct):
        if not hasattr(dct, 'items') or not hasattr(dct, 'keys'):
            raise exception.ReadValueError(
                "Unable to compare SchemaField with non dict-like object "
                "(missing implementation of .items() and .keys())"
            )

        local_keys = set([
            key for key, field in self.value.items() if not isinstance(
                field.value, misc.NotSet)])

        if set(dct.keys()).symmetric_difference(local_keys):
            return False

        for key, value in dct.items():
            if key not in self:
                return False

            if self[key] != value:
                return False

        return True

    def __iter__(self):
        return self.value.__iter__()

    def __next__(self):
        try:
            return self.value.__next__()
        except IndexError:
            raise StopIteration

    def __getitem__(self, key):
        if key not in self._computed_fields:
            raise exception.ReadValueError(f"Schema has no field {key}")

        return self.value[key]
