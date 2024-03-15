"""An unofficial Python client library for Bitkub API

"""

__version__ = "0.0.1"

from .client import Client  # noqa: F401
from .exception import BitkubException  # noqa: F401

__all__ = ["Client", "BitkubException"]
