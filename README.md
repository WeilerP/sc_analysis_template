# sc_analysis_template

A [cookiecutter](https://cookiecutter.readthedocs.io/)/[cruft](https://cruft.github.io/cruft/) template for single-cell analysis projects. It scaffolds a ready-to-run project (notebooks, scripts, a `src/` package, Jupyter Book docs, pre-commit hooks) with all the project-specific values filled in automatically, and later lets you pull template improvements into a project you already generated.

You can check out the [CellRank 2](https://github.com/theislab/cellrank2_reproducibility) and [CellRank protocol](https://github.com/theislab/cellrank_protocol) reproducibility repositories for example repositories following the same outline as this template, built off an earlier version of it.

## Create a project

```bash
uvx cruft create https://github.com/WeilerP/sc_analysis_template
```

You'll be prompted for:

- `project_name`: human-readable project name
- `package_name`: Python import name (derived from `project_name`, editable)
- `package_description`, `author_name`, `author_email`
- `github_username`: your personal GitHub account
- `github_namespace`: the account or organization the repo will live under (defaults to `github_username`)

## After generation

`cd` into the generated directory, and follow the installation and setup instructions outlined in the project's README.

## Updating a project you already generated

```bash
uvx cruft check    # is this project behind the template?
uvx cruft update   # apply template changes; writes *.rej files only on conflict
```

If `cruft update` produces `.rej` files, resolve the conflicts by hand and remove them — the generated project's pre-commit hooks (`check-merge-conflict`, `forbid-to-commit`) block committing until you do.

## Developing the template

Everything a generated project gets lives under `{{ cookiecutter.project_name }}/`; `cookiecutter.json` defines the prompted variables, and `hooks/pre_gen_project.py` / `hooks/post_gen_project.py` run before/after generation. To test a change:

```bash
uvx cruft create . --no-input --output-dir /tmp/cc-out
cd "/tmp/cc-out/Example Analysis"
uv sync --all-groups && uv run pre-commit run --all-files
```

## License

This project is licensed under the terms of the [BSD 3-Clause License](LICENSE).
