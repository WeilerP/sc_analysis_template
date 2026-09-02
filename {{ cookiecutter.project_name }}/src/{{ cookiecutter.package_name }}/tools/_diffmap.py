from typing import Literal

import scanpy as sc
import scanpy.logging as logg
from anndata import AnnData

from ..preprocessing import neighbors  # noqa: TID252


def diffmap(
    adata: AnnData,
    n_comps: int = 15,
    knn: int = 30,
    alpha: float = 0.0,
    obsm_key: str = "X_pca",
    key_added: str = "adaptive",
    random_state: int = 0,
    backend: Literal["scanpy", "rapids"] = "scanpy",
    copy: bool = False,
) -> AnnData | None:
    """Compute a Palantir-style diffusion map.

    Replaces the fixed-bandwidth UMAP/Gaussian kernel of `sc.pp.neighbors` with Palantir's adaptive anisotropic kernel
    (Setty et al. 2019) via `pp.neighbors(adata, adaptive=True, ...)`, before running the diffusion-map
    eigendecomposition. Density normalization of the diffusion operator (Coifman & Lafon, 2006) is performed by the
    underlying diffmap implementation, exactly as it would be for Palantir's own diffusion components. Does not require
    `palantir` as a dependency.

    Parameters
    ----------
    adata
        Annotated data matrix.
    n_comps
        Number of diffusion components to compute. Must be greater than 2, as enforced by `sc.tl.diffmap`.
    knn
        Number of nearest neighbors used to build the adaptive kernel. The per-observation bandwidth is the distance to
        each observation's `floor(knn / 3)`-th nearest neighbor.
    alpha
        Density normalization exponent applied to the adaptive kernel; `0` disables it, matching Palantir's default.
    obsm_key
        Key of `adata.obsm` holding the embedding the adaptive kernel is built from.
    key_added
        Prefix under which the adaptive kernel is stored on `adata` and handed on via `neighbors_key`. See Returns.
    random_state
        Random seed used for both the kNN search and the eigendecomposition.
    backend
        Library used for the kNN search and the eigendecomposition: `"scanpy"` (CPU) or `"rapids"` (GPU, requires
        `rapids_singlecell`).
    copy
        Return a copy of `adata` instead of writing to it in place.

    Returns
    -------
    Returns `None` if `copy=False`, else the updated copy. Sets `adata.obsm["X_diffmap"]` and
    `adata.uns["diffmap_evals"]` as `sc.tl.diffmap` does, and leaves the adaptive kernel on
    `adata.obsp[f"{key_added}_connectivities"]` / `adata.uns[f"{key_added}_neighbors"]` for reuse.

    Notes
    -----
    The 0-th column of `adata.obsm["X_diffmap"]` is the non-informative steady-state solution; the first diffusion
    component is at index 1.
    """
    if backend not in ("scanpy", "rapids"):
        raise ValueError(f"`backend` needs to be `'scanpy'` or `'rapids'` but is `{backend!r}`.")

    if n_comps >= adata.n_obs:
        logg.warning(
            f"`n_comps={n_comps}` is >= `adata.n_obs={adata.n_obs}`; the number of components will be "
            "silently capped to `adata.n_obs - 1`."
        )

    adata = adata.copy() if copy else adata

    neighbors(
        adata,
        adaptive=True,
        knn=knn,
        alpha=alpha,
        obsm_key=obsm_key,
        key_added=key_added,
        backend=backend,
        random_state=random_state,
        copy=False,
    )

    neighbors_key = f"{key_added}_neighbors"
    if backend == "scanpy":
        sc.tl.diffmap(adata, n_comps=n_comps, neighbors_key=neighbors_key, random_state=random_state)
    elif backend == "rapids":
        import rapids_singlecell as rsc

        rsc.tl.diffmap(adata, n_comps=n_comps, neighbors_key=neighbors_key, rng=random_state)

    if copy:
        return adata
