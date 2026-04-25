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
SAVE_DATE = True
SAVE_FIGURES = False

# %% [markdown]
# ## Constants

# %%
DATASET_ID = ""
if SAVE_DATE:
    (DATA_DIR / DATASET_ID / "processed").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / DATASET_ID / "results").mkdir(parents=True, exist_ok=True)

if SAVE_FIGURES:
    (FIG_DIR / DATASET_ID).mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Function definitions

# %% [markdown]
# ## Data loading

# %%
adata = read_zarr(DATA_DIR / DATASET_ID / "adata.zarr.zip")
adata

# %% [markdown]
# ## Data preprocessing

# %%

# %% [markdown]
# ## More advanced data analysis

# %% [markdown]
#
