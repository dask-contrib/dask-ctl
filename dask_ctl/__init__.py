from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from .discovery import (
    discover_cluster_names,
    discover_clusters,
    list_clusters,
    list_discovery_methods,
    get_cluster,
    scale_cluster,
    delete_cluster,
)
from .proxy import ProxyCluster
