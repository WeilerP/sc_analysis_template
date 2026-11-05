from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from scipy.stats import median_abs_deviation

if TYPE_CHECKING:
    from typing import Literal


def is_outlier(adata, obs_column: str, nmads: int, tail: Literal["left", "right", "both"] = "both") -> NDArray:
    r"""Identify outlier observations based on median absolute deviations.

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
    stat = adata.obs[obs_column].values
    median = np.median(stat)
    deviation = nmads * median_abs_deviation(stat)
    if tail == "right":
        return stat > median + deviation
    elif tail == "left":
        return stat < median - deviation
    elif tail == "both":
        return (stat < median - deviation) | (stat > median + deviation)
    else:
        raise ValueError(f"tail=`{tail}` is not supported; valid values: `'left'`, `'right'`, and `'both'` (default)")
