# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-2.0-or-later

"""Peeler.

A tool to create or update a blender_manifest.toml from a pyproject.toml
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
