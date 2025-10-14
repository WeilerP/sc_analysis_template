import warnings
from pathlib import Path

import zarr

import anndata as ad
from anndata import AnnData


def write_zarr(adata: AnnData, path: Path) -> None:
    """Write AnnData to hierarchical Zarr array zip store.

    Parameters
    ----------
    adata
        AnnData to save.
    path
        Filename of Zarr store.

    Returns
    -------
        Nothing, only writes data.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        store = zarr.storage.ZipStore(path, mode="w")
        adata.write_zarr(store=store)
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
