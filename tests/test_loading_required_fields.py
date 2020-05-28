import pytest

from python_schema import field, exception

from tests.fixtures import models


def test_we_can_mark_specific_field_on_schema_as_required():
    instance = models.SimpleUser()

    required_fields = instance.get_required_fields()

    assert required_fields[0] == 'first_name'
    assert required_fields[1] == 'last_name'

    # with pytest.raises(exception.RequiredFieldError) as err:
    #     instance.loads({
    #         'first_name': 'John',
    #     })
    #
    # assert (
    #     'One or more required field is missing: last_name' == str(err.value))
    #
    # with pytest.raises(exception.RequiredFieldError) as err:
    #     instance.loads({
    #         'last_name': 'Doe',
    #     })
    #
    # assert (
    #     'One or more required field is missing: first_name' == str(err.value))
    #
    # instance.loads({
    #     'first_name': 'Jane',
    #     'last_name': 'Doe',
    # })
    #
    # assert instance.value['first_name'] == 'Jane'
    # assert instance.value['last_name'] == 'Doe'
