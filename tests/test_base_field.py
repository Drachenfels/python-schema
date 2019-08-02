"""Using BaseField load, dump, validate your data and handle errors.
"""

import json

import pytest

from python_schema import field, exception


def test_unitialised_schema_throws_exceptions():
    schema = field.BaseField('yellow')

    # those we can access always
    assert schema.parent is None
    assert schema.errors == []

    # value is accesible only after we call 'loads'
    with pytest.raises(exception.ReadValueError):
        assert schema.value == 'Yolo?'

    schema.loads('is the best colour')
    assert schema.value == 'is the best colour'


def test_load_data_to_a_field():
    """Load data to BaseField, check if we access it. Try with
    different data types.
    """
    schema = field.BaseField('boom')

    schema.loads('headshot')

    # dumps calls as_json on default, wanted to keep up with standard json
    # library
    data = schema.dumps()

    assert data == 'headshot'
    assert schema == 'headshot'
    assert schema.name == 'boom'
    assert schema.value == 'headshot'
    assert schema.errors == []
    # dump to python types
    assert schema.as_python() == 'headshot'
    # dump to json schema
    assert schema.as_json() == 'headshot'
    # this is basically the same
    assert schema.as_json() == schema.dumps()

    # we can reload schema as many times as we wish
    schema.loads(-1)

    data = schema.dumps()

    assert data == -1
    assert schema.name == 'boom'
    assert schema.value == -1
    assert schema.errors == []
    assert schema.as_python() == -1
    assert schema.as_json() == -1

    class SomeObjectThatJsonHasNoIdea():
        pass

    value = SomeObjectThatJsonHasNoIdea()

    schema.loads(value)

    data = schema.dumps()

    assert data == value
    assert schema.name == 'boom'
    assert schema.value == value
    assert schema.errors == []
    assert schema.as_python() == value

    # this will throw exception as json has no clue how to serialize
    # SomeObjectThatJsonHasNoIdea, method as_json is not doing by itself any
    # checks or castings to another type, it's merely information for a field
    # that if it knows how, it should return field that json can understand
    with pytest.raises(TypeError):
        json.dumps(schema.as_json())

    assert schema.as_json() == value


def test_we_can_add_validation_to_base_field():
    """Like test before, but this time we add custom validation to BaseField.
    """
    # basic idea is that each validator is either returning True (all good) or
    # text message (with what went wrong)
    schema = field.BaseField(
        'boom', validators=[
            lambda val: (
                True if val > 0 else
                f"Value has to be bigger than zero, {val} <= 0"
            )
        ])

    with pytest.raises(exception.ValidationError):
        schema.loads(-1)

    assert schema.errors == ['Value has to be bigger than zero, -1 <= 0']

    try:
        schema.loads(-1)
    except exception.ValidationError as err:
        assert schema.errors == ['Value has to be bigger than zero, -1 <= 0']
        assert str(err) == 'Validation error'


def test_we_may_or_may_not_disallow_none():
    """For some fields in schema None is fine, for others it's impossibility.
    Good example is boolean value where None can be interpreted as either False
    or not provided.
    """
    schema1 = field.BaseField('agree_to_cookies', allow_none=True)

    schema1.loads(None)

    assert schema1.value is None

    schema2 = field.BaseField('agree_to_cookies', allow_none=False)

    with pytest.raises(exception.NoneNotAllowedError):
        schema2.loads(None)


def test_we_may_set_description():
    """Some fields can be additionally annotated. Useful for debugging,
    automated doc generation and a like
    """
    schema = field.BaseField(
        'what_is_the_meaning_of_everything',
        description='The most common question in the universe')

    schema.loads(42)

    assert schema.value == 42
    assert schema.description == 'The most common question in the universe'


def test_that_we_can_set_useful_defaults_by_subclassing():
    class UsefulDefaultField(field.BaseField):
        description = 'This should be more useful than BaseField'
        allow_none = False

    field_one = UsefulDefaultField(name='useful_one')
    field_one.loads('Boom!')

    assert field_one.value == 'Boom!'
    assert field_one.name == 'useful_one'
    assert field_one.description == 'This should be more useful than BaseField'
    assert field_one.allow_none is False

    field_two = UsefulDefaultField(name='useful_two', description="Too long")
    field_two.loads('Headshot!')

    assert field_two.value == 'Headshot!'
    assert field_two.name == 'useful_two'
    assert field_two.description == 'Too long'
    assert field_two.allow_none is False
