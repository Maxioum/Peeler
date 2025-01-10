# Contributing

When contributing to this repository, please first discuss the change you wish
to make via chat, email or other means with the owners of this
repository before making a change.

Please note we have a code of conduct, please follow it in all your
interactions with the project.

## Pull request Process

See [first-contribution](https://github.com/firstcontributions/first-contributions)

- Fork this repository
- Clone the repository see [Getting Started](#getting-started)
- Make necessary changes and commit those changes.
- Update the [CHANGELOG.md](CHANGELOG.md) with details of changes. The changelog scheme we use is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
- If needed, increase the version numbers in pyproject.toml and CHANGELOG.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
- Wait until the success of the CICD pipeline
- Make sure your branch is rebased onto the destination branch.
- You may request the reviewer to merge it for you.


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

See the [pyproject.toml](pyproject.toml) file for the list of dependencies.

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


## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of
experience, nationality, personal appearance, race, religion, or sexual identity
and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

- The use of sexualized language or imagery and unwelcome sexual attention or
  advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information, such as a physical or electronic
  address, without explicit permission
- Other conduct which could reasonably be considered inappropriate in a
  professional setting

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

### Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team. All complaints will be reviewed and
investigated and will result in a response that is deemed necessary and
appropriate to the circumstances. The project team is obligated to maintain
confidentiality with regard to the reporter of an incident. Further details of
specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/),
version 2.1, available at <https://www.contributor-covenant.org/version/2/1/code_of_conduct>
