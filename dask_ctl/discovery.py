from typing import Callable, Dict, AsyncIterator, Tuple, List
from contextlib import suppress
import pkg_resources
import warnings

from tornado.ioloop import IOLoop

from distributed.deploy.cluster import Cluster
from distributed.deploy.spec import SpecCluster


def list_discovery_methods() -> Dict[str, Callable]:
    """Lists registered discovery methods.

    Dask cluster discovery methods are registered via the ``dask_cluster_discovery`` entrypoint.
    This function lists all methods registered via that entrypoint.

    Returns
    -------
    dict
        A mapping of discovery methods containing the functions themselves and metadata about
        where they came from.

    Examples
    --------
    >>> list_discovery_methods()  # doctest: +SKIP
    {'proxycluster': {
        'discover': <function dask_ctl.proxy.discover()>,
        'package': 'dask-ctl',
        'version': '<package version>',
        'path': '<path to package>'}
    }
    >>> list(list_discovery_methods())
    ['proxycluster']

    """
    discovery_methods = {}
    for ep in pkg_resources.iter_entry_points(group="dask_cluster_discovery"):
        with suppress(AttributeError):
            discovery_methods.update(
                {
                    ep.name: {
                        "discover": ep.load(),
                        "package": ep.dist.key,
                        "version": ep.dist.version,
                        "path": ep.dist.location,
                    }
                }
            )
    return discovery_methods


async def discover_cluster_names(
    discovery: str = None,
) -> AsyncIterator[Tuple[str, Callable]]:
    """Generator to discover cluster names.

    Cluster discovery methods are asynchronous. This async generator iterates through
    each discovery method and then iterates through each cluster name discovered.

    Can also be restricted to a specific disovery method.

    Parameters
    ----------
    discovery
        Discovery method to use, as listed in :func:`list_discovery_methods`.
        Default is ``None`` which uses all discovery methods.

    Yields
    -------
    tuple
        Each tuple contains the name of the cluster and a class which can be used to represent it.

    Examples
    --------
    >>> from dask.distributed import LocalCluster  # doctest: +SKIP
    >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
    >>> [name async for name in discover_cluster_names()]  # doctest: +SKIP
    [('proxycluster-8786', dask_ctl.proxy.ProxyCluster)]

    """
    discovery_methods = list_discovery_methods()
    for discovery_method in discovery_methods:
        try:
            if discovery is None or discovery == discovery_method:
                async for cluster_name, cluster_class in discovery_methods[
                    discovery_method
                ]["discover"]():
                    yield (cluster_name, cluster_class)
                if discovery is not None:
                    return
        except Exception as e:  # We are calling code that is out of our control here, so handling broad exceptions
            if discovery is None:
                warnings.warn(f"Cluster discovery for {discovery_method} failed.")
            else:
                raise e


async def discover_clusters(discovery=None) -> AsyncIterator[SpecCluster]:
    """Generator to discover clusters.

    This generator takes the names and classes output from :func:`discover_cluster_names`
    and constructs the cluster object using the `cls.from_name(name)` classmethod.

    Can also be restricted to a specific disovery method.

    Parameters
    ----------
    discovery
        Discovery method to use, as listed in :func:`list_discovery_methods`.
        Default is ``None`` which uses all discovery methods.

    Yields
    -------
    Cluster
        Cluster manager classes for each discovered cluster.

    Examples
    --------
    >>> from dask.distributed import LocalCluster  # doctest: +SKIP
    >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
    >>> [name async for name in discover_clusters()]  # doctest: +SKIP
    [ProxyCluster(proxycluster-8786, 'tcp://localhost:8786', workers=4, threads=12, memory=17.18 GB)]

    """
    async for cluster_name, cluster_class in discover_cluster_names(discovery):
        with suppress(Exception):
            yield cluster_class.from_name(cluster_name)


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
    loop = IOLoop.current()

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
    loop = IOLoop.current()

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
    loop = IOLoop.current()

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
    loop = IOLoop.current()

    async def _delete_cluster():
        async for cluster_name, cluster_class in discover_cluster_names():
            if cluster_name == name:
                return cluster_class.from_name(name).close()
        raise RuntimeError("No such cluster %s", name)

    return loop.run_sync(_delete_cluster)
