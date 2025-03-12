# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

"""Module for parsing, validating and updating a pyproject.toml file."""

from dep_logic.specifiers import RangeSpecifier
from packaging.version import Version

_BLENDER_SUPPORTED_PYTHON_VERSION = RangeSpecifier(
    Version("3.11"), Version("3.12"), include_min=True, include_max=False
)
