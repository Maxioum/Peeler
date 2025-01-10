# Peeler


>A tool to use a `pyproject.toml` file instead (or alongside) of the `blender_manifest.toml` required for building blender add-ons since Blender 4.2 .

To install run:

```bash
pip install peeler
```

# Feature

Create a `blender_manifest.toml` from values in your `pyproject.toml`


```toml
# pyproject.toml

[project]
name = "my_awesome_addon"
version = "1.0.0"
```

Run peeler:

```bash
peeler manifest /path/to/your/pyproject.toml /path/to/blender_manifest.toml
```

Will create (or update) the `blender_manifest.toml`:

```toml
# blender_manifest.toml

name = "my_awesome_addon"
version = "1.0.0"
```

Some meta-data are specific to Blender, such as `blender_version_min`, you can specify theses in your `pyproject.toml` file under the `[tool.peeler.manifest]` table:

```toml
# pyproject.toml
[project]
name = "my_awesome_addon"
version = "1.0.0"

[tool.peeler.manifest]
blender_version_min = "4.2.0"
```

Will create:

```toml
# blender_manifest.toml

name = "my_awesome_addon"
version = "1.0.0"
blender_version_min = "4.2.0"
```


## Authors

<!-- markdownlint-disable MD013 -->

- **Maxime Letellier** - _Initial work_

<!-- markdownlint-enable MD013 -->
