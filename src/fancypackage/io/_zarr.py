import warnings
from pathlib import Path

import zarr

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
        store = zarr.ZipStore(path, mode="w")
        adata.write_zarr(store=store)
        store.close()
