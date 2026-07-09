from collections.abc import Generator
from itertools import chain
from typing import Literal

import zarr
from zarr import Group as ZarrGroup
from zarr.storage import StoreLike

from anndata import AnnData
from anndata.experimental import read_elem_lazy
from anndata.io import read_elem


def _get_entries(group: ZarrGroup, level: str, entries: str | list[str] | None) -> Generator | list[str]:
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


def _read_axis_arrays(
    adata_axis_arrays, group: ZarrGroup, level: Literal["obsm", "varm"], lazy_keys: str | list[str] | None
) -> None:
    """Populate an `obsm`/`varm` mapping, reading `lazy_keys` with dask and the rest in memory.

    Parameters
    ----------
    adata_axis_arrays
        The `adata.obsm` or `adata.varm` mapping to populate in place.
    group
        Hierarchical Zarr group.
    level
        Either ``"obsm"`` or ``"varm"``.
    lazy_keys
        Entries to read lazily (dask-backed). If `None`, every entry is read in memory;
        these mappings are small (n_obs/n_var x k) and going lazy mainly breaks downstream
        array operations such as plotting.
    """
    if level not in ("obsm", "varm"):
        raise ValueError(f"Argument `level` needs to be either `'obsm'` or `'varm'` but is {level}.")

    lazy = {lazy_keys} if isinstance(lazy_keys, str) else set(lazy_keys or [])
    for key in chain(group[level].group_keys(), group[level].array_keys()):
        element = group[f"{level}/{key}"]
        adata_axis_arrays[key] = read_elem_lazy(element) if key in lazy else read_elem(element)


def read_as_dask(
    store: StoreLike,
    layers: str | list[str] | None = None,
    obsm_keys: str | list[str] | None = None,
    varm_keys: str | list[str] | None = None,
    obsp_keys: str | list[str] | None = None,
    varp_keys: str | list[str] | None = None,
) -> AnnData:
    """Read AnnData with dask.

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
        Layers to read lazily (dask-backed). If `None`, all layers are read with dask.
    obsm_keys
        Entries in `obsm` to read lazily (dask-backed). If `None`, every entry is read in memory.
    varm_keys
        Entries in `varm` to read lazily (dask-backed). If `None`, every entry is read in memory.
    obsp_keys
        Entries in `obsp` to read lazily (dask-backed). If `None`, every entry is read in memory.
    varp_keys
        Entries in `varp` to read lazily (dask-backed). If `None`, every entry is read in memory.

    Returns
    -------
    AnnData with `X` and `layers` dask-backed; `obsm`/`varm`/`obsp`/`varp` in memory unless requested lazily.
    """
    group = zarr.open(store=store)

    adata = AnnData(
        obs=read_elem(group["obs"]),
        var=read_elem(group["var"]),
        uns=read_elem(group["uns"]),
    )

    adata.X = read_elem_lazy(group["X"])

    for layer in _get_entries(group=group, level="layers", entries=layers):
        adata.layers[layer] = read_elem_lazy(group[f"layers/{layer}"])

    _read_axis_arrays(adata.obsm, group=group, level="obsm", lazy_keys=obsm_keys)
    _read_axis_arrays(adata.varm, group=group, level="varm", lazy_keys=varm_keys)
    _read_axis_arrays(adata.obsp, group=group, level="obsp", lazy_keys=obsp_keys)
    _read_axis_arrays(adata.varp, group=group, level="varp", lazy_keys=varp_keys)

    group.store.close()

    return adata
