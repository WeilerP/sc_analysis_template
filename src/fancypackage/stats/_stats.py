import numpy as np
from numpy.typing import ArrayLike
from scipy.stats import median_abs_deviation


def is_outlier(adata, obs_column: str, nmads: int) -> ArrayLike:
    M = adata.obs[obs_column].values
    outlier = (M < np.median(M) - nmads * median_abs_deviation(M)) | (
        np.median(M) + nmads * median_abs_deviation(M) < M
    )
    return outlier
