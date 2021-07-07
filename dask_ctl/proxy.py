from typing import Callable, AsyncIterator, Tuple
import asyncio

from zeroconf import (
    IPVersion,
    ServiceInfo,
    Zeroconf,
)
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf

from distributed.deploy.cluster import Cluster
from distributed.core import rpc, Status
from distributed.utils import LoopRunner


_ZC_SERVICE = "_dask._tcp.local."


class ProxyCluster(Cluster):
    """A representation of a cluster with a locally running scheduler.

    If a Dask Scheduler is running locally it is generally assumed that the process is tightly
    coupled to a parent process and therefore the cluster manager type cannot be reconstructed.
    The ProxyCluster object allows you limited interactivity with a local cluster in the same way
    you would with a regular cluster, allowing you to retrieve logs, get stats, etc.

    """

    @classmethod
    def from_name(
        cls, name: str, loop: asyncio.BaseEventLoop = None, asynchronous: bool = False
    ):
        """Get instance of ``ProxyCluster`` by name.

        Parameters
        ----------
        name
            Name of cluster to get ``ProxyCluster`` for. Has the format ``proxycluster-{port}``.
        loop (optional)
            Existing event loop to use.
        asynchronous (optional)
            Start asynchronously. Default ``False``.

        Returns
        -------
        ProxyCluster
            Instance of ProxyCluster.

        Examples
        --------
        >>> from dask.distributed import LocalCluster  # doctest: +SKIP
        >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
        >>> ProxyCluster.from_name("proxycluster-8786")  # doctest: +SKIP
        ProxyCluster(proxycluster-8786, 'tcp://localhost:8786', workers=4, threads=12, memory=17.18 GB)

        """

        cluster = cls(asynchronous=asynchronous)
        cluster.name = name

        # Get scheduler address via zeroconf
        zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        scheduler = ServiceInfo(_ZC_SERVICE, f"{name}._dask._tcp.local.")
        if not scheduler.request(zeroconf, 3000):
            raise RuntimeError("Unable to find cluster")
        addr = scheduler.parsed_addresses()[0]
        protocol = scheduler.properties[b"protocol"].decode("utf-8")
        cluster.scheduler_comm = rpc(f"{protocol}://{addr}:{scheduler.port}")
        zeroconf.close()

        cluster._loop_runner = LoopRunner(loop=loop, asynchronous=asynchronous)
        cluster.loop = cluster._loop_runner.loop
        if not asynchronous:
            cluster._loop_runner.start()

        cluster.status = Status.starting
        cluster.sync(cluster._start)
        return cluster


async def discover() -> AsyncIterator[Tuple[str, Callable]]:
    """Discover proxy clusters.

    If a Dask Scheduler is running locally it is generally assumed that the process is tightly
    coupled to a parent process and therefore the cluster manager type cannot be reconstructed.
    Instead we can construct ProxyCluster objects which allow limited interactivity with a local cluster in the same way
    you would with a regular cluster, allowing you to retrieve logs, get stats, etc.

    This doscovery works by checking all local services listening on ports, then attempting to connect a
    :class:`dask.distributed.Client` to it. If it is successful we assume it is a cluster that we can represent.

    Notes
    -----
    Listing open ports is not possible as a reular user on macOS. So discovery must be run as root. For regular users
    we still check the default ``8786`` port for a scheduler.

    Yields
    -------
    tuple
        Each tuple contains the name of the cluster and a class which can be used to represent it.

    Examples
    --------
    >>> from dask.distributed import LocalCluster  # doctest: +SKIP
    >>> cluster = LocalCluster(scheduler_port=8786)  # doctest: +SKIP
    >>> [name async for name in discover()]  # doctest: +SKIP
    [('proxycluster-8786', dask_ctl.proxy.ProxyCluster)]

    """
    aiozc = AsyncZeroconf(ip_version=IPVersion.V4Only)
    browser = AsyncServiceBrowser(
        aiozc.zeroconf, [_ZC_SERVICE], handlers=[lambda *args, **kw: None]
    )

    # ServiceBrowser runs in a thread. Give it a chance to find some schedulers.
    await asyncio.sleep(0.5)

    schedulers = [
        x.split(".")[0]
        for x in aiozc.zeroconf.cache.names()
        if x.endswith(_ZC_SERVICE) and x != _ZC_SERVICE
    ]

    for scheduler in schedulers:
        yield (
            scheduler,
            ProxyCluster,
        )

    await browser.async_cancel()
    await aiozc.async_close()
