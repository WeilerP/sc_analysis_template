from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from anndata import AnnData


def map_and_add_column(adata: AnnData, old_col: str, new_col: str, mapping: dict[str | int, list[str | int]]) -> None:
    """Aggregate cluster-level labels into a new `obs` column.

    Parameters
    ----------
    adata
        Annotated data with a categorical column ``old_col`` in `obs`.
    old_col
        Name of the `obs` column to map from.
    new_col
        Name of the `obs` column to create.
    mapping
        Maps each new label to the list of original labels it covers.

    Returns
    -------
    Nothing, only updates the passed AnnData object with the new column.

    Examples
    --------
    >>> # Input: AnnData object `adata` with 4 leiden clusters in `adata.obs["leiden"]`
    >>> # Goal: assign cells to their cell type by mapping the leiden clusters to the cell types
    >>> cell_type_to_leiden = {"T": {"0", "3"}, "B": {"1", "2"}}
    >>> map_and_add_column(adata, old_col="leiden", new_col="cell_type", mapping=cell_type_to_leiden)
    """
    labels = pd.Series(index=adata.obs_names, dtype=object)
    for new_label, old_labels in mapping.items():
        labels[adata.obs[old_col].isin(old_labels)] = new_label
    adata.obs[new_col] = labels.astype("category")
