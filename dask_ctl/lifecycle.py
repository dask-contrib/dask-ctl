import importlib
from typing import List

from dask.widgets import get_template
from dask.utils import typename
from distributed.deploy.cluster import Cluster
from .discovery import discover_cluster_names, discover_clusters
from .spec import load_spec
from .utils import loop


def create_cluster(spec_path: str) -> Cluster:
    """Create a cluster from a spec file.

    Parameters
    ----------
    spec_path
        Path to a cluster spec file.

    Returns
    -------
    Cluster
        Cluster manager representing the spec.

    Examples
    --------
    With the spec:

    .. code-block:: yaml

        # /path/to/spec.yaml
        version: 1
        module: "dask.distributed"
        class: "LocalCluster"

    >>> create_cluster("/path/to/spec.yaml")  # doctest: +SKIP
    LocalCluster(b3973c71, 'tcp://127.0.0.1:8786', workers=4, threads=12, memory=17.18 GB)

    """

    async def _create_cluster():
        cm_module, cm_class, args, kwargs = load_spec(spec_path)
        module = importlib.import_module(cm_module)
        cluster_manager = getattr(module, cm_class)

        kwargs = {key.replace("-", "_"): entry for key, entry in kwargs.items()}

        cluster = await cluster_manager(*args, **kwargs, asynchronous=True)
        cluster.shutdown_on_close = False
        return cluster

    return loop.run_sync(_create_cluster)


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


def get_cluster(name: str, asynchronous=False) -> Cluster:
    """Get a cluster by name.

    Parameters
    ----------
    name
        Name of cluster to get a cluster manager for.
    asynchronous
        Return an awaitable instead of starting a loop.

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

    if asynchronous:
        return _get_cluster()
    else:
        return loop.run_sync(_get_cluster)


def get_snippet(name: str) -> str:
    """Get a code snippet for connecting to a cluster.

    Parameters
    ----------
    name
        Name of cluster to get a snippet for.

    Returns
    -------
    str
        Code snippet.

    Examples
    --------
    >>> from dask.distributed import LocalCluster  # doctest: +SKIP
    >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
    >>> get_snippet("proxycluster-8786")  # doctest: +SKIP
    from dask.distributed import Client
    from dask_ctl.proxy import ProxyCluster

    cluster = ProxyCluster.from_name("proxycluster-8786")
    client = Client(cluster)

    """

    cluster = get_cluster(name)
    try:
        return cluster.get_snippet()
    except AttributeError:
        *module, cm = typename(type(cluster)).split(".")
        module = ".".join(module)
        return get_template("snippet.py.j2").render(
            module=module, cm=cm, name=name, cluster=cluster
        )


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

    return get_cluster(name).scale(n_workers)


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

    return get_cluster(name).close()
