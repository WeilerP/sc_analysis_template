import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from ..io import get_chrom_from_gtf  # noqa: TID252

if TYPE_CHECKING:
    from anndata import AnnData


def add_chromosome_info(adata: AnnData, gtf_path: str | Path, gene_id_column: str = "gene_ids") -> None:
    """Annotate ``adata.var`` with chromosome and sex-chromosome flags.

    Map ``var[gene_id_column]`` to chromosomes and inserts columns ``"chromosome"`` and ``"is_sex_chromosome"``.
    Idempotent: overwrites any pre-existing columns named ``"chromosome"`` and ``"is_sex_chromosome"``.

    Parameters
    ----------
    adata
        Annotated data.
    gtf_path
        Path to the Ensembl GTF used to resolve chromosomes.
    gene_id_column
        Column name in `adata.var` that contains the gene identifiers.
    """
    if gene_id_column not in adata.var or "genome" not in adata.var:
        warnings.warn(
            f"``adata.var`` does not include the gene ID column {gene_id_column}. Skipping chromosome annotation.",
            stacklevel=2,
        )
        return

    chromosome = adata.var[gene_id_column].map(get_chrom_from_gtf(gtf_path))

    n_unmapped = int(chromosome.isna().sum())
    if n_unmapped:
        warnings.warn(f"{n_unmapped}/{adata.n_vars} genes have no chromosome in the GTF.", stacklevel=2)

    adata.var["chromosome"] = chromosome.to_numpy()
    adata.var["is_sex_chromosome"] = chromosome.isin(("X", "Y")).to_numpy()
