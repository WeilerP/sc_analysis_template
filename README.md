# Single-cell analysis template repository

This repository acts as a template notebook for the analysis of single-cell data and methods; the corresponding Jupyter Book is rendered [here](https://weilerp.github.io/sc_analysis_template/).

You can check out the [CellRank 2](https://github.com/theislab/cellrank2_reproducibility) and [CellRank protocol](https://github.com/theislab/cellrank_protocol) reproducibility repositories for example repositories following the same outline as this template, built off an earlier version of this template repo.

## Setup

1. Rename `src/fancypackage/`.
2. Update `pyproject.toml` to include the correct information
    - Project name
    - Project description
    - Project-specific Python requirements
    - Project author
    - Project maintainers
    - Project URLs
3. Update `src/fancypackage/core/_constants.py` to include any paths relevant to your analysis and that should be accessible from any script or Jupyter notebook
4. Update this README to include the relevant information about your project.
5. Ensure repository settings are set up correctly to build Jupyter Book:
    - In `Settings > Actions > General > Workflow permissions`: Allow read and write permissions.
    - In `Settings > Pages > Build and deployment`: Set the branch to `gh-pages`.
6. If you use uv with a custom environment name: update the `UV_PROJECT_ENVIRONMENT` value in `.envrc`

## Installation

### uv

To install the accompanying packages with [uv](https://docs.astral.sh/uv/), you can run

```bash
uv venv
uv sync --group jupyter

# Optional: Add jupyter kernel
uv run ipython kernel install --user --env VIRTUAL_ENV .venv --name fancypackage --display-name "fancypackage"
```

If you want to specify a custom environment name and specific Python version, you may use [direnv](https://direnv.net/) and run

```bash
direnv allow
uv venv -p X.Y
uv sync --group jupyter
uv run pre-commit install

# Optional: Add jupyter kernel
uv run ipython kernel install --user --env VIRTUAL_ENV $UV_PROJECT_ENVIRONMENT --name fancypackage-pyXY --display-name "fancypackage-pyX.Y"
```

### pixi

To set up the project with [pixi](https://pixi.prefix.dev/latest/), run

```bash
pixi add --pypi --editable --no-install --frozen "fancypackage @ file://$(pwd)"
pixi install
pixi run setup-pre-commit

# Optional: Add jupyter kernel
pixi run ipython kernel install --user --env ~/.pixi/envs/default --name fancypackage --display-name "fancypackage"
```

and to use a specific Python version and environment name, run

```bash
pixi add  --frozen --feature pyXY python=X.Y
pixi workspace environment add fancypackage-pyXY --feature pyXY --feature dev --feature jupyter
pixi add --pypi --editable --no-install --frozen "fancypackage @ file://$(pwd)"
pixi install -e fancypackage-pyXY
pixi run setup-pre-commit

# Optional: Add jupyter kernel
pixi run ipython kernel install --user --env VIRTUAL_ENV .pixi/envs/fancypackage-pyXY --name fancypackage-pyXY --display-name "fancypackage-pyX.Y"
```

## Things to keep in mind

Whenever you use a new single-cell tool, add it to `known_bio` in `pyproject.toml` so `isort` can work correctly.

## Workflow

The workflow for committing a notebook is as follows: Upon committing a notebook, the pre-commit hooks format your notebook
and generate a corresponding script. You need to add the formatted notebook and Python script to the same commit for the commit to go through. The commit will now either be successful or not. If not, your Python script was formatted by the pre-commit hooks. In that case, you need to update your notebook accordingly, unstage the Python script, and recommit the notebook. You will iterate through this process until there are no inconsistencies between the notebook and its corresponding Python script.
