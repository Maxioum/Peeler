from typing import List

from tomlkit import TOMLDocument
from tomlkit.items import AoT, AbstractTable, Array, Whitespace
from tomlkit.container import Container


def get_comments(document_or_table: TOMLDocument | Container | AoT) -> List[str]:
    """Retrieve comments from a `TOMLDocument` or a Array of table literal.

    :param document: the document
    :return: a list of comments
    """

    comments = []

    if isinstance(document_or_table, (Container, TOMLDocument)):
        items = [value for _, value in document_or_table.body]
    elif isinstance(document_or_table, AoT):
        items = [value for value in document_or_table.body]
    else:
        raise TypeError(f"Invalid document type: {type(document_or_table)}")

    for item in items:
        if isinstance(item, Whitespace):
            continue

        if comment := item.trivia.comment:
            comments.append(comment)

        if isinstance(item, AoT):
            comments.extend(get_comments(item))

        elif isinstance(item, AbstractTable):
            comments.extend(get_comments(item.value))

        elif isinstance(item, Array):
            for elem in item._value:
                if elem.value and not isinstance(elem.value, Whitespace):
                    if comment := elem.value.trivia.comment:
                        comments.append(comment)
                if elem.comment:
                    comments.append(elem.comment.trivia.comment)

    return comments
