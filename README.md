# Peeler


>Use a `pyproject.toml` file instead (or alongside) of the `blender_manifest.toml` required for building blender add-ons since Blender 4.2 .

>Easily package a **blender add-on** without having to **manually** download dependencies `wheels` (and dependencies of dependencies !) and **manually** write theirs paths to `blender_manifest.toml` .


# Installation

[uv](https://docs.astral.sh/uv/) is needed to use the [Wheels](#wheels) feature

## If you don't have uv installed

Either [install uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```bash
pip install peeler
```

Or install uv and peeler at once:

```bash
pip install peeler[uv]
```

## If you're already a uv user

Peeler doesn't need to be added in your project dependencies, meaning you can use directly peeler as a tool:

```bash
uvx peeler [OPTIONS] COMMAND [ARGS]
```

Or install peeler without uv:

```bash
pip install peeler
```

# Features

## Manifest

Create a `blender_manifest.toml` from fields in a `pyproject.toml`


- Make sure to have a `pyproject.toml` with basic field values:

```toml
# pyproject.toml

[project]
name = "My Awesome Addon"
version = "1.0.0"
```

- Some meta-data are specific to **Blender**, such as `blender_version_min`, you can specify theses in your `pyproject.toml` file under the `[tool.peeler.manifest]` table, here's a minimal `pyproject.toml` working version:

```toml
# pyproject.toml

[project]
name = "My Awesome Addon"
version = "1.0.0"

[tool.peeler.manifest]
blender_version_min = "4.2.0"
id = "my_awesome_addon"
license = ["SPDX:0BSD"]
maintainer = "John Smith"
tagline = "My Add-on is awesome"
```

- Run peeler to create (or update) `blender_manifest.toml`:


```bash
peeler manifest /path/to/your/pyproject.toml /path/to/blender_manifest.toml
```

```toml
# created blender_manifest.toml

version = "1.0.0"
name = "My Awesome Addon"
schema_version = "1.0.0"
type = "add-on"
blender_version_min = "4.2.0"
id = "my_awesome_addon"
license = ["SPDX:0BSD"]
maintainer = "John Smith"
tagline = "My Add-on is awesome"
```

The manifest is filled with values from the **pyproject** `[project]`, `[tool.peeler.manifest]` tables and default values.

To get a full list of values required or optional in a `blender_manifest.toml` visit https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#manifest


## Wheels

Download the **wheels** needed to package your add-on using dependencies specified in your `pyproject.toml`, and write their paths to `blender_manifest.toml`

- In your `pyproject.toml` specify your dependencies:

```toml
# pyproject.toml

[project]
name = "My Awesome Addon"
version = "1.0.0"
requires-python = "==3.11"

# For instance rich and Pillow (the popular image manipulation module)

dependencies = [
    "Pillow==11.1.0",
    "rich>=13.9.4",
]

```

- Run peeler to downloads the wheels for **all platforms**:


```bash
peeler wheels ./pyproject.toml ./blender_manifest.toml
```

Your `blender_manifest.toml` will be updated with the downloaded wheels paths

```toml
# updated blender_manifest.toml

version = "1.0.0"
name = "My Awesome Addon"
schema_version = "1.0.0"
type = "add-on"
blender_version_min = "4.2.0"

# the wheels as a list of paths
wheels = [
    # pillow wheels for all platforms
    "./wheels/pillow-11.1.0-cp311-cp311-macosx_10_10_x86_64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-macosx_11_0_arm64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-manylinux_2_28_aarch64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-manylinux_2_28_x86_64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-musllinux_1_2_aarch64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-musllinux_1_2_x86_64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-win32.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-win_amd64.whl",
    "./wheels/pillow-11.1.0-cp311-cp311-win_arm64.whl",

    # wheels for rich and its dependencies
    "./wheels/rich-13.9.4-py3-none-any.whl",
    "./wheels/markdown_it_py-3.0.0-py3-none-any.whl",
    "./wheels/mdurl-0.1.2-py3-none-any.whl",
    "./wheels/pygments-2.18.0-py3-none-any.whl"
]

```

Note that the **dependencies of the dependencies** of the specified in `pyproject.toml` are also downloaded, neat !

```bash
# pillow and rich dependency tree resolved from
# dependencies = [
#    "Pillow==11.1.0",
#    "rich>=13.9.4",
# ]

My Awesome Addon v1.0.0
├── pillow v11.1.0
├── rich v13.9.4
│   ├── markdown-it-py v3.0.0
│   │   └── mdurl v0.1.2
│   └── pygments v2.18.0
```

# Authors

<!-- markdownlint-disable MD013 -->

- **Maxime Letellier** - _Initial work_

<!-- markdownlint-enable MD013 -->
