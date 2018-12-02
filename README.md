# python-schema

## Intro:

Agnostic schema that was inspired by many other schemas (yes, another one).
What makes it different? Simple AND easy.

## Tour among others:

Schema (https://pypi.org/project/schema/)

Pros:

    - simple & robust

Cons:

    - due too simplicity it escalates quickly towards hard to comprehend
      structures
    - not obvious to override functionality
    - if python has classes why not to use them?

Marshmallow (https://marshmallow.readthedocs.io/en/3.0/)

Pros:

    - capable
    - easy to read (up to certain point)

Cons:

    - pre-processing, post-processing, methods
    - integration with orms
    - metaclasses

JSON Schema (https://json-schema.org/)

Pros:

    - interdisciplinary
    - easy to read

Cons:

    - python implementations are not feature complete
    - complex validation not yet supported (as of 2018-04-01)
    - issue with inheritenace and marking field as required (or not) (as of
      2018-04-01)

WTForms (https://wtforms.readthedocs.io/en/stable/)

Pros:

    - feature complete
    - classes

Cons:

    - it's about forms and we do not need it

## What is python-schema then:

Above but trimmed down to essentials.

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

## Premise

    I. Each schema is a Field that may or may not have more fields.

    II. Each field behaves same way, that is:

        a. normalisation

        b. validation

        c. ready-to-use

    III. Schema loads data using context (whatever it is for you) and dumps
        data using context (again whatever it could be for you)

    IV. Each schema can be converted back to dictionary (keeping some values
        closer to python ie imaginary numbers or date object) or json
        (enforcing casting to format json can understand)

    V. If you need more complex functionality you are expected to subclass
        python-schema

## Examples

Project's principle is of TDD, click hyperlinks to see working and tested
examples.

Side note. We use pytest, so `pip install pytest` and then just type
`pytest`.

    A. Basics - define, load, dump, access, validate [tests/test_basics.py]
