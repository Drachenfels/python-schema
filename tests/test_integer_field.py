"""Checks if IntegerField is usable.
"""

import pytest

from python_schema import field, exception


def test_field_loads_data():
    """Load data to IntegerField, check if we can access it. Try with different
    types on input (normalisation should kick in).
    """
    schema = field.IntField('meaning_of_everything', allow_none=True)

    class A:
        def __str__(self):
            return '6'

    values_to_check = [
        ('12', 12),
        (-1, -1),
        ('0', 0),
        (42, 42),
        (0, 0),
        (A(), 6),
        (None, None),
    ]

    for value_before, value_after in values_to_check:
        schema.loads(value_before)

        assert schema.name == 'meaning_of_everything'
        assert schema.value == value_after
        assert schema.errors == []
        assert schema.as_dictionary() == value_after
        assert schema.as_json() == value_after


def test_cases_when_normalisation_fails():
    """Test checks if normalisataion is not overcommiting itself.
    """
    schema = field.IntField('meaning_of_everything', allow_none=False)

    values_to_check = [
        'True',
        True,
        False,
        'hello',
        '12.3.4.5',
        13.4,
        '12.8',
    ]

    for value in values_to_check:
        with pytest.raises(exception.NormalisationError):
            schema.loads(value)

        assert schema.errors == \
            [f'IntField cannot be populated with value: {value}']

        try:
            schema.loads(value)
        except exception.NormalisationError as err:
            assert err.errors == \
                [f'IntField cannot be populated with value: {value}']

    with pytest.raises(exception.NormalisationError):
        schema.loads(None)

    try:
        schema.loads(None)
    except exception.NormalisationError as err:
        assert err.errors == [f'None is not allowed value']
