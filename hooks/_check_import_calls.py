import shutil
import sys
import tempfile
from pathlib import Path

from post_gen_project import prettify_notebook, prettify_script


def check_file(path: str) -> None:
    """Validate a script or notebook's ``_import(...)`` bootstrap calls without rewriting it.

    Runs the real prettification logic against a disposable copy of ``path`` so the
    original template source (still containing unrendered Jinja tokens) is never
    modified; only the ``ValueError`` raised on a name mismatch is of interest here.

    Parameters
    ----------
    path
        Path to the ``.py`` or ``.ipynb`` file to validate.

    Returns
    -------
    Nothing. Raises ``ValueError`` if a mismatch is found.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / Path(path).name
        shutil.copy(path, tmp_path)
        if path.endswith(".py"):
            prettify_script(str(tmp_path))
        elif path.endswith(".ipynb"):
            prettify_notebook(str(tmp_path))


def main(paths: list[str]) -> int:
    """Validate every path in ``paths``, reporting all mismatches found.

    Parameters
    ----------
    paths
        Files to check, as passed by pre-commit.

    Returns
    -------
    ``0`` if all files are consistent, ``1`` otherwise.
    """
    errors = []
    for path in paths:
        try:
            check_file(path)
        except ValueError as e:
            errors.append(f"{path}: {e}")
    if errors:
        print(*errors, sep="\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
