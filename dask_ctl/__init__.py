from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from .discovery import (
    discover_cluster_names,
    discover_clusters,
    list_discovery_methods,
)
from .lifecycle import (
    get_cluster,
    scale_cluster,
    delete_cluster,
    list_clusters,
)
from .proxy import ProxyCluster
