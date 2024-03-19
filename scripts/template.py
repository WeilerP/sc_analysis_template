# %% [markdown]
# # A descriptive title
#
# A short description of what this notebook is doing.

# %% [markdown]
# ## Library imports

# %%
import os
import sys

import scanpy as sc

sys.path.extend(["../", "."])
from paths import DATA_DIR, FIG_DIR  # isort: skip  # noqa: E402

# %% [markdown]
# ## General settings

# %%
SAVE_FIGURES = False
if SAVE_FIGURES:
    os.makedirs(FIG_DIR, exist_ok=True)

FIGURE_FORMATE = "pdf"

# %% [markdown]
# ## Constants

# %% [markdown]
# ## Function definitions

# %% [markdown]
# ## Data loading

# %%
adata = sc.read(DATA_DIR / "adata.h5ad")
adata

# %% [markdown]
# ## Data preprocessing

# %% [markdown]
# ## More advanced data analysis
