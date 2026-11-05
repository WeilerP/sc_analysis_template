from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pandas import Series


def read_chrom_from_gtf(fpath: str | Path) -> Series:
    """Map Ensembl gene IDs to chromosomes from a GTF annotation.

    Parses the ``gene`` feature rows of an Ensembl GTF to extract each gene's chromosome from the ``seqname`` field.

    Parameters
    ----------
    fpath
        Path to an Ensembl GTF (``.gtf`` or ``.gtf.gz``).

    Returns
    -------
    Pandas Series indexed by Ensembl IDs and their corresponding chromosome name as values.
    """
    fpath = Path(fpath)
    if not fpath.exists():
        raise FileNotFoundError(f"GTF annotation not found at {fpath}")

    gtf = pd.read_csv(
        fpath,
        sep="\t",
        comment="#",
        header=None,
        usecols=[0, 2, 8],
        names=["seqname", "feature", "attributes"],
        dtype=str,
    )

    var_mask = gtf["feature"].isin(["gene"])
    var_names = gtf.loc[var_mask, :].copy()
    var_ids = var_names["attributes"].str.extract(r'gene_id "([^"]+)"', expand=False)

    chrom_by_var = pd.Series(var_names["seqname"].to_numpy(), index=var_ids, name="chromosome")
    return chrom_by_var[~chrom_by_var.index.duplicated(keep="first")]
