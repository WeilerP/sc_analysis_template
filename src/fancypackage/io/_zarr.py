import warnings
from pathlib import Path
from typing import TYPE_CHECKING

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


def read_zarr(path: Path) -> AnnData:
    """Read hierarchical Zarr array zip store to AnnData.

    Parameters
    ----------
    path
        Filename of Zarr store.

    Returns
    -------
    Read AnnData object.
    """
    store = zarr.storage.ZipStore(path, mode="r")
    adata = ad.io.read_zarr(store)
    store.close()

    return adata
