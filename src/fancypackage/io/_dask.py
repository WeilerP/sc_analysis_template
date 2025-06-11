from itertools import chain
from pathlib import Path
from typing import Generator

import zarr
from zarr.hierarchy import Group

from anndata import AnnData
from anndata.experimental import read_elem_as_dask
from anndata.io import read_elem


def _get_entries(group: Group, level: str, entries: str | list[str] | None) -> Generator | list[str]:
    """Get entries of a Zarr group, potentially subsetted.

    Parameters
    ----------
    group
        Hierarchical Zarr group.
    level
        Level in `group` to read entries from.
    entries
        Entries to read. If `None`, all groups and arrays in `level` are inferred.

    Returns
    -------
    Groups and arrays of specified level in the hierarchical Zarr group as a generator or list of strings.
    """
    if entries is None:
        return chain(group[level].group_keys(), group[level].array_keys())
    elif isinstance(entries, str):
        return [entries]
    else:
        return entries


def read_as_dask(
    store: Path | str,
    layers: str | list[str] | None = None,
    obsm_keys: str | list[str] | None = None,
    varm_keys: str | list[str] | None = None,
) -> AnnData:
    """Read AnnData with read with dask.

    ```python
    adata = read_as_dask(file_path)

    obs_mask = adata.obs[column] == group
    adata_subset = adata[obs_mask, :].to_memory()
    ```

    Parameters
    ----------
    store
        Store or path to directory in file system or name of zip file.
    layers
        Layers to include in the AnnData. If `None`, all layers are read with dask.
    obsm_keys
        Entries in `obsm` to include in the AnnData. If `None`, all entries are read with dask.
    varm_keys
        Entries in `varm` to include in the AnnData. If `None`, all entries are read with dask.

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

    layers = _get_entries(group=group, level="layers", entries=layers)
    for layer in layers:
        adata.layers[layer] = read_elem_as_dask(group[f"layers/{layer}"])

    obsm_keys = _get_entries(group=group, level="obsm", entries=obsm_keys)
    for obsm_key in obsm_keys:
        adata.obsm[obsm_key] = read_elem_as_dask(group[f"obsm/{obsm_key}"])

    varm_keys = _get_entries(group=group, level="varm", entries=varm_keys)
    for varm_key in varm_keys:
        adata.obsm[varm_key] = read_elem_as_dask(group[f"varm/{varm_key}"])

    return adata
