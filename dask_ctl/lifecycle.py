from typing import List

from distributed.deploy.cluster import Cluster
from .discovery import discover_cluster_names, discover_clusters
from .utils import loop


def list_clusters() -> List[Cluster]:
    """List all clusters.

    Discover clusters and return a list of cluster managers representing each one.

    Returns
    -------
    list
        List of cluster manager classes for each discovered cluster.

    Examples
    --------
    >>> from dask.distributed import LocalCluster  # doctest: +SKIP
    >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
    >>> list_clusters()  # doctest: +SKIP
    [ProxyCluster(proxycluster-8786, 'tcp://localhost:8786', workers=4, threads=12, memory=17.18 GB)]

    """

    async def _list_clusters():
        clusters = []
        async for cluster in discover_clusters():
            clusters.append(cluster)
        return clusters

    return loop.run_sync(_list_clusters)


def get_cluster(name: str) -> Cluster:
    """Get a cluster by name.

    Parameters
    ----------
    name
        Name of cluster to get a cluster manager for.

    Returns
    -------
    Cluster
        Cluster manager representing the named cluster.

    Examples
    --------
    >>> from dask.distributed import LocalCluster  # doctest: +SKIP
    >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
    >>> get_cluster("proxycluster-8786")  # doctest: +SKIP
    ProxyCluster(proxycluster-8786, 'tcp://localhost:8786', workers=4, threads=12, memory=17.18 GB)

    """

    async def _get_cluster():
        async for cluster_name, cluster_class in discover_cluster_names():
            if cluster_name == name:
                return cluster_class.from_name(name)
        raise RuntimeError("No such cluster %s", name)

    return loop.run_sync(_get_cluster)


def scale_cluster(name: str, n_workers: int) -> None:
    """Scale a cluster by name.

    Constructs a cluster manager for the named cluster and calls
    ``.scale(n_workers)`` on it.

    Parameters
    ----------
    name
        Name of cluster to scale.
    n_workers
        Number of workers to scale to

    Examples
    --------
    >>> scale_cluster("mycluster", 10)  # doctest: +SKIP

    """

    async def _scale_cluster():
        async for cluster_name, cluster_class in discover_cluster_names():
            if cluster_name == name:
                return cluster_class.from_name(name).scale(n_workers)
        raise RuntimeError("No such cluster %s", name)

    return loop.run_sync(_scale_cluster)


def delete_cluster(name: str) -> None:
    """Close a cluster by name.

    Constructs a cluster manager for the named cluster and calls
    ``.close()`` on it.

    Parameters
    ----------
    name
        Name of cluster to close.

    Examples
    --------
    >>> delete_cluster("mycluster")  # doctest: +SKIP

    """

    async def _delete_cluster():
        async for cluster_name, cluster_class in discover_cluster_names():
            if cluster_name == name:
                return cluster_class.from_name(name).close()
        raise RuntimeError("No such cluster %s", name)

    return loop.run_sync(_delete_cluster)
