# Single-cell analysis template repository

This repository acts as a template notebook for the analysis of single-cell data and methods.
You can check the [CellRank 2 reproducibility repository](https://github.com/theislab/cellrank2_reproducibility)
for an example repository following the same outline as this template.

## Set up

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

## Installation

```bash
conda create -n fancyname-pyXX python=X.X --yes && conda activate fancyname-pyXX
pip install -e ".[dev]"
pre-commit install

pip install jupyterlab ipywidgets
python -m ipykernel install --user --name fancyname-pyXX --display-name "fancyname-pyXX"
```

## Things to keep in mind

Whenever you use a new single-cell tool, add it to `known_bio` in `pyproject.toml` s.t. `isort` can work correctly.

## Workflow

The workflow for committing a notebook is as follows: Upon committing a notebook, the pre-commit hooks format your notebook
and generate a corresponding script. You need to add the formatted notebook and Python script to the same commit for the commit to go through. The commit will now either be successful or not. If not, your Python script was formatted by the pre-commit hooks. In that case, you need to update your notebook accordingly, unstage the Python script, and recommit the notebook. You will iterate through this process until there are no inconsistencies between the notebook and its corresponding Python script.
