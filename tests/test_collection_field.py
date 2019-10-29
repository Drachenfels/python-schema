"""Checks if CollectionField is usable.
"""

import pytest

from python_schema import field, exception


def test_collection_of_str_fields_works():
    """Schema is Collection of StrFields, verify everything works as expected.
    """
    schema = field.CollectionField('list_of_pebbles', field.StrField)

    values_to_check = [
        (['a', 'b', 'c'], ['a', 'b', 'c']),
        ([1, 2, 3], ['1', '2', '3']),
    ]

    for value_before, value_after in values_to_check:
        schema.loads(value_before)

        assert schema.name == 'list_of_pebbles'
        assert len(schema.value) == 3
        assert schema.errors == []
        assert schema.as_json() == value_after
        assert schema.as_python() == value_after


def test_collection_of_str_fields_works_with_empty_payload():
    """Schema is Collection of StrFields, but we will populate it with empty
    content.
    """
    schema = field.CollectionField('list_of_pebbles', field.StrField)

    schema.loads(None)

    assert schema.name == 'list_of_pebbles'
    assert schema.as_python() is None
    assert schema.as_json() is None

    schema.loads([])

    assert schema.name == 'list_of_pebbles'
    assert schema.as_python() == []
    assert schema.as_json() == []


def test_collection_of_int_fields_works_with_normalisation():
    """Schema is Collection of IntFields, payload that we pass is normalised as
    expected.
    """
    schema = field.CollectionField(
        'list_of_primes', field.IntField)

    class AnObject:
        def __str__(self):
            return '13'

    values_to_check = [
        ([2, 3, 5, 7, 11, 13], [2, 3, 5, 7, 11, 13]),
        ([2, '3', 5, '7', 11, AnObject()], [2, 3, 5, 7, 11, 13]),

    ]

    for value_before, value_after in values_to_check:
        schema.loads(value_before)

        assert schema.name == 'list_of_primes'
        assert len(schema.value) == 6
        assert schema.errors == []
        assert schema.as_python() == value_after
        assert schema.as_json() == value_after


def test_collection_of_anything_works():
    """Schema is Collection of BaseFields (any value is expected), verify
    everything works as expected.
    """
    schema = field.CollectionField(
        'list_of_anything', field.BaseField)

    class AnObject:
        def __str__(self):
            return '13'

    instance = AnObject()

    values_to_check = [
        ([2, '3', 4, 'hello', None, instance],
         [2, '3', 4, 'hello', None, instance]),

    ]

    for value_before, value_after in values_to_check:
        schema.loads(value_before)

        assert schema.name == 'list_of_anything'
        assert schema.errors == []
        assert schema.as_python() == value_after
        assert schema.as_json() == value_after


def test_error_handling_works_on_main_collection_field_part_1():
    """Collection is the first field that may have a validation error on itself
    (for example only 5 elements max) and on the value that collection has (for
    example only even numbers). Tests are split same way.

    This verifies validation on collection works.
    """
    schema = field.CollectionField(
        'short_list_of_numbers', type_=field.IntField, validators=[
            lambda val: (
                True if 1 < len(val) < 6 else
                f"List has to be between 2 and 5 elements, got {len(val)}"
            )
        ]
    )

    schema.loads([2, 4, 6])

    assert schema.errors == []

    try:
        schema.loads([2, ])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [
            'List has to be between 2 and 5 elements, got 1']

    try:
        schema.loads([2, 4, 6, 8, 10, 12, 14])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [
            'List has to be between 2 and 5 elements, got 7']


def test_error_handling_works_on_content_of_collection_part_2():
    """Collection is the first field that may have a validation error on itself
    (for example only 5 elements max) and on the value that collection has (for
    example only even numbers). Tests are split same way.

    This verifies validation on individual elements works.
    """
    schema = field.CollectionField(
        'list_of_even_numbers', type_=field.IntField(
            'individual_number', validators=[
                lambda val: (
                    f"Number is not even, got {val}" if val % 2 else True
                )
            ]
        )
    )

    try:
        schema.loads([4, 5, 8])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [{
            1: [
                'Number is not even, got 5',
            ]
        }]

    try:
        schema.loads([2, 3, 4, 5, 6])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [{
            1: [
                'Number is not even, got 3',
            ],
            3: [
                'Number is not even, got 5',
            ],
        }]


def test_error_handling_works_on_content_of_collection_part_3():
    """Collection is the first field that may have a validation error on itself
    (for example only 5 elements max) and on the value that collection has (for
    example only even numbers). Tests are split same way.

    This tests verifies that validation is done in phases, only when phase one
    (validation of main collection) is success we progress to phase 2. This
    assumption is driven by the fact that while we may collection of max 5
    elements we definitely do not want to validate collection of 10k elements.
    """
    schema = field.CollectionField(
        'short_list_of_even_numbers',
        type_=field.IntField(
            'individual_number', validators=[
                lambda val: (
                    f"Number is not even, got {val}" if val % 2 else True
                )
            ]
        ),
        validators=[
            lambda val: (
                True if 1 < len(val) < 6 else
                f"List has to be between 2 and 5 elements, got {len(val)}"
            )
        ]
    )

    # this is warm up and sanity check
    schema.loads([2, 4, 6])

    assert schema.errors == []

    # this is too short, we should not care about number being even
    try:
        schema.loads([3, ])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [
            'List has to be between 2 and 5 elements, got 1']

    # this is too long, we should not care about number being even
    try:
        schema.loads([2, 3, 5, 7, 9, 10, 12, 14])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [
            'List has to be between 2 and 5 elements, got 8']

    # this is right on length, but one number is not even
    try:
        schema.loads([2, 5, 10])
    except exception.ValidationError as err:
        assert str(err) == "Validation error"
        assert schema.errors == [{
            1: ['Number is not even, got 5'],
        }]

    # this one is right on spot
    schema.loads([2, 6, 12])

    assert schema.errors == []


def test_cases_when_we_do_not_allow_nones():
    schema = field.CollectionField(
        'list_of_emptyness', field.IntField, allow_none=False)

    with pytest.raises(exception.NormalisationError):
        schema.loads(None)

    try:
        schema.loads(None)
    except exception.NormalisationError as err:
        assert schema.errors == ['None is not allowed value']
        assert str(err) == 'None is not allowed value'


def test_collection_of_same_collection_works():
    even_numbers_collection = field.CollectionField(
        'even_numbers',
        type_=field.IntField(
            'individual_number', validators=[
                lambda val: (
                    f"Number is not even, got {val}" if val % 2 else True
                )
            ]
        ),
        validators=[
            lambda val: (
                True if len(val) > 1 else
                f"List has to be at least 2 elements long, got {len(val)}"
            )
        ],
    )

    master_collection = field.CollectionField(
        'series_of_even_numbers',
        type_=even_numbers_collection
    )

    master_collection.loads([
        [2, 4, 6],
        [12, 18, 22]
    ])

    assert master_collection.dumps() == [
        [2, 4, 6],
        [12, 18, 22]
    ]

    # check if validation is working as expected

    with pytest.raises(exception.ValidationError):
        master_collection.loads([
            [2, 4],
            [2, 5, 6],
            [6, 12],
        ])

    with pytest.raises(exception.ValidationError):
        master_collection.loads([
            [2,],
        ])
