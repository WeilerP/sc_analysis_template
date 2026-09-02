from typing import Literal

import numpy as np
from scipy import sparse

import scanpy as sc
from anndata import AnnData


def _adaptive_kernel(
    embedding: np.ndarray,
    knn: int,
    alpha: float,
    random_state: int,
    backend: Literal["scanpy", "rapids"],
) -> sparse.csr_matrix:
    """Build Palantir's adaptive anisotropic affinity kernel from an embedding.

    For every observation, the distance to its own `floor(knn / 3)`-th nearest neighbor is used as a per-observation
    bandwidth. kNN distances are scaled by that bandwidth and exponentiated, then symmetrized. Coifman-Lafon density
    normalization is applied on top if `alpha > 0`.

    Parameters
    ----------
    embedding
        Array of shape (n_obs, n_features) to search nearest neighbors in, e.g. `adata.obsm["X_pca"]`.
    knn
        Number of nearest neighbors to use when estimating the adaptive bandwidth.
    alpha
        Density normalization exponent. `0` disables normalization; `1` removes density information entirely, as in
        classical Laplacian Eigenmaps.
    random_state
        Random seed forwarded to the kNN search.
    backend
        Library computing the kNN graph: `"scanpy"` for `sc.pp.neighbors` (CPU) or `"rapids"` for
        `rapids_singlecell.pp.neighbors` (GPU).

    Returns
    -------
    Sparse, symmetric affinity kernel of shape (n_obs, n_obs).
    """
    n_obs = embedding.shape[0]
    temp = AnnData(np.asarray(embedding))
    if backend == "scanpy":
        sc.pp.neighbors(temp, n_pcs=0, n_neighbors=knn, random_state=random_state)
    elif backend == "rapids":
        import rapids_singlecell as rsc

        rsc.pp.neighbors(temp, n_pcs=0, n_neighbors=knn, random_state=random_state)
    knn_distances = temp.obsp["distances"]

    # `floor(knn / 3)` matches Palantir (Setty et al., Nature Biotech).
    # `knn_distances` is a kNN graph adjacency matrix: every row holds exactly the same number of *stored* entries by
    # definition of a k-nearest-neighbors query (holds regardless of backend), so `knn_distances.data` can be reshaped
    # to `(n_obs, row_length)` and partitioned along `axis=1` in a single vectorized call. Duplicate observations
    # store an explicit zero rather than dropping the entry, so the row length stays constant for them, too.
    # `row_length` can be smaller than `knn` if `sc.pp.neighbors` shrank `n_neighbors` for a small dataset, but that
    # shrink is applied uniformly to every row, so a single `min(...)` clamp still covers it.
    adaptive_k = max(1, int(np.floor(knn / 3)))
    row_length = knn_distances.getnnz(axis=1)[0]
    k = min(adaptive_k, row_length)
    distances_matrix = knn_distances.data.reshape(n_obs, row_length)
    adaptive_std = np.partition(distances_matrix, k - 1, axis=1)[:, k - 1]

    # `sparse.find` drops the stored zeros, leaving `dists` strictly positive, so the division below can never
    # evaluate `0 / 0`: `weights` is always finite. `adaptive_std` can still be 0 for an observation with enough
    # exact duplicates to zero its bandwidth, which divides to `inf` and exponentiates to an affinity of 0.
    # Only that divide-by-zero is silenced, so a `0 / 0` would still surface as an `invalid value` warning if the
    # assumption above ever stopped holding.
    x, y, dists = sparse.find(knn_distances)
    with np.errstate(divide="ignore"):
        weights = np.exp(-dists / adaptive_std[x])

    W = sparse.csr_matrix((weights, (x, y)), shape=(n_obs, n_obs))
    kernel = W + W.T

    if alpha > 0:
        degree = np.ravel(kernel.sum(axis=1))
        degree[degree != 0] = degree[degree != 0] ** (-alpha)
        normalization = sparse.diags(degree)
        kernel = normalization @ kernel @ normalization

    return kernel.tocsr()


def neighbors(
    adata: AnnData,
    adaptive: bool = False,
    knn: int = 30,
    alpha: float = 0.0,
    obsm_key: str = "X_pca",
    key_added: str = "adaptive",
    random_state: int = 0,
    backend: Literal["scanpy", "rapids"] = "scanpy",
    copy: bool = False,
    **kwargs,
) -> AnnData | None:
    """Compute a neighbors graph, optionally using Palantir's adaptive anisotropic kernel.

    With `adaptive=False` (default), this is a plain pass-through to the backend's own `pp.neighbors`. With
    `adaptive=True`, the fixed-bandwidth kernel is replaced by Palantir's adaptive anisotropic kernel (Setty et al.
    2019) and stored under its own keys, so it can coexist with a plain neighbors graph on the same `adata`. `knn`,
    `alpha`, `obsm_key`, `key_added` and `random_state` only apply in that case; `kwargs` only in the other.

    Parameters
    ----------
    adata
        Annotated data matrix.
    adaptive
        Whether to build the adaptive anisotropic kernel instead of calling `sc.pp.neighbors` directly.
    knn
        Number of nearest neighbors used to build the adaptive kernel.
    alpha
        Density normalization exponent applied to the adaptive kernel; `0` disables it, matching Palantir's default.
    obsm_key
        Key of `adata.obsm` holding the embedding the adaptive kernel is built from.
    key_added
        Prefix under which the adaptive kernel is stored on `adata`. See Returns.
    random_state
        Random seed used for the kNN search underlying the adaptive kernel.
    backend
        Library computing the kNN graph: `"scanpy"` (CPU) or `"rapids"` (GPU, requires `rapids_singlecell`).
    copy
        Return a copy of `adata` instead of writing to it in place.
    kwargs
        Additional keyword arguments forwarded to `sc.pp.neighbors`/`rapids_singlecell.pp.neighbors`.

    Returns
    -------
    Returns `None` if `copy=False`, else the updated copy. With `adaptive=False`, sets the same fields as
    `sc.pp.neighbors`. With `adaptive=True`, sets `adata.obsp[f"{key_added}_connectivities"]` and
    `adata.uns[f"{key_added}_neighbors"]`, leaving any existing plain neighbors output untouched.
    """
    if backend not in ("scanpy", "rapids"):
        raise ValueError(f"`backend` needs to be `'scanpy'` or `'rapids'` but is `{backend!r}`.")

    if not adaptive:
        if backend == "scanpy":
            return sc.pp.neighbors(adata, copy=copy, **kwargs)
        elif backend == "rapids":
            import rapids_singlecell as rsc

            return rsc.pp.neighbors(adata, copy=copy, **kwargs)

    if obsm_key not in adata.obsm:
        raise KeyError(f"`{obsm_key}` not found in `adata.obsm`. Compute it first, e.g. via `sc.pp.pca`.")

    adata = adata.copy() if copy else adata
    kernel = _adaptive_kernel(adata.obsm[obsm_key], knn=knn, alpha=alpha, random_state=random_state, backend=backend)

    connectivities_key = f"{key_added}_connectivities"
    neighbors_key = f"{key_added}_neighbors"
    adata.obsp[connectivities_key] = kernel
    adata.uns[neighbors_key] = {
        "connectivities_key": connectivities_key,
        "distances_key": connectivities_key,
        "params": {"n_neighbors": knn, "method": "adaptive"},
    }

    if copy:
        return adata
