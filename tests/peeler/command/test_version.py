import re

from pytest import CaptureFixture

from peeler.command.version import version_command

package_name_regex = f"peeler"

# from https://semver.org/spec/v2.0.0.html
version_regex = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"


def test_version_command(capfd: CaptureFixture) -> None:
    version_command()
    out, err = capfd.readouterr()

    assert re.match(f"^{package_name_regex} {version_regex}$", out)
