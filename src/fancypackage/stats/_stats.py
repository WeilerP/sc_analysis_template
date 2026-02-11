import numpy as np
from numpy.typing import NDArray
from scipy.stats import median_abs_deviation


def is_outlier(adata, obs_column: str, nmads: int) -> NDArray:
    r"""Identifies outlier observations based on median absolute deviations.

    For a given feature :math:`x_j` of observation :math:`j`, the median absolute deviation (MAD) is defined as

    .. math::
        \text{MAD} = \left\lVert x_j - \text{median}(x) \right\rVert.

    Parameters
    ----------
    adata
        Annotated data matrix.
    obs_column
        Column name of `adata.obs` containing feature to compute outliers for.
    nmads
        Number of MADs beyond which an observation is labelled an outlier.

    Returns
    -------
    Boolean array of size (n_obs,) that labels outlier observations.
    """
    M = adata.obs[obs_column].values
    outlier = (M < np.median(M) - nmads * median_abs_deviation(M)) | (
        np.median(M) + nmads * median_abs_deviation(M) < M
    )
    return outlier
