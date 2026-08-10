from typing import Literal

from matplotlib.collections import PathCollection
from matplotlib.figure import Figure

import scanpy as sc
import scanpy.logging as logg
from anndata import AnnData


def plot_embedding(
    adata: AnnData,
    figsize: tuple[int, int] = (6, 6),
    aspect: list[Literal["auto", "equal"] | float] | Literal["auto", "equal"] | float = "auto",
    return_fig: bool = False,
    **kwargs,
) -> Figure | None:
    """Plot embedding and set figure size and aspect ratio.

    Parameters
    ----------
    adata
        Annotated data matrix.
    figsize
        Figure width and height in inches.
    aspect
        Aspect ratio of the Axes scaling, i.e. y/x-scale. Possible values:
        * "auto": fill the position rectangle with data.
        * "equal": same as aspect=1, i.e. same scaling for x and y.
        * float: The displayed size of 1 unit in y-data coordinates will be aspect times the displayed size of 1 unit in
            x-data coordinates; e.g. for aspect=2 a square in data coordinates will be rendered with a height of twice
            its width.
    return_fig
        Flag to return the matplotlib figure.
    kwargs
        Keyword arguments passed to Scanpy's `pl.embedding` function.


    Returns
    -------
    If `return_fig==True` the Matplotlib figure object.
    """
    if (
        ("color" in kwargs.keys())
        and not isinstance(kwargs["color"], str)
        and (len(kwargs["color"]) > 1)
        and (figsize[0] == figsize[1])
    ):
        figsize = (len(kwargs["color"]) * figsize[0], figsize[1])
    sort_order = kwargs.pop("sort_order", False)

    fig = sc.pl.embedding(adata, sort_order=sort_order, return_fig=True, **kwargs)

    fig.set_size_inches(*figsize)
    # scatter axes <-> PathCollection; colorbar axes <-> QuadMesh
    data_axes = [ax for ax in fig.get_axes() if any(isinstance(c, PathCollection) for c in ax.collections)]

    if isinstance(aspect, (str, float)):
        aspect = [aspect] * len(data_axes)
    elif len(data_axes) != len(aspect):
        logg.warning("The aspect list does not match the number of panels. Using `aspect='auto'` for all panels.")
        aspect = ["auto"] * len(data_axes)

    for ax, asp in zip(data_axes, aspect, strict=True):
        next(c for c in ax.collections if isinstance(c, PathCollection)).set_rasterized(True)
        # adjustable='box' shrinks the axes frame instead of adjusting data limits,
        ax.set_aspect(asp, adjustable="box")

    if return_fig:
        return fig
