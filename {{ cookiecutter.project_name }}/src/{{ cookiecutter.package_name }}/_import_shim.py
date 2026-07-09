from __future__ import annotations

import importlib
from typing import Any


def import_names(module: str, *names: str) -> tuple[Any, ...]:
    """Import ``names`` from the dotted module path ``module``.

    Template-authoring helper only. Every call site is rewritten into a plain
    ``from ... import ...`` statement, and this module itself is deleted, by
    ``hooks/post_gen_project.py`` after generation.

    Parameters
    ----------
    module
        Dotted path of the module to import from.
    names
        Attribute names to fetch from the imported module.

    Returns
    -------
    Tuple of the requested attributes, in the same order as ``names``.
    """
    mod = importlib.import_module(module)
    return tuple(getattr(mod, name) for name in names)
