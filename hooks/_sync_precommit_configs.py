import subprocess
import sys
import tempfile
from pathlib import Path

# The generator root keeps its own near-clone of the body's .pre-commit-config.yaml
# (so editing the template itself gets the same lint/format enforcement a generated
# project has), but the `repo: local` section is legitimately different in each: root's
# local hooks operate on the template repo itself (path prefixes, root-only checks like
# check-import-calls), body's operate on a standalone generated project.
#
# Everything ABOVE `repo: local` (the external tool hooks: biome, ruff, jupytext, ...)
# should stay identical between the two files. This hook keeps root's copy of that
# section in sync with body's (the source of truth — it's what real generated projects
# actually run) via a real 3-way merge, so a genuine conflict surfaces as ordinary git
# conflict markers (caught by the existing check-merge-conflict hook) instead of being
# silently overwritten.
LOCAL_MARKER = "  - repo: local\n"
ROOT_CONFIG = Path(".pre-commit-config.yaml")
BODY_CONFIG = Path("{{ cookiecutter.project_name }}/.pre-commit-config.yaml")


def split_at_local(text):
    """Split a pre-commit config into its synced prefix and untouched local suffix.

    Parameters
    ----------
    text
        Full contents of a ``.pre-commit-config.yaml`` file.

    Returns
    -------
    A ``(prefix, suffix)`` tuple, where ``suffix`` starts at the ``repo: local`` line.
    """
    idx = text.index(LOCAL_MARKER)
    return text[:idx], text[idx:]


def main():
    """Sync root's non-local pre-commit hooks from body's, 3-way-merging on conflict."""
    root_text = ROOT_CONFIG.read_text()
    body_text = BODY_CONFIG.read_text()

    root_prefix, root_local = split_at_local(root_text)
    body_prefix, _ = split_at_local(body_text)

    if root_prefix == body_prefix:
        return

    try:
        committed = subprocess.run(
            ["git", "show", f"HEAD:{ROOT_CONFIG}"], capture_output=True, text=True, check=True
        ).stdout
        base_prefix, _ = split_at_local(committed)
    except (subprocess.CalledProcessError, ValueError):
        base_prefix = root_prefix

    with tempfile.TemporaryDirectory() as tmp_dir:
        ours_path = Path(tmp_dir) / "ours.yaml"
        base_path = Path(tmp_dir) / "base.yaml"
        theirs_path = Path(tmp_dir) / "theirs.yaml"
        ours_path.write_text(root_prefix)
        base_path.write_text(base_prefix)
        theirs_path.write_text(body_prefix)

        result = subprocess.run(["git", "merge-file", "--diff3", str(ours_path), str(base_path), str(theirs_path)])
        merged_prefix = ours_path.read_text()

    ROOT_CONFIG.write_text(merged_prefix + root_local)

    if result.returncode != 0:
        sys.exit(
            f"Merge conflict syncing {ROOT_CONFIG} with {BODY_CONFIG} — "
            "resolve the conflict markers, then re-stage and re-commit."
        )


if __name__ == "__main__":
    main()
