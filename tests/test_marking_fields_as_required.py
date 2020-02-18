import pytest

from python_schema import field, exception


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


def test_we_can_mark_specific_field_on_schema_as_required():
    class SimpleUser(User):
        required = [
            'first_name',
            'last_name',
        ]

    instance = SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields[0] == 'first_name'
    assert required_fields[1] == 'last_name'

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'John',
        })

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'last_name': 'Doe',
        })

    instance.loads({
        'first_name': 'Jane',
        'last_name': 'Doe',
    })

    assert instance.value['first_name'] == 'Jane'
    assert instance.value['last_name'] == 'Doe'


def test_we_can_mark_sub_schema_as_required_without_specifying_any_field():
    """As long as something populates home_address it will work
    """
    class SimpleUser(User):
        required = [
            'home_address',
        ]

    instance = SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields[0] == 'home_address'

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'John',
        })

    instance.loads({
        'home_address': {
            'postcode': 'W1H 7EJ',
        },
    })

    instance.loads({
        'home_address': {
            'street_name': 'Hyde Park',
        },
    })

    instance.loads({
        'home_address': {
            'city': 'London',
        },
    })

    instance.loads({
        'home_address': {
            'postcode': 'W1H 7EJ',
            'street_name': 'Hyde Park',
            'city': 'London',
        },
    })

    assert instance.value['home_address'].value['postcode'] == 'W1H 7EJ'
    assert instance.value['home_address'].value['street_name'] == 'Hyde Park'
    assert instance.value['home_address'].value['city'] == 'London'


def test_we_can_mark_specific_field_on_sub_schema_as_required():
    """This test will check as well hybrid approach
    """
    class SimpleUser(User):
        required = [
            'home_address',
            'office_address.postcode',
        ]

    instance = SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields[0] == 'home_address'
    assert required_fields[1] == 'office_address.postcode'

    # missing home address and postcode on office address
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'John',
        })

    # missing postcode on office address
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'John',
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    # missing home address
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    # we have some field on home address, but postcode on office address is
    # missing
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
            'office_address': {
                'city': 'London',
            },
        })

    # this should work
    instance.loads({
        'home_address': {
            'city': 'London',
        },
        'office_address': {
            'postcode': 'W1H 7EJ',
        },
    })

    assert instance.value['home_address'].value['city'] == 'London'
    assert instance.value['office_address'].value['postcode'] == 'W1H 7EJ'


def test_we_can_mark_specific_field_on_two_sub_schema_as_required():
    """Test verifies if there are no clashes and etc.
    """
    class SimpleUser(User):
        required = [
            'home_address.postcode',
            'office_address.street_name',
        ]

    instance = SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields[0] == 'home_address.postcode'
    assert required_fields[1] == 'office_address.street_name'

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'home_addres': {
                'street_name': 'Hyde Park',
            },
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    # this should work
    instance.loads({
        'home_addres': {
            'postcode': 'W1H 7EJ',
        },
        'office_address': {
            'street_name': 'Hyde Park',
        },
    })

    assert instance.value['home_address'].value['postcode'] == 'W1H 7EJ'
    assert instance.value['office_address'].value['street_name'] == 'Hyde Park'


def test_we_can_mark_all_the_fields_required_but_not_subfields():
    """Wildcards mark all fields as required, but not on sub-fields
    """
    class SimpleUser(User):
        required = [
            '*',
        ]

    instance = SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields[0] == 'cookies_accepted_date'
    assert required_fields[1] == 'first_name'
    assert required_fields[2] == 'friends'
    assert required_fields[3] == 'home_address'
    assert required_fields[4] == 'last_name'
    assert required_fields[5] == 'office_address'

    # each of the .raises will have one field missing
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'Jane',
            'friends': [{
                'first_name': 'John',
                'last_name': 'Doe',
            }],
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
            'last_name': {
                'Doe',
            },
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'cookies_accepted_date': '2020-01-01',
            'friends': [{
                'first_name': 'John',
                'last_name': 'Doe',
            }],
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
            'last_name': {
                'Doe',
            },
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'cookies_accepted_date': '2020-01-01',
            'first_name': 'Jane',
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
            'last_name': {
                'Doe',
            },
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'cookies_accepted_date': '2020-01-01',
            'first_name': 'Jane',
            'friends': [{
                'first_name': 'John',
                'last_name': 'Doe',
            }],
            'last_name': {
                'Doe',
            },
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'cookies_accepted_date': '2020-01-01',
            'first_name': 'Jane',
            'friends': [{
                'first_name': 'John',
                'last_name': 'Doe',
            }],
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
            'office_address': {
                'postcode': 'W1H 7EJ',
            },
        })

    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'cookies_accepted_date': '2020-01-01',
            'first_name': 'Jane',
            'friends': [{
                'first_name': 'John',
                'last_name': 'Doe',
            }],
            'home_address': {
                'postcode': 'W1H 7EJ',
            },
            'last_name': {
                'Doe',
            },
        })

    # this should work
    instance.loads({
        'cookies_accepted_date': '2020-01-01',
        'first_name': 'Jane',
        'friends': [{
            'first_name': 'John',
            'last_name': 'Doe',
        }],
        'home_address': {
            'postcode': 'W1H 7EJ',
        },
        'last_name': {
            'Doe',
        },
        'office_address': {
            'postcode': 'W1H 7EJ',
        },
    })

    assert instance.value['cookies_accepted_date'] == '2020-01-01'
    assert instance.value['friends'][0] == {
        'first_name': 'John',
        'last_name': 'Doe',
    }
    assert instance.value['last_name'] == 'Doe'


