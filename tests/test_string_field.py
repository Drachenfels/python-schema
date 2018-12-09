"""Checks if StrField is usable.
"""

import pytest

from python_schema import field, exception


def test_field_loads_data():
    """Load data to StrField, check if we can access it. Try with different
    types on input (normalisation should kick in).
    """
    schema = field.StrField('meaning_of_everything', allow_none=True)

    class AnObject:
        def __str__(self):
            return '42'

    values_to_check = [
        ('42', '42'),
        (42, '42'),
        ('Hello', 'Hello'),
        ('True', 'True'),
        (True, 'True'),
        (AnObject(), '42'),
        (None, None),
    ]

    for value_before, value_after in values_to_check:
        schema.loads(value_before)

        assert schema.name == 'meaning_of_everything'
        assert schema.value == value_after
        assert schema.errors == []
        assert schema.as_dictionary() == value_after
        assert schema.as_json() == value_after


def test_cases_when_normalisation_works_but_effects_are_awkward():
    """Test checks if normalisation is not overcommitting itself.
    """
    schema = field.StrField('meaning_of_everything', allow_none=False)

    class AnObject:
        pass

    instance = AnObject()

    values_to_check = [
        (instance, str(instance)),
        (AnObject, str(AnObject)),
        ({}, '{}'),
        ([], '[]'),
    ]

    for value_before, value_after in values_to_check:
        schema.loads(value_before)

        assert schema.name == 'meaning_of_everything'
        assert schema.value == value_after
        assert schema.errors == []
        assert schema.as_dictionary() == value_after
        assert schema.as_json() == value_after


def test_cases_when_we_do_not_allow_nones():
    schema = field.StrField('meaning_of_everything', allow_none=False)

    with pytest.raises(exception.NormalisationError):
        schema.loads(None)

    try:
        schema.loads(None)
    except exception.NormalisationError as err:
        assert err.errors == [f'None is not allowed value']
