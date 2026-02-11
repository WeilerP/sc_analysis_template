# %% [markdown]
# # A descriptive title
#
# A short description of what this notebook is doing.

# %% [markdown]
# ## Library imports

# %%
from fancypackage import DATA_DIR, FIG_DIR
from fancypackage.io import read_zarr

# %% [markdown]
# ## General settings

# %%
DATASET_ID = ""

# %%
SAVE_FIGURES = False
if SAVE_FIGURES:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

FIGURE_FORMAT = "pdf"

# %% [markdown]
# ## Constants

# %% [markdown]
# ## Function definitions

# %% [markdown]
# ## Data loading

# %%
adata = read_zarr(DATA_DIR / DATASET_ID / "adata.zarr.zip")
adata

# %% [markdown]
# ## Data preprocessing

# %% [markdown]
# ## More advanced data analysis
