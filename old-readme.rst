Intro:

Agnostic schema that was inspired by many others, in other words, yet another
one. What makes it different? Paradgim. If you need something special then
extend and/or override, **python-schema** stays simple AND easy.

Feel free to take a look at other solution that I was trying and utlimately
have become inspiration for this library.


Examples

Project's principle is of TDD, click hyperlinks to see working and tested
examples.

NOTE: project uses pytest

::

    $ pip install pytest
    $ pytest


Basics - define, load, dump, access, validate [`tests/test_basics.py`_]
--------------------------------------------------------------------

.. _`tests/test_basics.py`: https://github.com/Drachenfels/python-schema/blob/master/tests/test_basics.py

.. code-block:: python

    from python_schema import field, exception

    schema = field.BaseField('boom')

    schema.loads('headshot')

    # dumps calls as_json on default, wanted to keep up with standard json
    # library
    data = schema.dumps()

    assert data == 'headshot'
    assert schema.name == 'boom'
    assert schema.value == 'headshot'
    assert schema.errors == []
    # this is example of non-json dump
    assert schema.as_dictionary() == 'headshot'
    # this is alias to schema.dumps
    assert schema.as_json() == 'headshot'


Validation
----------

Each field accepts validators, validators has to be a list of callables that
either return True (no error) or text message that explains nature of the
error.  Validators are executed in order provided and all validators are
executed once before ValidationError is raised. If this is undesirable,
validator can throw `exception.ValidationError` earlier to cause short circuit.