def test_we_can_mark_all_the_fields_required_including_on_subfield():
    """Wildcards mark all fields required including subfields.

    Trick is that one of the fields is CollectionField that might be empty or
    not. If it's not empty then all the objects on it will be marked as
    required.
    """
    class SimpleUser(User):
        required = [
            '*.*',
        ]

    instance = SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields == [
        'cookies_accepted_date',
        'first_name',
        'friends.[].cookies_accepted_date',
        'friends.[].first_name',
        'friends.[].friends',
        'friends.[].home_address',
        'friends.[].home_address.city',
        'friends.[].home_address.postcode',
        'friends.[].home_address.street_name',
        'friends.[].last_name',
        'friends.[].office_address',
        'friends.[].office_address.city',
        'friends.[].office_address.postcode',
        'friends.[].office_address.street_name',
        'home_address.city',
        'home_address.postcode',
        'home_address.street_name',
        'office_address',
        'office_address.city',
        'office_address.postcode',
        'office_address.street_name',
    ]


def test_check_if_wildcard_wont_kill_by_infinite_recursion():
    class RecUser2(RecUser):
        required_fields = [
            '*.*',
        ]

    instance = RecUser2()

    required_fields = instance.get_required_fields()

    assert required_fields == [
        'best_friend',
        'best_friend.best_friend',
        'best_friend.first_name',
        'best_friend.last_name',
        'first_name',
        'last_name',
    ]

    # this should fail as we do not have best friend
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'Jane',
            'last_name': 'Doe',
            'best_friend': {
                'first_name': 'John',
                'last_name': 'Doe',
            },
        })

    # this should work
    instance.loads({
        'first_name': 'Jane',
        'last_name': 'Doe',
        'best_friend': {
            'first_name': 'John',
            'last_name': 'Doe',
            'best_friend': {
            },
        },
    })

    assert instance == {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'best_friend': {
            'first_name': 'John',
            'last_name': 'Doe',
            'best_friend': {
            },
        },
    }

    # this should fail as our best-friend has best-friend that does not have
    # best-friend
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'Jane',
            'last_name': 'Doe',
            'best_friend': {
                'first_name': 'John',
                'last_name': 'Doe',
                'best_friend': {
                    'first_name': 'Ashlyn',
                    'last_name': 'Poplar',
                },
            },
        })

    # this will work again
    instance.loads({
        'first_name': 'Jane',
        'last_name': 'Doe',
        'best_friend': {
            'first_name': 'John',
            'last_name': 'Doe',
            'best_friend': {
                'first_name': 'Ashlyn',
                'last_name': 'Poplar',
                'best_friend': {
                },
            },
        },
    })

    # this should fail again as leaf best-friend has no best-friend
    with pytest.raises(exception.RequiredFieldError):
        instance.loads({
            'first_name': 'Jane',
            'last_name': 'Doe',
            'best_friend': {
                'first_name': 'John',
                'last_name': 'Doe',
                'best_friend': {
                    'first_name': 'Ashlyn',
                    'last_name': 'Poplar',
                    'best_friend': {
                        'first_name': 'Commander',
                        'last_name': 'Shephard',
                    },
                },
            },
        })


# # BRAINSTORMNG PART
#     # any sub-field that has name postcode no matter how deep, for example
#     # if we have collection of addresses each of them will have postcode as
#     # required field
#     required = [
#         '*.postcode',
#     ]
#
#     # sub-field that has name postcode but only if parent is self
#     required = [
#         '>.postcode',
#     ]
#
#     # all sub-fields but only if parent is self
#     required = [
#         '>.*',
#     ]

# how to resolve requirements

# first collect all of them from the leafs
# go up branch, apply required, apply non-required
# go up branch, apply required, apply non-required
# rinse-repeat

# requirement is additive, thus requirments from leafs are added to parents
# and then to grand-parent, but each parent can override decision of
# children, if it's not enough we can use standard inheritance to make it
# more granular
