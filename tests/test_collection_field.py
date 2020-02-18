"""Checks if CollectionField is usable.
"""

import pytest

from python_schema import field, exception


def test_collection_of_strings_works():
    """Schema is Collection of StrFields, verify everything works as expected.
    """
    schema = field.CollectionField('list_of_pebbles', field.StrField('Pebble'))

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


def test_collection_requires_field_type_to_be_an_instance():
    """CollectionField requires that field_type is actually an instance and not
    a type.
    """
    with pytest.raises(exception.SchemaConfigurationError):
        field.CollectionField('list_of_pebbles', field.StrField)


def test_collection_of_strings_works_with_empty_payload():
    """Schema is Collection of StrFields, but we will populate it with empty
    content.
    """
    schema = field.CollectionField('list_of_pebbles', field.StrField('Pebble'))

    schema.loads(None)

    assert schema.name == 'list_of_pebbles'
    assert schema.as_python() is None
    assert schema.as_json() is None

    schema.loads([])

    assert schema.name == 'list_of_pebbles'
    assert schema.as_python() == []
    assert schema.as_json() == []
    # because payload was actually empty iterable, direct comparison would work
    # as well
    assert schema == []


def test_collection_of_integers_works_and_normalisation_will_kick_in():
    """Schema is Collection of IntFields, payload that we pass is normalised as
    expected. CollectionField itself checks whether value provided can be
    iterated over while IntField will check if specific value can be sensible
    cast to integer.
    """
    schema = field.CollectionField('list_of_primes', field.IntField('prime'))

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
        'list_of_anything', field.BaseField('something'))

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


def test_collection_accepts_only_between_2_and_5_elements():
    def number_of_elements(val, min_=2, max_=5):
        if len(val) < min_ or len(val) > max_:
            return (
                f"List has to be between {min_} and {max_} elements, "
                f"got {len(val)}"
            )

        return True

    schema = field.CollectionField(
        'short_list_of_numbers', field_type=field.IntField('number'),
        validators=[
            number_of_elements
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


def test_collection_accepts_only_even_numbers():
    def only_even_number(val):
        if val % 2:
            return f"Number is not even, got {val}"

        return True

    schema = field.CollectionField(
        'list_of_even_numbers', field_type=field.IntField(
            'numer', validators=[
                only_even_number
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


def test_collection_acepts_not_less_than_6_numbers_all_are_odd():
    """
    This tests verifies that validation is done in phases, only when phase one
    (validation of main collection) is success we progress to phase 2. This
    assumption is driven by the fact that while we may collection of max 5
    elements we definitely do not want to validate collection of 10k elements.
    """
    def only_even_number(val):
        if not val % 2:
            return f"Number is not odd, got {val}"

        return True

    def not_less_than_six(val):
        if len(val) < 6:
            return (
                f"List has to be at least 6 elements, got {len(val)} elements"
            )

        return True

    schema = field.CollectionField(
        'short_list_of_even_numbers',
        field_type=field.IntField(
            'individual_number', validators=[only_even_number]
        ),
        validators=[not_less_than_six]
    )

    # this is warm up and sanity check
    schema.loads([1, 3, 5, 7, 9, 11])

    assert schema.errors == []

    # this is too short, we should not get error about even numbers, as they
    # are checked in second phase of validation
    try:
        schema.loads([2, 4, 6, 8, 10])
    except exception.ValidationError as err:
        assert str(err) == 'Validation error'
        assert schema.errors == [
            'List has to be at least 6 elements, got 5 elements']

    # this is right on length, but one number is not odd
    try:
        schema.loads([1, 3, 4, 7, 9, 11])
    except exception.ValidationError as err:
        assert str(err) == "Validation error"
        assert schema.errors == [{
            2: ['Number is not odd, got 4'],
        }]

    # yet another sanity check
    schema.loads([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])

    assert schema.errors == []


def test_collection_cannot_be_none():
    schema = field.CollectionField(
        'list_of_emptyness', field.IntField('vacuum'), allow_none=False)

    with pytest.raises(exception.NormalisationError):
        schema.loads(None)

    try:
        schema.loads(None)
    except exception.NormalisationError as err:
        assert schema.errors == ['None is not allowed value']
        assert str(err) == 'None is not allowed value'


def test_collection_cannot_be_none_but_individual_elements_can():
    schema = field.CollectionField(
        'list_of_emptyness', field.IntField('vacuum'), allow_none=False)

    with pytest.raises(exception.NormalisationError):
        schema.loads(None)

    try:
        schema.loads(None)
    except exception.NormalisationError as err:
        assert schema.errors == ['None is not allowed value']
        assert str(err) == 'None is not allowed value'

    # this one will work
    schema.loads([None, None, None])

    assert len(schema.value) == 3
    assert schema == [None, None, None]


def test_collection_cannot_be_none_nor_indivual_elements():
    schema = field.CollectionField(
        'list_of_emptyness',
        field.IntField('hard_vacuum', allow_none=False), allow_none=False)

    with pytest.raises(exception.NormalisationError):
        schema.loads(None)

    try:
        schema.loads(None)
    except exception.NormalisationError as err:
        assert schema.errors == ['None is not allowed value']
        assert str(err) == 'None is not allowed value'


class CustomCollection(field.CollectionField):
    field_type = field.LazyField(
        'sub_collection', load='tests.test_collection_field.CustomCollection',
        field_type=field.BaseField('element'),
        validators=[
            lambda val: (
                'At least one element of any type' if len(val) < 1 else True
            )
        ]
    )


def test_collection_of_collections_with_at_least_one_value_each_works():
    master = CustomCollection('master_collection')

    class Yolo:
        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return self.name

        def __str__(self):
            return self.name

        def __eq__(self, other):
            return self.name == other.name

    # following use cases should work

    master.loads(None)

    assert master.name == 'master_collection'
    assert master.as_python() is None
    assert master.as_json() is None

    master.loads([])

    assert master.name == 'master_collection'
    assert master.as_python() == []
    assert master.as_json() == []

    master.loads([
        ['a', 'b'],
        [1],
        [Yolo('bird'), Yolo('cow')],
    ])

    assert master.name == 'master_collection'
    assert master.as_python() == [
        ['a', 'b'],
        [1],
        [Yolo('bird'), Yolo('cow')],
    ]

    master.loads([
        ['a'],
        [1],
        [None],
    ])

    assert master.name == 'master_collection'
    assert master.as_python() == [
        ['a'],
        [1],
        [None]
    ]

    # followin use cases should not work

    try:
        master.loads([
            [],
            [],
        ])
    except exception.ValidationError as err:
        assert str(err) == "Validation error"
        assert master.errors == [{
            0: ['At least one element of any type'],
            1: ['At least one element of any type'],
        }]

    try:
        master.loads([
            [1],
            ['a'],
            [],
            [Yolo('crocodile')],
        ])
    except exception.ValidationError as err:
        assert str(err) == "Validation error"
        assert master.errors == [{
            2: ['At least one element of any type'],
        }]
