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

from packaging.version import Version

DATA_DIR = Path(__file__).parent / "data"

MIN_UV_VERSION = Version("0.7.0")

MAX_UV_VERSION = Version((Path(__file__).parent.parent / ".max-uv-version").read_text())
