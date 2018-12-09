*************
python-schema
*************

Intro:
======

Agnostic schema that was inspired by many others, in other words, yet another
one. What makes it different? Paradgim. If you need something special then
extend and/or override, **python-schema** stays simple AND easy.

Feel free to take a look at other solution that I was trying and utlimately
have become inspiration for this library.

Schema (https://pypi.org/project/schema/)
-----------------------------------------

What I liked:

- simple

What I do not like:

- too simple, it makes code escalate quickly towards hard to comprehend structures
- not obvious to override functionality
- if python has classes why not to use them?

Marshmallow (https://marshmallow.readthedocs.io/en/3.0/)
--------------------------------------------------------

What I liked:

- capable
- easy to read
- classes

What I do not like:

- pre-processing, post-processing, methods
- agnostic yet integrates with orms
- metaclasses

JSON Schema (https://json-schema.org/)
--------------------------------------

What I liked:

- interdisciplinary
- easy to read

What I do not like:

- python implementations are not feature complete
- complex validation not yet supported (as of 2018-04-01)
- issue with inheritenace and marking field as required (or not) (as of 2018-04-01)

WTForms (https://wtforms.readthedocs.io/en/stable/)
---------------------------------------------------

What I liked:

- classes
- easy to read

What I do not like:

- it's forms, overkill for micro-services

What is python-schema then:
===========================

All above but trimmed down to essentials.

You have:

- schema
- required fields (which support inheritance and complex tree structures)
- validation (rudimentary, but extendable)
- it accepts only dictionaries on entry
- but outputs python code or json code
- if in doubt, override!

You do not have:

- decorators
- non-dictionaries
- magic methods that will do something
- integration with anything
- bloat

Premise
=======

    I. Each schema is a Field that may or may not have more fields.

    II. Each field behaves same way, that is:

        a. normalisation

        b. validation

        c. ready-to-use

    III. Schema loads data and dumps data using context (whatever it means, require your implementation)

    IV. Each schema can be converted back to dictionary (keeping some values closer to python ie imaginary numbers or date object) or json (enforcing casting to format json can understand - mostly strings for almost anything else than numbers)

    V. If you need more complex functionality you are expected to subclass python-schema

Examples
========

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
