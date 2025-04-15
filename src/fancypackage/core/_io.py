from pathlib import Path

import zarr

from anndata import AnnData
from anndata.experimental import read_elem_as_dask
from anndata.io import read_elem


def read_as_dask(store: Path | str, layers: str | list[str]) -> AnnData:
    """Read AnnData with `X` and layers read with dask.

    ```python
    adata = read_as_dask(file_path)

    obs_mask = adata.obs[column] == group

    adata_subset = adata[obs_mask, :].copy()
    uns = {}
    for parameter in uns_keys:
        value = adata.uns[group][parameter]
        if value.shape == (adata_subset.n_vars,):
            adata_subset.var[parameter] = value
        else:
            uns[parameter] = value
    adata_subset.uns = uns

    return adata_subset.to_memory()
    ```

    Parameters
    ----------
    store
        Store or path to directory in file system or name of zip file.
    layers
        Layers to include in the AnnData.

    Returns
    -------
    AnnData backed with dask.
    """
    group = zarr.open(store=store)

    adata = AnnData(
        obs=read_elem(group["obs"]),
        var=read_elem(group["var"]),
        uns=read_elem(group["uns"]),
        obsm=read_elem(group["obsm"]),
        varm=read_elem(group["varm"]),
    )

    adata.X = read_elem_as_dask(group["X"])

    if isinstance(layers, str):
        layers = [layers]
    for layer in layers:
        adata.layers[layer] = read_elem_as_dask(group[f"layers/{layer}"])

    return adata
