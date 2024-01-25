import asyncio
from typing import Callable, Dict, AsyncIterator, Tuple
from contextlib import suppress
import pkg_resources
import warnings

import dask.config
from distributed.deploy.spec import SpecCluster

from .utils import AsyncTimedIterable


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
    >>> list(list_discovery_methods())  # doctest: +SKIP
    ['proxycluster']

    """
    discovery_methods = {}
    for ep in pkg_resources.iter_entry_points(group="dask_cluster_discovery"):
        with suppress(AttributeError, ImportError):
            discovery_methods.update(
                {
                    ep.name: {
                        "discover": ep.load(),
                        "package": ep.dist.key,
                        "version": ep.dist.version,
                        "path": ep.dist.location,
                        "enabled": (
                            not dask.config.get("ctl.disable_discovery")
                            or ep.name not in dask.config.get("ctl.disable_discovery")
                        ),
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
            if discovery_methods[discovery_method]["enabled"] and (
                discovery is None or discovery == discovery_method
            ):
                try:
                    async for cluster_name, cluster_class in AsyncTimedIterable(
                        discovery_methods[discovery_method]["discover"](), 5
                    ):
                        yield (cluster_name, cluster_class)
                    if discovery is not None:
                        return
                except asyncio.TimeoutError:
                    warnings.warn(
                        f"Cluster discovery for {discovery_method} timed out."
                    )
        except (
            Exception
        ) as e:  # We are calling code that is out of our control here, so handling broad exceptions
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
