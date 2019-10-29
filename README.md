# python-schema

---
## Why would I use it?

If it happens that you are working on an API, RPC or simply work with functions
that accept complex data structures (trees and alike) common task is to have a
tool that verifies that all required fields are present, types are of expected
colour and finally there is consistent way to handle errors. Sometimes output
is complex and same is expected. Sometimes we just need to establish contract
how different libraries/modules/functions will communicate with each other.

Initially it was achieved usually by hand crafting validators on the fly as
projects were developed, then someone figured out that we can call them forms
and use for html/gui rendering as well, finally we all settled with schema's (
there is plenty of them). Where the most sane approach was taken to decouple
issue of normalisation and validation from anything else (to name a few: orm,
gui, leaking implementation to outside world).

This library belongs to the 3rd generation and by no means is revolutionary. It
just attempt to have the same but with no over-engineered parts. Code has to be
simple, easy to understand, but configurable just enough. Whenever developer
needs something extra, he can easily override or extend what was given to him.

---
## How to use it?

The python-schema consist of many fields like: IntField, StrField, BoolField,
FloatField, CollectionField, SchemaField, BaseField and etc.

Each field has two primary functions to load data (where normalisation and
validation happens) and to dump data (where conversion to either native python
or json-compatible format happens).

---
## Examples

> “Talk is cheap. Show me the code.” - Linus Torvald

One of the principles of python-schema is TDD, each case study will be
functional test copy-pasted from the test suite (that being said there is many
more tests than shown below).

### Case 1 - Simple Schema
see [Case #1] (https://www.example.com/)


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

---
## Premise of python-schema

Only essentials are part of library:

* from super simple to super complex schema
* required fields with support of inheritance and complex structures
* rudimentary validation but easy to expand
* minimum 3rd-party depdencies (currently none)
* accept json-like dictionary or python primitives on input (exclusively
  everything that could show up after json.dumps)
* output is either json-like dictionary or python native code (former
  guarantees json.dumps later oes not)
* if in doubt or need custom, code is simple, subclass python-schema and override/extend

What you do not have in library:

* ORM integration
* decorators
* meta classes
* module of badly formatted 600 lines of code with references as a way of populating objects
* magic
* methods that do some complex stuff
* integration with anything (unless working with json strings we call integration)
* bloat

---
## Flow of python schema

1. Each schema is a Field that may or may not have more fields
2. Each field loads content, that is:

    a. normalise

    b. validate

3. Each field dumps content, that is:

    a. return python-native (imaginary numbers, datetime objects)

    **or**

    a. return json compatible content (everything unknown to json.dumps converted to string)

4. Each field understands context, ie. when working with datetime, dumping will
   return date according to current user(s) timezone

---
## Don't like it, do you know anything better?

Of course! There is plenty that I used as inspiration (what to do) and warning
(what not to do):

* [JSON Schema (https://json-schema.org/)] (https://json-schema.org/)
* [Marshmallow (https://marshmallow.readthedocs.io/en/3.0/)] (https://marshmallow.readthedocs.io/en/3.0/)
* [WTForms (https://wtforms.readthedocs.io/en/stable/)] (https://wtforms.readthedocs.io/en/stable/)
* [Schema (https://pypi.org/project/schema/)] (https://pypi.org/project/schema/)

