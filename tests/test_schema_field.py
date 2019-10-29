"""Checks if SchemaField is usable.
"""

import pytest

from python_schema import field, exception


def test_inline_schema_works():
    """Inline schema is created on the fly.
    """
    schema = field.SchemaField('user', fields=[
        field.StrField('name'),
        field.StrField('last_name'),
        field.IntField('age'),
    ])

    schema.loads({
        'name': 'Frank',
        'last_name': 'Castle',
        'age': '35',
    })

    assert schema['name'] == 'Frank'
    assert schema['last_name'] == 'Castle'
    assert schema['age'] == 35

    assert schema == {
        'name': 'Frank',
        'last_name': 'Castle',
        'age': 35,
    }


def test_inline_schema_without_fields_does_not_work():
    schema = field.SchemaField('user')

    # inline schema that did not attach any fields should report unknown
    # fields

    with pytest.raises(exception.UnknownFieldError):
        schema.loads({
            'name': 'Frank',
            'last_name': 'Castle',
            'age': '35',
        })


def test_standalone_schema_works():
    """Standalone schema is just a class.
    """
    class User(field.SchemaField):
        fields = [
            field.StrField('name'),
            field.StrField('last_name'),
            field.IntField('age'),
        ]

    schema = User()

    schema.loads({
        'name': 'Frank',
        'last_name': 'Castle',
        'age': '42',
    })

    assert schema['name'] == 'Frank'
    assert schema['last_name'] == 'Castle'
    assert schema['age'] == 42

    assert schema == {
        'name': 'Frank',
        'last_name': 'Castle',
        'age': 42,
    }


def test_inheritance_works():
    """Inheritance should work on different schema.
    """
    class User(field.SchemaField):
        fields = [
            field.StrField('name'),
            field.StrField('last_name'),
            field.IntField('age'),
        ]

    class MarketableUser(User):
        fields = [
            field.StrField('postcode'),
        ]

    user = User()
    maraketable_user = MarketableUser()

    user.loads({
        'name': 'Frank',
        'last_name': 'Castle',
        'age': '36',
    })

    maraketable_user.loads({
        'name': 'John',
        'last_name': 'Doe',
        'age': '31',
        'postcode': 'W1',
    })

    assert user['name'] == 'Frank'
    assert user['last_name'] == 'Castle'
    assert user['age'] == 36

    assert user['name'] == 'Frank'
    assert user['last_name'] == 'Castle'
    assert user['age'] == 36

    with pytest.raises(exception.ReadValueError):
        user['postcode'] == 'W1'  # NOQA

    maraketable_user['name'] == 'John'  # NOQA
    maraketable_user['last_name'] == 'Doe'  # NOQA
    maraketable_user['age'] == 31  # NOQA
    maraketable_user['postcode'] == 'W1'  # NOQA

    with pytest.raises(exception.UnknownFieldError):
        user.loads({
            'name': 'Joe',
            'last_name': 'Doe',
            'age': 18,
            'postcode': 'EE1',
        })


def test_awkward_names_do_work():
    """Test that _some_value and __some_value will work.
    """
    class CosmicEntity(field.SchemaField):
        fields = (
            field.StrField('value'),
            field.StrField('_value'),
            field.StrField('__value'),

            field.IntField('errors'),
            field.IntField('_errors'),
            field.IntField('__errors'),
        )

    payload = {
        'value': 'some value',
        '_value': 'some _value',
        '__value': 'some __value',
        'errors': 1,
        '_errors': 2,
        '__errors': 3,
    }

    entity = CosmicEntity()
    entity.loads(payload)

    # accessing via getitem works always
    assert entity['value'] == 'some value'
    assert entity['_value'] == 'some _value'
    assert entity['__value'] == 'some __value'
    assert entity['errors'] == 1
    assert entity['_errors'] == 2
    assert entity['__errors'] == 3
