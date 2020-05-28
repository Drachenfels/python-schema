from python_schema import exception, misc

from .base_field import BaseField


class SchemaField(BaseField):
    # throw exception if loads receives unexpected key, otherwise ignore
    # silently
    exception_on_unknown = True

    # list of fields that this schema defines
    fields = None

    # list of required fields, if any
    required = None

    def __init__(
            self, name=None, exception_on_unknown=None, required=None,
            **kwargs):
        """Initialises new instance of the Schema.

        name - name that should override default in form of __class__.__name__
        """
        name = name if name else self.__class__.__name__

        super().__init__(name, **kwargs)

        if self.fields is None:
            self.fields = []

        self.exception_on_unknown = (
            (True if self.exception_on_unknown is True else False)
            if exception_on_unknown is None else exception_on_unknown
        )

        self.required = (
            ([] if self.required is None else self.required)
            if required is None else required
        )

    def normalise(self, value):
        value = super().normalise(value)

        if value is None:
            return value

        if self.exception_on_unknown:
            unknown_keys = set(value.keys()).difference(
                set(self.get_all_fields().keys()))

            if unknown_keys:
                message = "Unexpected payload with key(s): {}".format(
                    ', '.join(unknown_keys))

                self.errors.append(message)

                raise exception.UnknownFieldError(message)

        return value

    def get_configuration_attributes(self):
        return super().get_configuration_attributes() + [
            'exception_on_unknown', 'required']

    def get_required_fields(self):
        ancestor_required = []

        for ancestor in self.__class__.mro()[1:-1]:
            _required = getattr(ancestor, 'required', None)

            required = _required if _required else []

            for name in required:  # NOQA
                ancestor_required.append(name)

        my_required = self.required

        all_required = []

        for name in my_required:
            all_required.append(name)

        return all_required + ancestor_required

    def validate_required_fields(self, payload):
        if not self.required:
            return

        req_fields = [elm.split('.')[0] for elm in self.required]

        payload_fields = [] if payload is None else list(payload.keys())

        not_provided = list(set(req_fields).difference(set(payload_fields)))

        not_provided.sort()

        if not_provided:
            raise exception.RequiredFieldError(
                "One or more required field is missing: {}".format(
                    ", ".join(not_provided)
                )
            )

    def get_all_fields(self):
        """Returns all the fields that this class and it's super-class(es).

        Using mro we combine 'fields' from every object instead being forced to
        defined get_all_fields on each of sub-classes and calling super.

        Compare:

        class A:
            fields = ['a', 'b']

        class B(A):
            fields = ['c']

        vs (incomlete example)

        class A:
            def get_all_fields(self):
                return ['a', 'b']

        class B(A):
            def get_all_felds(self):
                return super().get_all_felds() + ['c']
        """
        all_fields = {}

        for ancestor in self.__class__.mro()[:-1]:
            _fields = getattr(ancestor, 'fields', None)

            fields = _fields if _fields else []

            for field in fields:  # NOQA
                if isinstance(field, type):
                    raise exception.SchemaConfigurationError(
                        f"Field {field} at {self.name}(SchemaField) is not "
                        "an instance"
                    )

                all_fields[field.name] = field

        for field in self.fields:
            if isinstance(field, type):
                raise exception.SchemaConfigurationError(
                    f"Field {field} at {self.name}(SchemaField) is not "
                    "an instance"
                )

            all_fields[field.name] = field

        return all_fields

    def loads(self, payload):
        self.reset_state()

        payload = self.normalise(payload)

        self.validate(payload)

        self.validate_required_fields(payload)

        if payload is None:
            self.value = None

            return

        values = {}

        for key, field in self.get_all_fields().items():
            if key not in payload:
                continue

            values[key] = field.make_new(parent=self)
            values[key].loads(payload[key])

        self.value = values

    def __str__(self):
        prefix = '\t' * self.total_parents

        output = [
            f'<SchemaField({self.name}={{',
        ]

        value = self.get_final_value()

        if value is misc.NotSet:
            output.append(f'{prefix}\tNotSet')
            value = {}

        for key, val in value.items():
            output.append(f'{prefix}\t{key}: {val}')

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

        local_keys = {
            key for key, field in self.value.items()
            if field.get_final_value() is not misc.NotSet
        }

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
        if key not in self.value:
            raise exception.ReadValueError(f"Schema has no field {key}")

        return self.value[key]

    def _get_non_empty_fields(self):
        if self.value is None:
            return None

        return [
            (key, field) for key, field in self.value.items()
            if field.get_final_value() is not misc.NotSet
        ]

    def as_json(self):
        fields = self._get_non_empty_fields()

        if fields is None:
            return None

        return {
            key: field.as_json() for key, field in fields
        }

    def as_python(self):
        fields = self._get_non_empty_fields()

        if fields is None:
            return None

        return {
            key: field.as_python() for key, field in fields
        }
