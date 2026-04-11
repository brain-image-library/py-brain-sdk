"""
brainimagelibrary
"""

__version__ = "0.0.23"
__author__ = "Ivan Cao-Berg"
__credits__ = "Brain Image Library Team"

from .retrieve import by_id, by_directory, by_url, by_version
from . import metadata
from .metadata import *
from .reports import *
from .inventory import *
from .datecite import *
from .summary import *

__all__ = [
    # version info
    "__version__",
    "__author__",
    "__credits__",
    # submodules
    "metadata",
    # retrieve shortcuts
    "by_id",
    "by_directory",
    "by_url",
    "by_version",
    # inventory
    "summary",
    "DatasetInventory",
    "to_manifest",
    "has",
    "get",
    # reports
    "daily",
    "get_all_bildids",
    # datecite
    "Dataset",
    "Collection",
    "dataset",
    "collection",
    "get_datacite_metadata",
    "get_datacite_citations",
    "get_number_of_citations",
    # summary
    "load",
]
