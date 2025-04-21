# Peeler – Simplify Your Blender Add-on Packaging

>This package is under active development. Feel free to ask for help [here](https://github.com/Maxioum) or open an issue [here](https://github.com/Maxioum/Peeler/issues/new).
I’ll be happy to develop the feature you need. :smile:


A tool to easily package your **Blender add-on**

Building and installing a Blender add-on with dependencies requires **manually** downloading the necessary wheels and specifying their paths in `blender_manifest.toml`. Peeler automates this process, allowing you to package your Blender add-on without **manually handling dependencies** (and their own dependencies !) or **manually writing their paths** in `blender_manifest.toml`.

Since Blender 4.2, add-ons must use `blender_manifest.toml` instead of the standard `pyproject.toml` used in Python projects. **Peeler** lets you use `pyproject.toml` instead (or alongside) to simplify dependency management and streamline your workflow.

# Installation

[uv](https://docs.astral.sh/uv/) is required to use the [Wheels](#wheels) feature.

## If you don't have uv installed

Either [install uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```bash
pip install peeler
```

Or install uv and peeler at the same time:

```bash
pip install peeler[uv]
```

## If you are already a uv user

**Peeler** does not need to be added to your project dependencies - you can use Peeler directly as a tool:

```bash
uvx peeler [OPTIONS] COMMAND [ARGS]
```

Or install **Peeler** without uv:

```bash
uv pip install peeler
```

# Features

>Each feature can be used independently.

[Manifest](#Manifest):
Generate the `blender_manifest.toml` from fields in a `pyproject.toml`.

[Wheels](#Wheels):
Download the required **wheels** for packaging your add-on based on the dependencies specified in your `pyproject.toml`, automatically write their paths to `blender_manifest.toml`.

## Manifest

Generate the `blender_manifest.toml` from fields in a `pyproject.toml`.

### 1. Ensure your `pyproject.toml` contains basic field values

```toml
# pyproject.toml

[project]
name = "My Awesome Add on"
version = "1.0.0"
requires-python = "==3.11.*"
```

### 2. Some metadata are specific to **Blender**

For instance `blender_version_min`, you can specify these metadata in your `pyproject.toml` file under the `[tool.peeler.manifest]` table
Here's a minimal working version:

```toml
# pyproject.toml

[project]
name = "My Awesome Add on"
version = "1.0.0"
requires-python = "==3.11.*"

[tool.peeler.manifest]
blender_version_min = "4.2.0"
id = "my_awesome_add_on"
license = ["SPDX:0BSD"]
maintainer = "John Smith"
tagline = "My Add-on is awesome"
```

### 3. Run Peeler to create (or update) your `blender_manifest.toml`

```bash
peeler manifest /path/to/your/pyproject.toml /path/to/blender_manifest.toml
```

```toml
# Generated blender_manifest.toml

version = "1.0.0"
name = "My Awesome Add on"
schema_version = "1.0.0"
type = "add-on"
blender_version_min = "4.2.0"
id = "my_awesome_add_on"
license = ["SPDX:0BSD"]
maintainer = "John Smith"
tagline = "My Add-on is awesome"
```

The manifest is populated with values from your `pyproject.toml` `[project]` and `[tool.peeler.manifest]` tables, along with default values.

For a full list of required and optional values in a `blender_manifest.toml` visit [Blender Documentation](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#manifest)

### 4. Build your add-on

If your add-on has dependencies make sure to use the [Wheels](#wheels) feature below.

Then to build your add-on use the [regular Blender command](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#command-line):

```bash
blender --command extension build
```

Hint: Ensure Blender is [added to your `PATH`](https://docs.blender.org/manual/en/4.4/advanced/command_line/launch/)

## Wheels

Download the required **wheels** for packaging your add-on based on the dependencies specified in your `pyproject.toml`, automatically write their paths to `blender_manifest.toml`.

### 1. In your `pyproject.toml`, specify your dependencies

```toml
# pyproject.toml

[project]
name = "My Awesome Add-on"
version = "1.0.0"
requires-python = "==3.11.*"

# For instance rich and Pillow (the popular image manipulation module)

dependencies = [
    "Pillow==11.1.0",
    "rich>=13.9.4",
]

```

### 2. Run peeler wheels to download the wheels for **all platforms**

```bash
peeler wheels ./pyproject.toml ./blender_manifest.toml
```

**Peeler** updates your `blender_manifest.toml` with the downloaded wheels paths.

```toml
# Updated blender_manifest.toml

version = "1.0.0"
name = "My Awesome Add on"
schema_version = "1.0.0"
type = "add-on"
blender_version_min = "4.2.0"

# The wheels as a list of paths
wheels = [
    # Pillow wheels for all platforms
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

    # Wheels for rich and its dependencies
    "./wheels/rich-13.9.4-py3-none-any.whl",
    "./wheels/markdown_it_py-3.0.0-py3-none-any.whl",
    "./wheels/mdurl-0.1.2-py3-none-any.whl",
    "./wheels/pygments-2.18.0-py3-none-any.whl"
]

```

Note that the **dependencies of the dependencies** (and so on) specified in `pyproject.toml` are also downloaded, ensuring everything is packaged correctly. Pretty neat, right?

```bash
# Pillow and rich dependency tree resolved from
# dependencies = [
#    "Pillow==11.1.0",
#    "rich>=13.9.4",
# ]

My Awesome Add on v1.0.0
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
