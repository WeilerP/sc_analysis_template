import warnings
from pathlib import Path
from typing import Literal, TYPE_CHECKING

import zarr

import anndata as ad
from anndata import AnnData

if TYPE_CHECKING:
    from mudata import MuData
    from treedata import TreeData


def write_zarr(data: AnnData | MuData | TreeData, path: Path) -> None:
    """Write AnnData-like object to hierarchical Zarr array zip store.

    Parameters
    ----------
    adata
        AnnData-like object to save; supports AnnData, MuData and TreeData.
    path
        Filename of Zarr store.

    Returns
    -------
        Nothing, only writes data.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        store = zarr.storage.ZipStore(path, mode="w")
        data.write_zarr(store=store)
        store.close()


def read_zarr(path: Path, backend: Literal["anndata", "mudata", "treedata"] = "anndata") -> AnnData | MuData | TreeData:
    """Read hierarchical Zarr array zip store to AnnData-like object.

    Parameters
    ----------
    path
        Filename of Zarr store.
    backend
        Backend to use for reading the Zarr store. Supported backends are "anndata" (default), "mudata" and "treedata".

    Returns
    -------
    The read AnnData-like object (Anndata, MuData, or TreeData).
    """
    store = zarr.storage.ZipStore(path, mode="r")

    if backend == "anndata":
        data = ad.read_zarr(store)
    elif backend == "mudata":
        import mudata as md

        data = md.read_zarr(store)
    elif backend == "treedata":
        import treedata as td

        data = td.read_zarr(store)
    store.close()

    return data
