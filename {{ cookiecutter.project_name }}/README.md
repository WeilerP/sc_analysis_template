# {{ cookiecutter.project_name }}

{{ cookiecutter.package_description }} The corresponding Jupyter Book is rendered [here]({{ cookiecutter.docs_url }}).

## Project structure

- `data/`
    - Directory containing data relevant to project
    - Contains one subdirectory for each dataset
    - Proposed structure: each dataset has its own subdirectory containing
        - `raw/`: original, unaltered data that always exists unless the data has been loaded from an external data directory
        - `processed/`: processed data from `raw/`
        - `results`: analysis results
- `figures/`
    - Directory to collect generated figures
    - Contains one subdirectory for each dataset
- `jobs/`
    - Directory to collect scripts for submitting HPC jobs, e.g., with sbatch, (in `jobs/scripts/`) and their generated output files (in `jobs/logs/`)
- `notebooks/`
    - Directory containing Jupyter notebooks
    - Contains one subdirectory for each dataset
- `scripts/`
    - Directory containing Python or R scripts
    - Contains one subdirectory for each dataset

## Installation

### uv

To install the accompanying packages with [uv](https://docs.astral.sh/uv/), you can run

```bash
uv venv
uv sync --group jupyter
uv run pre-commit install

# Optional: Add jupyter kernel
uv run ipython kernel install --user --env VIRTUAL_ENV .venv --name {{ cookiecutter.package_name }} --display-name "{{ cookiecutter.package_name }}"
```

If you want to specify a custom environment name and specific Python version, you may use [direnv](https://direnv.net/) and run

```bash
direnv allow
uv venv {{ cookiecutter.package_name }}-pyXY -p X.Y
uv sync --group jupyter
uv run pre-commit install

# Optional: Add jupyter kernel
uv run ipython kernel install --user --env VIRTUAL_ENV $UV_PROJECT_ENVIRONMENT --name {{ cookiecutter.package_name }}-pyXY --display-name "{{ cookiecutter.package_name }}-pyX.Y"
```

### pixi

To set up the project with [pixi](https://pixi.prefix.dev/latest/), run

```bash
pixi add --pypi --editable --no-install --frozen "{{ cookiecutter.package_name }} @ file://$(pwd)"
pixi install
pixi run setup-pre-commit

# Optional: Add jupyter kernel
pixi run ipython kernel install --user --env ~/.pixi/envs/default --name {{ cookiecutter.package_name }} --display-name "{{ cookiecutter.package_name }}"
```

and to use a specific Python version and environment name, run

```bash
pixi add  --frozen --feature pyXY python=X.Y
pixi workspace environment add {{ cookiecutter.package_name }}-pyXY --feature pyXY --feature dev --feature jupyter
pixi add --pypi --editable --no-install --frozen "{{ cookiecutter.package_name }} @ file://$(pwd)"
pixi install -e {{ cookiecutter.package_name }}-pyXY
pixi run setup-pre-commit

# Optional: Add jupyter kernel
pixi run ipython kernel install --user --env VIRTUAL_ENV .pixi/envs/{{ cookiecutter.package_name }}-pyXY --name {{ cookiecutter.package_name }}-pyXY --display-name "{{ cookiecutter.package_name }}-pyX.Y"
```

## Things to keep in mind

Whenever you use a new single-cell tool, add it to `bio` in `pyproject.toml` so `isort` can work correctly.

## Workflow

The workflow for committing a notebook is as follows: Upon committing a notebook, the pre-commit hooks format your notebook and generate a corresponding script. You need to add the formatted notebook and Python script to the same commit for the commit to go through. The commit will now either be successful or not. If not, your Python script was formatted by the pre-commit hooks. In that case, you need to update your notebook accordingly, unstage the Python script, and recommit the notebook. You will iterate through this process until there are no inconsistencies between the notebook and its corresponding Python script.
