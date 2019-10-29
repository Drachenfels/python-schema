from python_schema import field


def test_case_one_simple_schema():
    class User(field.SchemaField):
        fields = [
            field.StrField('name'),
            field.StrField('last_name'),
            field.IntField('age'),
        ]

    user = User()

    # payload has fulfilled expectation of User, no errors expected
    user.loads({
        'name': 'John',
        'last_name': 'Doe',
        'age': '50',
    })

    assert user['name'] == 'John'
    assert user['last_name'] == 'Doe'

    # notice normalization of '50' into 50
    assert user['age'] == 50

    # we can also compare user to dictionary
    assert user == {
        'name': 'John',
        'last_name': 'Doe',
        # again '50' was normalised
        'age': 50,
    }

    # last thing we can do is convert user to normalised output

    # as either native python objects (in this case DateField would change into
    # datetime object)
    dct = user.as_python()

    assert dct['name'] == 'John'
    assert dct['last_name'] == 'Doe'
    assert dct['age'] == 50

    # or as json-compatible format that can be safely json.dumps any time later

    json_dct = user.as_json()

    assert json_dct['name'] == 'John'
    assert json_dct['last_name'] == 'Doe'
    assert json_dct['age'] == 50

    import json

    assert json.dumps(json_dct) == \
        '{"name": "John", "last_name": "Doe", "age": 50}'

    # there is third method of dumping normalised data `.dumps()` however it's
    # purpose is only to maintain symmetry between loads and dumps as json
    # module does

    dumps_dct = user.dumps()

    assert dumps_dct == json_dct
