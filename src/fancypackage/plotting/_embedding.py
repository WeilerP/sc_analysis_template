from typing import Literal

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
    fig = sc.pl.embedding(adata, return_fig=True, **kwargs)

    fig.set_size_inches(*figsize)
    axes = fig.get_axes()
    if len(axes) > 0 and isinstance(aspect, (str, float)):
        aspect = [aspect] * len(axes)
    elif len(axes) != len(aspect):
        logg.warning("The aspect list is shorter than the number of panels. Using `aspect='auto'` for all panels.")
        aspect["auto"] * len(axes)

    for ax_id, ax in enumerate(axes):
        ax.collections[0].set_rasterized(True)
        ax.set_aspect(aspect[ax_id])

    if return_fig:
        return fig
