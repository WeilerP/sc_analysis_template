# Adapted from https://github.com/adamgayoso/mplscience/tree/main/mplscience/_styledata
from collections.abc import Iterable

import matplotlib

_default = {
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "savefig.transparent": True,
    "figure.figsize": (4, 4),
    "axes.titlesize": 12,
    "axes.titlepad": 8.0,
    "axes.labelsize": 12,
    "axes.linewidth": 1.2,
    "axes.labelpad": 6.0,
    "font.size": 12,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Computer Modern Sans Serif", "DejaVU Sans"],
    "xtick.labelsize": 12,
    "xtick.minor.size": 1.375,
    "xtick.major.size": 2.75,
    "xtick.major.pad": 2,
    "xtick.minor.pad": 2,
    "ytick.labelsize": 12,
    "ytick.minor.size": 1.375,
    "ytick.major.size": 2.75,
    "ytick.major.pad": 2,
    "ytick.minor.pad": 2,
    "legend.fontsize": 12,
    "legend.handlelength": 1.4,
    "legend.numpoints": 1,
    "legend.scatterpoints": 1,
    "legend.frameon": False,
    "lines.linewidth": 1.7,
}

_despine = {
    "axes.spines.top": False,
    "axes.spines.right": False,
}

STYLES = {"default": _default, "despine": _despine}


def style_context(
    context: str | dict | Iterable[str | dict] = ("default", "despine"), reset_current: bool = False, **kwargs
):
    """Create a style context for plotting.

    Parameters
    ----------
    context
        Style name(s) or settings to apply. Available: "default", "despine".
    reset_current
        Reset any custom styling before applying the context.
    kwargs
        Optional keyword arguments. To set specific rcparams, pass them as a dictionary via the `rcparams` argument.

    Returns
    -------
    A matplotlib rc_context with the selected style(s).
    """
    rcparams = {}
    context = [context] if isinstance(context, (str, dict)) else context

    if reset_current:
        from seaborn import reset_orig

        reset_orig()

    for spec in context:
        if isinstance(spec, str) and (spec not in STYLES):
            raise ValueError(f"Style '{spec}' not found. Available: {', '.join(f"'{style}'" for style in STYLES)}")
        elif isinstance(spec, str):
            rcparams.update(STYLES[spec])
        else:
            rcparams.update(spec)
    if "rcparams" in kwargs:
        rcparams.update(kwargs["rcparams"])

    return matplotlib.rc_context(rcparams)
