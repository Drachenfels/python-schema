"""Checks if SchemaField is usable.
"""

import pytest

from python_schema import field, exception


def test_we_can_access_all_the_fields_on_class_and_its_ancestors():
    """Simple case is that SchemaField is a dictionary of various values
    """
    class Human(field.SchemaField):
        fields = [
            field.IntField('age'),
            field.StrField('name'),
        ]

    class Teenager(Human):
        fields = [
            field.StrField('hobby'),
        ]

    class Pupil(Human):
        fields = [
            field.StrField('school'),
        ]

    class SuperHero(Pupil, Teenager):
        fields = [
            field.StrField('superpower'),
        ]

    instance = SuperHero()

    fields = instance.get_all_fields()

    assert fields['name'].name == 'name'
    assert fields['age'].name == 'age'
    assert fields['hobby'].name == 'hobby'
    assert fields['school'].name == 'school'
    assert fields['superpower'].name == 'superpower'


# class Address(field.SchemaField):
#     fields = [
#         field.StrField('postcode'),
#         field.StrField('street'),
#     ]
#
#
# class BusinessAddress(Address):
#     fields = [
#         field.StrField('letterbox'),
#     ]
#
#
# class Book(field.SchemaField):
#     fields = [
#         field.StrField('title'),
#         field.SchemaField(
#             'author', 'tests.test_schema_field_can_survive_cycles.Author'),
#     ]
#
#
# class Author(field.SchemaField):
#     fields = {
#         'name': (field.StrField, {'validators': ['yolo1', 'yolo2']}),
#     }
#     # fields = [
#     #     field.StrField('name'),
#     #     field.CollectionField(
#     #         'books',
#     #         field.SchemaField(
#     #             'book', 'tests.test_schema_field_can_survive_cycles.Book'),
#     #     ),
#     #     field.SchemaField('home_address', Address),
#     #     field.SchemaField('secret_address', Address()),
#     #     field.SchemaField(
#     #         'office_address',
#     #         'tests.test_schema_field_can_survive_cycles.BusinessAddress'),
#     #     BusinessAddress('publisher_address'),
#     # ]


# class User2(field.SchemaField):
#     fields = [
#         field.StrField('username'),
#         field.StrField('password'),
#         field.CollectionField(
#             'friends', field.LazyField('tests.test_schema_field.User')
#         )
#     ]


# def test_typical_schema_usage():
#     """Simple case is that SchemaField is a dictionary of various values
#     """
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('username'),
#             field.StrField('password'),
#             field.IntField('number_of_posts')
#         ]
#
#     instance = User()
#
#     instance.loads({
#         'username': 'Drachenfels',
#         'password': 'secretpassword',
#         'number_of_posts': '13',
#     })
#
#     assert instance.fields['username'] == 'Drachenfels'
#     assert instance.fields['password'] == 'secretpassword'
#     assert instance.fields['number_of_posts'] == 13
#
#
# def test_if_we_can_keep_track_friends():
#     """User has name and friends, friends objects themselves are of class User.
#     """
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('name'),
#             field.CollectionField('friends', type_=field.LazyField('User')),
#         ]
#
#     instance = User()
#
#     instance.loads({
#         'name': 'John',
#         'friends': [{
#             'name': 'Emma',
#             'friends': [{
#                 'name': 'John',
#             }, {
#                 'name': 'Emily',
#             }, {
#                 'name': 'Dan',
#             }]
#         }],
#     })


# def test_binary_tree_like_structure():
#     """Test will try to build a tree in form of
#
#                20
#             /      \
#            15      29
#           /  \    /  \
#          7   17 24   34
#     """
#     class Node(field.SchemaField):
#         fields = [
#             field.StrField('value'),
#             field.LazyField('left', 'Node'),
#             field.LazyField('right', 'Node'),
#         ]
#
#     root = Node()
#
#     root.loads({
#         'value': '1',
#         'left': {
#             'value': 15,
#             'left': {
#                 'value': 7,
#             },
#             'right': {
#                 'value': 17,
#             },
#         },
#         'right': {
#             'value': 29,
#             'left': {
#                 'value': 24,
#             },
#             'right': {
#                 'value': 34,
#             },
#         }
#     })
#
#     assert root.fields['value'] == 1
#
#     assert root.fields['left'].fields['value'] == 15
#     assert root.fields['left'].fields['left'].fields['value'] == 7
#     assert root.fields['left'].fields['right'].fields['value'] == 17
#
#     assert root.fields['right'].fields['value'] == 29
#     assert root.fields['right'].fields['left'].fields['value'] == 24
#     assert root.fields['right'].fields['right'].fields['value'] == 34


