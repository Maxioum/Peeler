# Peeler

## Getting Started

These instructions will get you a copy of the project on your
local machine for development and testing purposes.

Clone this repository in an empty directory

```bash
git clone https://github.com/Maxioum/peeler.git
```

### Project Management

This project is using [uv](https://docs.astral.sh/uv/) to manage dependencies
and to build the package.

See pyproject.toml files for the list of dependencies.

[How to install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Virtual Environments

You may create a virtual environnement managed by uv with

```bash
uv venv
```

make sure to activate the environnement

### Testing

```bash
uv run pytest .
```

## Coding style enforcement

### Pre-commit

[Pre-commit](https://pre-commit.com/) framework manages and maintains multi-language
pre-commit hooks.

To install hooks the first time, run

```bash
  uvx pre-commit install
```

After this step all your future commits will need to satisfy coding style rules.

### Ruff

[Ruff](https://docs.astral.sh/ruff/) is a Python linter and code formatter.

To manually run Ruff on your code

```bash
uvx ruff check
```

```bash
uvx ruff format
```

### Mypy

[Mypy](https://mypy-lang.org/) is a static type checker for Python.

These packages uses as much as possible python static typing feature and mypy helps
us to check our typing inconsistencies.

To manually run Mypy on your code

```bash
uv run mypy .
```

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of
conduct, and the process for submitting Pull Requests.

## Versioning

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Authors

<!-- markdownlint-disable MD013 -->

- **Maxime Letellier** - _Initial work_

<!-- markdownlint-enable MD013 -->
