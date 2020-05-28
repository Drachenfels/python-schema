from python_schema import field


class RecUser(field.SchemaField):
    fields = [
        field.StrField('first_name'),
        field.StrField('last_name'),
        field.LazyField(
            'best_friend', 'tests.test_marking_fields_as_required.RecUser'),
    ]


class Address(field.SchemaField):
    fields = [
        field.StrField('postcode'),
        field.StrField('city'),
        field.StrField('street_name'),
    ]


class User(field.SchemaField):
    fields = [
        field.StrField('first_name'),
        field.StrField('last_name'),
        Address('home_address'),
        Address('office_address'),
        field.CollectionField(
            'friends', field_type=field.LazyField(
                'friend',
                'tests.test_marking_fields_as_required.User'
            )
        ),
        field.StrField('cookies_accepted_date'),
    ]


class Person(field.SchemaField):
    fields = [
        field.StrField('first_name'),
        field.StrField('last_name'),
    ]

    required = [
        'first_name',
        'last_name',
    ]


class Pupil(Person):
    fields = [
        field.StrField('school_name'),
    ]

    required = [
        'school_name',
    ]


class Employee(Pupil):
    fields = [
        field.StrField('employer_name'),
    ]

    required = [
        'employer_name',
        '!school_name',
    ]
