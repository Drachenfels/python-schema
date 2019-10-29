"""Checks if SchemaField is usable.
"""

import pytest

from python_schema import field, exception


def test_simple_standalone_schema_works():
    """Standalone schema is just a class.
    """
    class User(field.SchemaField):
        fields = [
            field.StrField('first_name'),
            field.StrField('last_name'),
        ]

    schema = User()

    schema.loads({
        'first_name': 'Frank',
        'last_name': 'Castle',
    })

    assert schema['first_name'] == 'Frank'
    assert schema['last_name'] == 'Castle'

    assert schema == {
        'first_name': 'Frank',
        'last_name': 'Castle',
    }


def test_schema_behaves_like_a_dictionary():
    class User(field.SchemaField):
        fields = [
            field.StrField('first_name'),
            field.StrField('last_name'),
        ]

    schema = User()

    schema.loads({
        'first_name': 'Frank',
        'last_name': 'Castle',
    })

    for key in schema:
        assert key in ['first_name', 'last_name']

    for key in schema.keys():
        assert key in ['first_name', 'last_name']

    for value in schema.values():
        assert value in ['Frank', 'Castle']

    for key, value in schema.items():
        assert key in ['first_name', 'last_name']
        assert value in ['Frank', 'Castle']


def test_we_can_skip_one_field_on_load():
    class User(field.SchemaField):
        fields = [
            field.StrField('first_name'),
            field.StrField('last_name'),
        ]

    schema = User()

    schema.loads({
        'first_name': 'Frank',
    })

    assert schema['first_name'] == 'Frank'

    assert schema == {
        'first_name': 'Frank',
    }

    assert schema.as_python() == {
        'first_name': 'Frank',
    }

    assert schema.as_json() == {
        'first_name': 'Frank',
    }


def test_we_can_add_more_fields_on_loads():
    class User(field.SchemaField):
        exception_on_unknown = False

        fields = [
            field.StrField('first_name'),
            field.StrField('last_name'),
        ]

    schema = User()

    schema.loads({
        'first_name': 'Frank',
        'last_name': 'Castle',
        'age': '40',
    })

    assert schema['first_name'] == 'Frank'
    assert schema['last_name'] == 'Castle'

    assert schema == {
        'first_name': 'Frank',
        'last_name': 'Castle',
    }

    class User2(field.SchemaField):
        exception_on_unknown = True

        fields = [
            field.StrField('first_name'),
            field.StrField('last_name'),
        ]

    schema = User2()

    with pytest.raises(exception.UnknownFieldError):
        schema.loads({
            'first_name': 'Frank',
            'last_name': 'Castle',
            'age': '40',
        })


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

    with pytest.raises(exception.UnknownFieldError):
        schema.loads({
            'name': 'Frank',
            'last_name': 'Castle',
            'age': '35',
        })


def test_inline_schema_without_fields_work_when_unknowns_are_accepted():
    schema = field.SchemaField('user', exception_on_unknown=False)

    schema.loads({
        'name': 'Frank',
        'last_name': 'Castle',
        'age': '35',
    })

    assert schema == {}


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


def test_schema_can_keep_collection_of_other_schema_field():
    class Article(field.SchemaField):
        fields = [
            field.StrField('title'),
            field.StrField('content'),
        ]

    class Newspaper(field.SchemaField):
        fields = [
            field.IntField('issue'),
            field.StrField('title'),
            field.CollectionField('articles', Article),
        ]

    payload = {
        'issue': 1,
        'title': 'OSes of the future',
        'articles': [{
            'title': 'Introduction',
            'content': 'Why we do exists and what will happen next',
        }, {
            'title': 'Linux - brief history',
            'content': 'Why we do exists and what will happen next',
        }]
    }

    issue = Newspaper()

    issue.loads(payload)

    assert issue == payload

    assert issue['articles'][0]['title'] == 'Introduction'
    assert issue['articles'][1]['title'] == 'Linux - brief history'
