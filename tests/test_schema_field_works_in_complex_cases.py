"""Checks if SchemaField and CollectionField can handle cases when it's
possible to introduce cycles.
"""

from python_schema import field


class Article(field.SchemaField):
    fields = [
        field.StrField('title'),
        field.StrField('content'),
    ]


class Newspaper(field.SchemaField):
    fields = [
        field.IntField('issue'),
        field.StrField('title'),
        field.CollectionField(
            'articles', Article
        )
    ]


def test_blogpost_has_an_author_and_authors_have_list_of_blogposts():
    """Inline schema is created on the fly.
    """
    payload = {
        'issue': 1,
        'title': 'OSes of the future',
        'articles': [{
            'title': 'Introduction',
            'content': 'Why we do exists and what will happen next',
        }, {
            'title': 'Linux - brief history',
            'content': 'Why we do exists and what will happen next',
        }]
    }

    issue = Newspaper()

    issue.loads(payload)

    assert issue == payload

    assert issue['articles'][0]['title'] == 'Introduction'
    assert issue['articles'][1]['title'] == 'Linux - brief history'
