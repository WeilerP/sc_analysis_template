# {{ cookiecutter.project_name }}

{{ cookiecutter.package_description }} The corresponding Jupyter Book is rendered [here](https://{{ cookiecutter.github_namespace }}.github.io/{{ cookiecutter.github_repo_name }}/).

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

## Package utilities

`{{ cookiecutter.package_name }}` exposes a few helper functions used throughout the notebooks/scripts:

### Core utility

- `DATA_DIR`, `FIG_DIR`: project-root-relative paths to `data/` and `figures/`
- `get_logger`: a preconfigured, idempotent logger; repeated calls return the same instance without adding duplicate handlers

### IO

Accessible from `{{ cookiecutter.package_name }}.io`, using `anndata` as default backend; `"mudata"` and `"treedata"` are supported as well.

- `write_zarr`: store datasets as Zarr zip archives
- `read_zarr`: read Zarr zip archives
- `read_as_dask`: read Zarr zip archives lazily into `AnnData` objects

### Plotting

Accessible from `{{ cookiecutter.package_name }}.plotting`.

- `style_context`: plotting context manager for scientific figures
- `plot_embedding`: a wrapper for `sc.pl.embedding` that ensures aspect is set to `"auto"` (needed for UMAP, t-SNE, etc. plots) and continuous annotations are not sorted by default (prevents skewed interpretation based on plotting artifacts)

### Statistics

Accessible from `{{ cookiecutter.package_name }}.stats`.

- `is_outlier`: identifies putative outlier observations based on median absolute deviations.

## Repository setup

For the Jupyter Book to deploy on push to `main`, set up the repository once:
- `Settings > Actions > General > Workflow permissions`: allow read and write permissions.
- `Settings > Pages > Build and deployment`: set `GitHub Actions` as Source.

If the repo is private and you authenticate over HTTPS with a PAT:

```bash
./.set_gh_remote.sh <your-PAT>
```

This sets `origin` to `https://<github_username>:<PAT>@github.com/<github_namespace>/<repo>.git` — the PAT is only ever passed as a CLI argument, never stored in any file.

## Things to keep in mind

Whenever you use a new single-cell tool, add it to `bio` in `pyproject.toml` so `isort` can work correctly.

## Documentation

The Jupyter Book is deployed [here](https://{{ cookiecutter.github_namespace }}.github.io/{{ cookiecutter.github_repo_name }}/) on every push to `main`. To build and preview it locally:

```bash
cd notebooks
uv run jupyter-book build --html
```

`notebooks/index.md` is generated from this README by a pre-commit hook (a 3-way merge via `git merge-file`) — edit this README, not `index.md` directly; a direct edit there is merged rather than clobbered, but conflicts show up as ordinary git conflict markers that need resolving by hand.

## Workflow

The workflow for committing a notebook is as follows: Upon committing a notebook, the pre-commit hooks format your notebook and generate a corresponding script. You need to add the formatted notebook and Python script to the same commit for the commit to go through. The commit will now either be successful or not. If not, your Python script was formatted by the pre-commit hooks. In that case, you need to update your notebook accordingly, unstage the Python script, and recommit the notebook. You will iterate through this process until there are no inconsistencies between the notebook and its corresponding Python script.

## License

This project is licensed under the terms of the [BSD 3-Clause License](LICENSE).
