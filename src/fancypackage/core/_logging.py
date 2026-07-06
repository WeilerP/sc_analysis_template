import logging


def get_logger(name: str = "fancypackage", level: int = logging.INFO) -> logging.Logger:
    """Return an idempotent, timestamped ``fancypackage`` logger.

    Parameters
    ----------
    name
        Name of the logger to configure and return. Since the standard library
        memoizes loggers by name, the default always yields the same instance.
    level
        Logging level applied on first configuration.

    Returns
    -------
    Configured logger. Repeated calls return the same instance without adding
    duplicate handlers.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
