import keyword
import re
import sys

PACKAGE_NAME = "{{ cookiecutter.package_name }}"
AUTHOR_EMAIL = "{{ cookiecutter.author_email }}"

RESERVED_NAMES = {"src", "data", "figures", "jobs", "notebooks", "scripts", "test"}

if not re.match(r"^[a-z_][a-z0-9_]*$", PACKAGE_NAME) or keyword.iskeyword(PACKAGE_NAME):
    sys.exit(
        f"ERROR: package_name '{PACKAGE_NAME}' is not a valid Python identifier "
        "(lowercase letters/digits/underscores, not starting with a digit, not a keyword)."
    )

if PACKAGE_NAME in RESERVED_NAMES:
    sys.exit(f"ERROR: package_name '{PACKAGE_NAME}' collides with a project directory name.")

if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", AUTHOR_EMAIL):
    sys.exit(f"ERROR: author_email '{AUTHOR_EMAIL}' is not a valid email address.")
