# %% [markdown]
# # A descriptive title
#
# A short description of what this notebook is doing.

# %% [markdown]
# ## Library imports

# %%
import anndata as ad

from fancypackage import DATA_DIR, FIG_DIR

# %% [markdown]
# ## General settings

# %%
SAVE_FIGURES = False
if SAVE_FIGURES:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

FIGURE_FORMATE = "pdf"

# %% [markdown]
# ## Constants

# %% [markdown]
# ## Function definitions

# %% [markdown]
# ## Data loading

# %%
adata = ad.io.read_zarr(DATA_DIR / "adata.zarr")
adata

# %% [markdown]
# ## Data preprocessing

# %% [markdown]
# ## More advanced data analysis
