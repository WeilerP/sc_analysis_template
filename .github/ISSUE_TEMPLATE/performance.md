---
name: Performance
about: Report a speed, memory, or scalability problem
title: ""
labels: performance
assignees: ""
---

## Description

<!-- What operation is slow or uses excessive memory, and on what data scale? -->

[TEXT HERE]

## Benchmark

<!-- Timing/memory numbers, how they were measured, and profiler output if available. -->

```python
# Benchmark or profiling code here
```

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
