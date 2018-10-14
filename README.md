# python-schema

## Intro:

Agnostic schema that was inspired by many other schemas (yes, another one). What makes it different? Simple AND easy.

## Tour among others:

Schema (https://pypi.org/project/schema/)

Pros:

    - simple & robust

Cons:

    - due to simplicity it escalates quickly towards hard to comprehend structures
    - not obvious to override functionality
    - if we have classes why not to use them? 

Marshmallow (https://marshmallow.readthedocs.io/en/3.0/)

Pros:

    - capable
    - easy to read (up certain point)

Cons:

    - pre-processing, post-processing, methods
    - integration with orms
    - not obvious how to override functionality

JSON Schema (https://json-schema.org/)

Pros:

    - interdisciplinary
    - easy to read

Cons:

    - python implementations are not feature complete
    - complex validation not yet supported (as of 2018-04-01)


WTForms (https://wtforms.readthedocs.io/en/stable/)

Pros:

    - feature complete
    - classes

Cons:

    - it's about forms and we do not need it

## What is python-schema then:

Above but trimmed down. 

You can define:

    - schema
    - required fields
    - validation (rudimentary, but extendable)
    - class 
    - you give it and get back dictionaries

You cannot:

    - built-in decorators
    - talk non-dictionaries 
    - define methods that will do something
    - expect that whatever you write will be interpreted by anything

## Examples

1. Simple stays simple

Schema:


```
    from python_schema import field

    class UberSimpleSchema(field.BaseField):
        pass
```

Anything can be passed as long as it's single value, for example:
