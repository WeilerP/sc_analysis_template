from __future__ import annotations

from collections.abc import Generator
from itertools import chain
from typing import Literal, TYPE_CHECKING

import zarr
from zarr import Group as ZarrGroup
from zarr.storage import StoreLike

from anndata import AnnData
from anndata.experimental import read_elem_lazy
from anndata.io import read_elem

if TYPE_CHECKING:
    from treedata import TreeData


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
    if level not in ("layers", "obsm", "obsp", "varm", "varp"):
        raise ValueError(
            f"Argument `level` needs to be in `'layers'`, `'obsm'`, `'obsp'`, `'varm'` or `'varp'` but is {level}."
        )

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
    backend: Literal["anndata", "treedata"] = "anndata",
) -> AnnData | TreeData:
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
        Entries in `obsp` to read lazily (dask-backed). If `None`, every entry is read with dask.
    varp_keys
        Entries in `varp` to read lazily (dask-backed). If `None`, every entry is read with dask.

    Returns
    -------
    AnnData-like object with `X`, `layers`, `obsp`, and `varp` dask-backed; `obsm`/`varm` in memory unless requested
    lazily.
    """
    group = zarr.open(store=store)

    if backend == "anndata":
        DataClass = AnnData
    elif backend == "treedata":
        from treedata import TreeData
        from treedata._core.read import _read_axis_trees_zarr

        DataClass = TreeData

    data = DataClass(
        obs=read_elem(group["obs"]),
        var=read_elem(group["var"]),
        uns=read_elem(group["uns"]),
    )

    if backend == "treedata":
        if "obst" in group.keys():
            data.obst = _read_axis_trees_zarr(group["obst"])
        if "vart" in group.keys():
            data.vart = _read_axis_trees_zarr(group["vart"])

    data.X = read_elem_lazy(group["X"])

    lazy_by_default = {"layers", "obsp", "varp"}
    for level, lazy_keys in (
        ("layers", layers),
        ("obsm", obsm_keys),
        ("varm", varm_keys),
        ("obsp", obsp_keys),
        ("varp", varp_keys),
    ):
        if level in lazy_by_default:
            lazy_keys = _get_entries(group=group, level=level, entries=lazy_keys)
        _read_axis_arrays(getattr(data, level), group=group, level=level, lazy_keys=lazy_keys)

    group.store.close()

    return data
