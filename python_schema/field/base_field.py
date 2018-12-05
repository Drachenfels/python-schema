from python_schema import misc, exception


class BaseField:
    def __init__(
            self, name, description='', validators=None, allow_none=True,
            default=None, parent=None):
        """Short description of what all those arguments stand for:

            name :: the only mandatory field, it basically tells how the field
                in question should be called, also it tells a schema to look
                for this name in coming payload, used as well for error display
                and error code generation

            description :: human readable description of the field, used for
                auto generated doc (default: '')

            validators :: list of validators that should be applied, data prior
                to validation is normalised (for example boolean field converts
                0/1 to False/True) thus validators should be concerned with
                value but not type (default: [])

            allow_none :: if given field allows None as data, this can
                be handled via validator but for certain systems null values
                are impossibility or amigbous (for boolean field None may mean
                False or that user didn't care to select answer)
                (default: True)

            default :: if field was not required and not provided, default
                value is being returned on dump (default: None)

            parent :: if object is part of bigger tree we can set a parent to
                it - most of the time is set automatically by python-schema
                (default: None)
        """
        self.name = name
        self.validators = [] if validators is None else validators
        self.allow_none = allow_none

        self.description = description
        self.parent = None if parent is None else parent

        self.default = default

    def is_set(self):
        return getattr(self.value, 'is_set', True)

    def reset(self):
        """Reset field to base state.
        """
        self.value = misc.ValueNotSet()
        self.errors = []

    def insist_not_empty_or_allowed_empty(self, value):
        if value is not None:
            return

        if self.allow_none is True:
            return

        raise exception.NoneNotAllowedError("None is not allowed value")

    def normalise(self, value):
        """BaseField accepts all values as-is
        """
        try:
            self.insist_not_empty_or_allowed_empty(value)
        except exception.NormalisationError as err:
            self.errors.append(str(err))

            raise

        return value

    def as_json(self):
        """Field should return json valid value.
        """
        if self.is_set():
            return self.value

        return self.default

    def as_dictionary(self):
        if self.is_set():
            return self.value

        return self.default

    def validate(self, value):
        for validate in self.validators:
            return_value = validate(value)

            if return_value is True:
                continue

            self.errors.append(return_value)

    def loads(self, value):
        self.reset()

        value = self.normalise(value)

        self.validate(value)

        if self.errors:
            raise exception.ValidationError(errors=self.errors)

        self.value = value

    def dumps(self):
        return self.as_json()

    # def make_new(self, parent):
    #     return self.__class__(
    #         name=self.name, description=self.description,
    #         validators=self.validators, allow_blank=self.allow_blank,
    #         parent=parent)
    #
    # def populate(self, value):
    #     self.confirm_argument_is_of_expected_shape(value)
    #
    #     self.data = None if value is None else self.normalise(value)
    #
    # def get_canonical_string(self):
    #     ancestors = []
    #     parent = self.parent
    #
    #     while parent:
    #         ancestors.insert(0, parent.name)
    #
    #         parent = parent.parent
    #
    #     ancestors.append(self.name)
    #
    #     return '.'.join(ancestors)
