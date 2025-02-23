# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

"""Peeler.

A tool to create or update a blender_manifest.toml from a pyproject.toml
"""

from pathlib import Path

from packaging.version import Version

DATA_DIR = Path(__file__).parent / "data"

MIN_UV_VERSION = Version("0.5.17")

MAX_UV_VERSION = Version((Path(__file__).parent.parent / ".max-uv-version").read_text())
