from typing import List
from pytest import mark

from tomlkit import TOMLDocument
from tomlkit.items import Comment

from peeler.toml_utils import get_comments


@mark.parametrize(
    ("toml_document", "comments"),
    [
        (
            "simple.toml",
            [],
        ),
        (
            "simple_with_comments.toml",
            [
                "# first",
                "# inline 1",
                "# in array",
                "# middle",
                "# under",
                "# inline 2",
                "# in array 2",
                "# object_in_array",
                "# inline 3",
                "# inline 4",
                "# end",
            ],
        ),
    ],
    indirect=["toml_document"],
)
def test_get_comments(toml_document: TOMLDocument, comments: List[Comment]) -> None:
    assert get_comments(toml_document) == comments
