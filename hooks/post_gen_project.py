import json
import os
import re

PACKAGE_NAME = "{{ cookiecutter.package_name }}"

# The template source can't use `from {{ cookiecutter.package_name }} import ...` directly,
# since a raw Jinja token in import position isn't valid Python. Instead it bootstraps a
# thin `_import(module, *names)` helper (see src/{{ cookiecutter.package_name }}/_import_shim.py)
# and calls it, keeping the unrendered template files themselves valid, lintable Python.
# After generation, this hook rewrites every call site back into a plain import statement,
# strips the now-unused bootstrap lines, and deletes the shim module.
BOOTSTRAP_RE = re.compile(
    r"^import importlib\n\n?"
    r"_import = importlib\.import_module\(\"[^\"]*\._import_shim\"\)\.import_names\n\n?",
    re.MULTILINE,
)
CALL_RE = re.compile(r"^(?P<lhs>.*)= _import\((?P<args>[^()]*)\)[ \t]*$", re.MULTILINE)


def _replace_call(match: re.Match[str]) -> str:
    """Reconstruct a plain ``from module import names`` statement from an ``_import(...)`` call.

    Parameters
    ----------
    match
        Regex match against ``CALL_RE``, capturing the assignment's left-hand side
        (``lhs``) and the call's argument list (``args``).

    Returns
    -------
    The equivalent ``from module import name1, name2, ...`` statement.
    """
    lhs_names = [n.strip() for n in match.group("lhs").strip().strip("()").split(",") if n.strip()]
    args = re.findall(r'"([^"]*)"', match.group("args"))
    module, names = args[0], args[1:]
    if lhs_names != names:
        raise ValueError(f"_import mismatch: left-hand side {lhs_names} != imported names {names} (module {module!r})")
    return f"from {module} import {', '.join(names)}"


def prettify_text(text: str) -> str:
    """Rewrite ``_import(...)`` bootstrap calls in ``text`` into plain import statements.

    Parameters
    ----------
    text
        Source text (script or notebook cell source) to rewrite.

    Returns
    -------
    ``text`` with every ``_import(...)`` call site replaced by a plain import
    statement and the now-unused bootstrap lines removed.
    """
    text = CALL_RE.sub(_replace_call, text)
    return BOOTSTRAP_RE.sub("", text)


def prettify_script(path: str) -> None:
    """Rewrite ``_import(...)`` bootstrap calls in a Python script in place.

    Parameters
    ----------
    path
        Path to the ``.py`` file to rewrite.

    Returns
    -------
    Nothing, only rewrites the file.
    """
    with open(path) as f:
        content = f.read()
    with open(path, "w") as f:
        f.write(prettify_text(content))


def prettify_notebook(path: str) -> None:
    """Rewrite ``_import(...)`` bootstrap calls in a Jupyter notebook's cells in place.

    Parameters
    ----------
    path
        Path to the ``.ipynb`` file to rewrite.

    Returns
    -------
    Nothing, only rewrites the file.
    """
    with open(path) as f:
        nb = json.load(f)
    for cell in nb["cells"]:
        source = "".join(cell.get("source", []))
        pretty = prettify_text(source).strip("\n")
        if pretty != source.strip("\n"):
            lines = pretty.split("\n")
            cell["source"] = [line + "\n" for line in lines[:-1]] + [lines[-1]]
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
        f.write("\n")


def main() -> None:
    """Prettify all scripts/notebooks, delete the import shim, and set script permissions."""
    for root, _dirs, filenames in os.walk("."):
        for name in filenames:
            path = os.path.join(root, name)
            if name.endswith(".py"):
                prettify_script(path)
            elif name.endswith(".ipynb"):
                prettify_notebook(path)

    shim_path = os.path.join("src", PACKAGE_NAME, "_import_shim.py")
    if os.path.exists(shim_path):
        os.remove(shim_path)

    for script in [".set_gh_remote.sh", ".sync_readme_to_index.sh"]:
        os.chmod(script, 0o755)


if __name__ == "__main__":
    main()
