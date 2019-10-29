from python_schema import field


class Address(field.SchemaField):
    fields = [
        field.StrField('postcode'),
        field.StrField('street'),
    ]


class BusinessAddress(Address):
    fields = [
        field.StrField('letterbox'),
    ]


class Book(field.SchemaField):
    fields = [
        field.StrField('title'),
        field.SchemaField(
            'author', 'tests.test_schema_field_can_survive_cycles.Author'),
    ]


class Author(field.SchemaField):
    fields = [
        field.StrField('name'),
        field.CollectionField(
            'books',
            field.SchemaField(
                'book', 'tests.test_schema_field_can_survive_cycles.Book'),
        ),
        field.SchemaField('home_address', Address),
        field.SchemaField('secret_address', Address()),
        field.SchemaField(
            'office_address',
            'tests.test_schema_field_can_survive_cycles.BusinessAddress'),
        BusinessAddress('publisher_address'),
    ]


def test_blogpost_has_an_author_and_authors_have_list_of_blogposts():
    payload = {
        'title': 'Chapter I',
        'author': {
            'name': 'drachenfels',
            'books': [{
                'title': 'Chapter I',
            }, {
                'title': 'Chapter II',
            }, {
                'title': 'Chapter III',
            }, {
                'title': 'Chapter IV',
            }],
            'home_address': {
                'postcode': 'aaa1',
                'street': 'st. James',
            },
            'office_address': {
                'postcode': 'bbb1',
                'street': 'st. John',
            },
            'secret_address': {
                'postcode': 'MMMM1',
                'street': 'st. Bruno',
            },
            'publisher_address': {
                'postcode': 'ccc1',
                'street': 'st. George',
            },
        },
    }

    book = Book()

    book.loads(payload)

    assert book == payload

    assert book['title'] == 'Chapter I'
    assert book['author']['name'] == 'drachenfels'
    assert len(book['author']['books']) == 4

    assert book['author']['home_address']['postcode'] == 'aaa1'
    assert book['author']['office_address']['postcode'] == 'bbb1'
    assert book['author']['publisher_address']['postcode'] == 'ccc1'
    assert book['author']['secret_address']['postcode'] == 'MMMM1'
