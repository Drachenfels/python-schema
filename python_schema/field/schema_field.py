from python_schema import exception, misc

from .base_field import BaseField


class SchemaField(BaseField):
    # configuration:

    # throw exception if loads receives unexpected key, otherwise ignore
    # silently
    exception_on_unknown = True
    fields = None
    schema = None  # allows lazy load and inline definition

    # state:

    # computed_fields takes into account parents, overrides and everything in
    # between, is set automatically during materailisation
    _computed_fields = None

    def __init__(
            self, name=None, schema=None, fields=None,
            exception_on_unknown=None, **kwargs):  # NOQA
        """Initialises new instance of the Schema.

        name - optional name for the schema if not given it will be taken from
            __class__.__name__ what is usually enough but if class Schema is
            created `inline` probably makes sense to override it

        class_ - class of schema field, should only be in use when lazy loading

        fields - optional list of fields that should be added to this schema,
            allows to modyfy on the fly content of SchemaField
        """
        # name is mandatory, but SchemaField is a class and as such we
        # can take class name as a name
        if name is None:
            name = self.__class__.__name__

        super().__init__(name, **kwargs)

        if self.fields is None:
            self.fields = []

        # this allows to set or override any fields defined on schema
        if fields:
            base_fields = {field.name: field for field in self.fields}

            base_fields.update({
                field.name: field for field in fields
            })

            self.fields = list(base_fields.values())

        self.exception_on_unknown = (
            (True if self.exception_on_unknown is True else False)
            if exception_on_unknown is None else exception_on_unknown
        )

        self.schema = self.__class__ if schema is None else schema

    def materialise(self):
        if isinstance(self.schema, str):
            schema = misc.ImportModule(self.schema).get_class()
        elif isinstance(self.schema, SchemaField):
            schema = self.schema.__class__
        else:
            schema = self.schema

        self._computed_fields = {}

        for field in self.fields:
            if field.name in self._computed_fields:
                continue

            self._computed_fields[field.name] = field.make_new(
                name=field.name)

        # reads all parents and adds all parents fields to our list of fields
        for ancestor in schema.mro()[:-1]:
            fields = getattr(ancestor, 'fields', None)

            if not fields:
                continue

            for field in fields:
                if field.name in self._computed_fields:
                    continue

                self._computed_fields[field.name] = field.make_new(
                    name=field.name)

        super().materialise()

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

        kwargs.setdefault('schema', self.schema)
        kwargs.setdefault('fields', self.fields)
        kwargs.setdefault('exception_on_unknown', self.exception_on_unknown)

        return kwargs

    def _loads(self, payload):
        if payload is None:
            self.value = None

            return

        schema = {}

        for key, field in self._computed_fields.items():
            schema[key] = field.make_new()

            if key in payload:
                schema[key].loads(payload[key])

            schema[key].parent = self

        self.value = schema

    def __str__(self):
        prefix = '\t' * self.total_parents

        output = [
            f'<SchemaField({self.name}={{',
        ]

        value = self.computed_value

        if value is misc.NotSet:
            output.append(f'{prefix}\tNotSet')
            value = {}

        for key, value in value.items():
            output.append(f'{prefix}\t{key}: {value}')

        output.append(
            f'{prefix}}})>'
        )

        return '\n'.join(output)

    def __eq__(self, dct):
        if not hasattr(dct, 'items') or not hasattr(dct, 'keys'):
            raise exception.ReadValueError(
                "Unable to compare SchemaField with non dict-like object "
                "(missing implementation of .items() and .keys())"
            )

        local_keys = set([
            key for key, field in self.value.items()
            if field.computed_value is not misc.NotSet
        ])

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

    def keys(self):
        return self.value.keys()

    def values(self):
        return self.value.values()

    def items(self):
        return self.value.items()

    def __getitem__(self, key):
        if key not in self._computed_fields:
            raise exception.ReadValueError(f"Schema has no field {key}")

        return self.value[key]

    def as_json(self):
        if self.value is None:
            return None

        output = {}

        for key, field in self.value.items():
            if field.computed_value is misc.NotSet:
                continue

            output[key] = field.as_json()

        return output

    def as_python(self):
        if self.value is None:
            return None

        output = {}

        for key, field in self.value.items():
            if field.computed_value is misc.NotSet:
                continue

            output[key] = field.as_python()

        return output
