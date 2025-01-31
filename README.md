# Peeler


>A tool to use a `pyproject.toml` file instead (or alongside) of the `blender_manifest.toml` required for building blender add-ons since Blender 4.2 .

To install run:

```bash
pip install peeler
```

# Feature

Create a `blender_manifest.toml` from values in your `pyproject.toml`

## How to

- Make sure to have a `pyproject.toml` with basic field values:

```toml
# pyproject.toml

[project]
name = "My Awesome Addon"
version = "1.0.0"
```

- Some meta-data are specific to Blender, such as `blender_version_min`, you can specify theses in your `pyproject.toml` file under the `[tool.peeler.manifest]` table, here's a minimal `pyproject.toml` working version:

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
tagline = "A short description"
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
tagline = "A short description"
```


## Authors

<!-- markdownlint-disable MD013 -->

- **Maxime Letellier** - _Initial work_

<!-- markdownlint-enable MD013 -->
