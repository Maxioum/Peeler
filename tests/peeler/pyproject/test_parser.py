import pytest

from peeler.pyproject.parse import Parser


@pytest.mark.parametrize("parser", [("pyproject.toml")], indirect=["parser"])
def test_parser(parser: Parser) -> None:
    assert parser.to_blender_manifest()