# def test_case_one_simple_schema():
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('name'),
#             field.StrField('last_name'),
#             field.IntField('age'),
#         ]
#
#     user = User()
#
#     # payload has fulfilled expectation of User, no errors expected
#     user.loads({
#         'name': 'John',
#         'last_name': 'Doe',
#         'age': '50',
#     })
#
#     assert user['name'] == 'John'
#     assert user['last_name'] == 'Doe'
#
#     # notice normalization of '50' into 50
#     assert user['age'] == 50
#
#     # we can also compare user to dictionary
#     assert user == {
#         'name': 'John',
#         'last_name': 'Doe',
#         # again '50' was normalised
#         'age': 50,
#     }
#
#     # last thing we can do is convert user to normalised output
#
#     # as either native python objects (in this case DateField would change into
#     # datetime object)
#     dct = user.as_python()
#
#     assert dct['name'] == 'John'
#     assert dct['last_name'] == 'Doe'
#     assert dct['age'] == 50
#
#     # or as json-compatible format that can be safely json.dumps any time later
#
#     json_dct = user.as_json()
#
#     assert json_dct['name'] == 'John'
#     assert json_dct['last_name'] == 'Doe'
#     assert json_dct['age'] == 50
#
#     import json
#
#     assert json.dumps(json_dct) == \
#         '{"name": "John", "last_name": "Doe", "age": 50}'
#
#     # there is third method of dumping normalised data `.dumps()` however it's
#     # purpose is only to maintain symmetry between loads and dumps as json
#     # module does
#
#     dumps_dct = user.dumps()
#
#     assert dumps_dct == json_dct


