from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from . import config

from .discovery import (
    discover_cluster_names,
    discover_clusters,
    list_discovery_methods,
)
from .lifecycle import (
    get_cluster,
    create_cluster,
    scale_cluster,
    delete_cluster,
    list_clusters,
    get_snippet,
)
from .proxy import ProxyCluster

import os.path

from dask.widgets import TEMPLATE_PATHS

TEMPLATE_PATHS.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "templates")
)
