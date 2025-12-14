# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

"""Peeler - Simplify Your Blender Add-on Packaging.

Usage: peeler [OPTIONS] COMMAND [ARGS]...

Run `peeler --help` for more info.

**Peeler Commands**:

`version:` print the currently installed `peeler` version.

`manifest:` create or update `blender_manifest.toml` from values in `pyproject.toml`.

`wheels:` download wheels and write paths to the `blender_manifest.toml`.
"""

from pathlib import Path

from dep_logic.specifiers import RangeSpecifier
from packaging.version import Version

DATA_DIR = Path(__file__).parent / "data"

_MIN_UV_VERSION = Version("0.7.0")

_MAX_UV_VERSION = Version("1")

UV_VERSION_RANGE = RangeSpecifier(
    min=_MIN_UV_VERSION, include_min=True, max=_MAX_UV_VERSION, include_max=False
)
