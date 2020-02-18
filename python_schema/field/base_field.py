from python_schema import exception, misc


class BaseField:  # pylint: disable=too-many-instance-attributes
    # configuration of the object, those attributes can be set either on class
    # directly or as parameter of __init__
    description = ''
    validators = None
    allow_none = True
    default_value = misc.NotSet

    # state of the object, should not be altered manually in order to avoid
    # unexpected behaviour
    parent = None
    errors = None
    _value = misc.NotSet

    def __init__(
            self, name, description=None, validators=None, allow_none=None,
            default_value=misc.NotSet):
        """Short description of what all those arguments stand for:

            name :: the only mandatory field, it basically tells how the field
                in question should be called, also it tells a schema to look
                for this name in coming payload, used as well for error display
                and error code generation

            description :: human readable description of the field, used for
                auto generated doc and (in future) openapi (default: '')

            validators :: list of validators that should be applied, data prior
                to validation is normalised (for example boolean field converts
                0/1 to False/True) thus validators should be concerned with
                value but not type (default: [])

            allow_none :: if given field allows None as data, this can
                be handled via validator but for certain systems null values
                are impossibility or ambiguous (for boolean field None may mean
                False or that user didn't care to select answer)
                (default: True)

            default_value :: if field was provided with any value,
                default_value may be returned, is not set on default and will
                cause exception if attempted to use in such state
        """
        self.name = name

        self.validators = (
            ([] if self.validators is None else self.validators)
            if validators is None else validators
        )
        self.allow_none = (
            (True if self.allow_none is True else False)
            if allow_none is None else allow_none
        )
        self.description = (
            ('' if not self.description else self.description)
            if description is None else description
        )
        self.default_value = (
            self.default_value if default_value is misc.NotSet else
            default_value
        )

        # and this resets the state of the field
        self.reset_state()

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        try:
            value = self.value
        except exception.ReadValueError:
            value = 'NotSet'

        return (
            f'<{self.__class__.__name__}({self.name}={value})>'
        )

    def __repr__(self):
        return self.__str__()

    @property
    def total_parents(self):
        counter = 0

        parent = self.parent

        while parent is not None:
            parent = parent.parent
            counter += 1

        return counter

    def get_configuration_attributes(self):
        return [
            'name', 'description', 'validators', 'allow_none', 'default_value'
        ]

    def make_new(self):
        """Create new instance of same class.

        Each Filed of python_schema behaves like a factory object. We define
        field_type CollectionField or fields on SchemaField as instance of
        prototype with complete configuration. When new data is loaded to those
        fields (and possibly more in the future) we create new instance being
        complete replica of given base field but with new values assigned to
        them. This solves problem of object being shared between different
        instance of CollectionField or SchemaField.
        """
        new_kwargs = {
            name: getattr(self, name) for name in self.get_core_attributes()
        }

        return self.__class__(**new_kwargs)

    def reset_state(self):
        """Reset field to base state (before first `.loads`).
        """
        self.value = misc.NotSet
        self.errors = []
        self.parent = None

    def insist_not_none_or_none_allowed(self, value):
        if value is not None:
            return

        if self.allow_none is True:
            return

        raise exception.NoneNotAllowedError("None is not allowed value")

    def normalise(self, value):
        try:
            self.insist_not_none_or_none_allowed(value)
        except exception.NormalisationError as err:
            self.errors.append(str(err))

            raise

        return value

    def validate(self, value):
        for validate in self.validators:
            try:
                return_value = validate(value)

                if return_value is True:
                    continue

                self.errors.append(return_value)
            except exception.ValidationError as err:
                self.errors.append(str(err))

                raise exception.ValidationError('Validation error')

        if self.errors:
            raise exception.ValidationError('Validation error')

    def as_json(self):
        """Field returns value that can be json.dumped (ie datetime is
        converted to a string).

        Note: because BaseField is base class that has no specific
        implementation we may end up with very non-json representation when
        calling as_json. The reason is that BaseField don't have enough
        information with what sort of data it's working with and casting
        everything into string is not a solution.
        """
        return self.value

    def as_python(self):
        """Field returns python valid data (ie datetime stays as a datatime)
        """
        return self.value

    @property
    def is_set(self):
        return self._value is not misc.NotSet

    @property
    def is_default_value_set(self):
        return self.default_value is not misc.NotSet

    def get_final_value(self):
        """Method returns value that is either a) one that was set on object,
        b) default that was provided for the field, c) misc.NotSet.
        """
        if self.is_set:
            return self._value

        if self.is_default_value_set:
            return self.default_value

        return misc.NotSet

    @property
    def value(self):
        """Method throws an exception if no value nor default was provided for
        the field.
        """
        if self.is_set:
            return self._value

        if self.is_default_value_set:
            return self.default_value

        raise exception.ReadValueError(
            "Load field with data or provide default_value")

    @value.setter
    def value(self, value):
        self._value = value

    @value.deleter
    def value(self):
        self._value = misc.NotSet

    def loads(self, payload):
        self.reset_state()

        payload = self.normalise(payload)

        self.validate(payload)

        self.value = payload

    def dumps(self):
        return self.as_json()