# def test_simple_standalone_schema_works():
#     """Standalone schema is just a class.
#     """
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('first_name'),
#             field.StrField('last_name'),
#         ]
#
#     schema = User()
#
#     schema.loads({
#         'first_name': 'Frank',
#         'last_name': 'Castle',
#     })
#
#     assert schema['first_name'] == 'Frank'
#     assert schema['last_name'] == 'Castle'
#
#     assert schema == {
#         'first_name': 'Frank',
#         'last_name': 'Castle',
#     }
#
#
# def test_schema_behaves_like_a_dictionary():
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('first_name'),
#             field.StrField('last_name'),
#         ]
#
#     schema = User()
#
#     schema.loads({
#         'first_name': 'Frank',
#         'last_name': 'Castle',
#     })
#
#     for key in schema:
#         assert key in ['first_name', 'last_name']
#
#     for key in schema.keys():
#         assert key in ['first_name', 'last_name']
#
#     for value in schema.values():
#         assert value in ['Frank', 'Castle']
#
#     for key, value in schema.items():
#         assert key in ['first_name', 'last_name']
#         assert value in ['Frank', 'Castle']
#
#
# def test_we_can_skip_one_field_on_load():
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('first_name'),
#             field.StrField('last_name'),
#         ]
#
#     schema = User()
#
#     schema.loads({
#         'first_name': 'Frank',
#     })
#
#     assert schema['first_name'] == 'Frank'
#
#     assert schema == {
#         'first_name': 'Frank',
#     }
#
#     assert schema.as_python() == {
#         'first_name': 'Frank',
#     }
#
#     assert schema.as_json() == {
#         'first_name': 'Frank',
#     }
#
#
# def test_we_can_add_more_fields_on_loads():
#     class User(field.SchemaField):
#         exception_on_unknown = False
#
#         fields = [
#             field.StrField('first_name'),
#             field.StrField('last_name'),
#         ]
#
#     schema = User()
#
#     schema.loads({
#         'first_name': 'Frank',
#         'last_name': 'Castle',
#         'age': '40',
#     })
#
#     assert schema['first_name'] == 'Frank'
#     assert schema['last_name'] == 'Castle'
#
#     assert schema == {
#         'first_name': 'Frank',
#         'last_name': 'Castle',
#     }
#
#     class User2(field.SchemaField):
#         exception_on_unknown = True
#
#         fields = [
#             field.StrField('first_name'),
#             field.StrField('last_name'),
#         ]
#
#     schema = User2()
#
#     with pytest.raises(exception.UnknownFieldError):
#         schema.loads({
#             'first_name': 'Frank',
#             'last_name': 'Castle',
#             'age': '40',
#         })
#
#
# def test_inline_schema_works():
#     """Inline schema is created on the fly.
#     """
#     schema = field.SchemaField('user', fields=[
#         field.StrField('name'),
#         field.StrField('last_name'),
#         field.IntField('age'),
#     ])
#
#     schema.loads({
#         'name': 'Frank',
#         'last_name': 'Castle',
#         'age': '35',
#     })
#
#     assert schema['name'] == 'Frank'
#     assert schema['last_name'] == 'Castle'
#     assert schema['age'] == 35
#
#     assert schema == {
#         'name': 'Frank',
#         'last_name': 'Castle',
#         'age': 35,
#     }
#
#
# def test_inline_schema_without_fields_does_not_work():
#     schema = field.SchemaField('user')
#
#     with pytest.raises(exception.UnknownFieldError):
#         schema.loads({
#             'name': 'Frank',
#             'last_name': 'Castle',
#             'age': '35',
#         })
#
#
# def test_inline_schema_without_fields_work_when_unknowns_are_accepted():
#     schema = field.SchemaField('user', exception_on_unknown=False)
#
#     schema.loads({
#         'name': 'Frank',
#         'last_name': 'Castle',
#         'age': '35',
#     })
#
#     assert schema == {}
#
#
# def test_inheritance_works():
#     """Inheritance should work on different schema.
#     """
#     class User(field.SchemaField):
#         fields = [
#             field.StrField('name'),
#             field.StrField('last_name'),
#             field.IntField('age'),
#         ]
#
#     class MarketableUser(User):
#         fields = [
#             field.StrField('postcode'),
#         ]
#
#     user = User()
#     maraketable_user = MarketableUser()
#
#     user.loads({
#         'name': 'Frank',
#         'last_name': 'Castle',
#         'age': '36',
#     })
#
#     maraketable_user.loads({
#         'name': 'John',
#         'last_name': 'Doe',
#         'age': '31',
#         'postcode': 'W1',
#     })
#
#     assert user['name'] == 'Frank'
#     assert user['last_name'] == 'Castle'
#     assert user['age'] == 36
#
#     assert user['name'] == 'Frank'
#     assert user['last_name'] == 'Castle'
#     assert user['age'] == 36
#
#     with pytest.raises(exception.ReadValueError):
#         user['postcode'] == 'W1'  # NOQA
#
#     maraketable_user['name'] == 'John'  # NOQA
#     maraketable_user['last_name'] == 'Doe'  # NOQA
#     maraketable_user['age'] == 31  # NOQA
#     maraketable_user['postcode'] == 'W1'  # NOQA
#
#     with pytest.raises(exception.UnknownFieldError):
#         user.loads({
#             'name': 'Joe',
#             'last_name': 'Doe',
#             'age': 18,
#             'postcode': 'EE1',
#         })
#
#
# def test_awkward_names_do_work():
#     """Test that _some_value and __some_value will work.
#     """
#     class CosmicEntity(field.SchemaField):
#         fields = (
#             field.StrField('value'),
#             field.StrField('_value'),
#             field.StrField('__value'),
#
#             field.IntField('errors'),
#             field.IntField('_errors'),
#             field.IntField('__errors'),
#         )
#
#     payload = {
#         'value': 'some value',
#         '_value': 'some _value',
#         '__value': 'some __value',
#         'errors': 1,
#         '_errors': 2,
#         '__errors': 3,
#     }
#
#     entity = CosmicEntity()
#     entity.loads(payload)
#
#     # accessing via getitem works always
#     assert entity['value'] == 'some value'
#     assert entity['_value'] == 'some _value'
#     assert entity['__value'] == 'some __value'
#     assert entity['errors'] == 1
#     assert entity['_errors'] == 2
#     assert entity['__errors'] == 3
#
#
# def test_schema_can_keep_collection_of_other_schema_field():
#     class Article(field.SchemaField):
#         fields = [
#             field.StrField('title'),
#             field.StrField('content'),
#         ]
#
#     class Newspaper(field.SchemaField):
#         fields = [
#             field.IntField('issue'),
#             field.StrField('title'),
#             field.CollectionField('articles', Article),
#         ]
#
#     payload = {
#         'issue': 1,
#         'title': 'OSes of the future',
#         'articles': [{
#             'title': 'Introduction',
#             'content': 'Why we do exists and what will happen next',
#         }, {
#             'title': 'Linux - brief history',
#             'content': 'Why we do exists and what will happen next',
#         }]
#     }
#
#     issue = Newspaper()
#
#     issue.loads(payload)
#
#     assert issue == payload
#
#     assert issue['articles'][0]['title'] == 'Introduction'
#     assert issue['articles'][1]['title'] == 'Linux - brief history'
#
#
# def test_blogpost_has_an_author_and_authors_have_list_of_blogposts():
#     payload = {
#         'title': 'Chapter I',
#         'author': {
#             'name': 'drachenfels',
#             'books': [{
#                 'title': 'Chapter I',
#             }, {
#                 'title': 'Chapter II',
#             }, {
#                 'title': 'Chapter III',
#             }, {
#                 'title': 'Chapter IV',
#             }],
#             'home_address': {
#                 'postcode': 'aaa1',
#                 'street': 'st. James',
#             },
#             'office_address': {
#                 'postcode': 'bbb1',
#                 'street': 'st. John',
#             },
#             'secret_address': {
#                 'postcode': 'MMMM1',
#                 'street': 'st. Bruno',
#             },
#             'publisher_address': {
#                 'postcode': 'ccc1',
#                 'street': 'st. George',
#             },
#         },
#     }
#
#     book = Book()
#
#     book.loads(payload)
#
#     assert book == payload
#
#     assert book['title'] == 'Chapter I'
#     assert book['author']['name'] == 'drachenfels'
#     assert len(book['author']['books']) == 4
#
#     assert book['author']['home_address']['postcode'] == 'aaa1'
#     assert book['author']['office_address']['postcode'] == 'bbb1'
#     assert book['author']['publisher_address']['postcode'] == 'ccc1'
#     assert book['author']['secret_address']['postcode'] == 'MMMM1'
