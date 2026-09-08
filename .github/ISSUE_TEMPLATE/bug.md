---
name: Bug report
about: Create a report to help us improve
title: ""
labels: bug
assignees: ""
---

<!-- Describe the bug -->

## Description

[TEXT HERE]

<!-- To reproduce -->

```python
# Your code here
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

<details> <summary> Error output </summary>

```pytb
# Paste the error output here, if applicable
```

</details>

## Versions

<details> <summary> Versions </summary>

Run this in a notebook, then click the "Copy as Markdown" button and paste the result here:

```pycon
import gmi, session_info2; session_info2.session_info(dependencies=True)
```

Or from the pixi environment shell (do not use `uvx` for this — it won't see gmi's installed dependencies):

```shell
session-info2 -f markdown
```

</details>
