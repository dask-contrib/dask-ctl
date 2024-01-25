from typing import Callable, AsyncIterator, Tuple
import asyncio
import contextlib

# import psutil

from distributed.deploy.cluster import Cluster
from distributed.core import rpc, Status
from distributed.client import Client
from distributed.utils import LoopRunner


def gen_name(port):
    return f"proxycluster-{port}"


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
        port = name.split("-")[-1]
        return cls.from_port(port, loop=loop, asynchronous=asynchronous)

    @classmethod
    def from_port(
        cls, port: int, loop: asyncio.BaseEventLoop = None, asynchronous: bool = False
    ):
        """Get instance of ``ProxyCluster`` by port.

        Parameters
        ----------
        port
            Localhost port of cluster to get ``ProxyCluster`` for.
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
        >>> cluster = LocalCluster(scheduler_port=81234)  # doctest: +SKIP
        >>> ProxyCluster.from_port(81234)  # doctest: +SKIP
        ProxyCluster(proxycluster-81234, 'tcp://localhost:81234', workers=4, threads=12, memory=17.18 GB)

        """
        cluster = cls(asynchronous=asynchronous)
        cluster.name = gen_name(port)

        cluster.scheduler_comm = rpc(f"tcp://localhost:{port}")

        cluster._loop_runner = LoopRunner(loop=loop, asynchronous=asynchronous)
        cluster.loop = cluster._loop_runner.loop
        if not asynchronous:
            cluster._loop_runner.start()

        cluster.status = Status.starting
        cluster.sync(cluster._start)
        return cluster

    def scale(self, *args, **kwargs):
        raise TypeError("Scaling of ProxyCluster objects is not supported.")

    def close(self, *args, **kwargs):
        raise TypeError("Closing of ProxyCluster objects is not supported.")

    def __await__(self):
        async def _():
            return self

        return _().__await__()


async def discover() -> AsyncIterator[Tuple[str, Callable]]:
    """Discover proxy clusters.

    If a Dask Scheduler is running locally it is generally assumed that the process is tightly
    coupled to a parent process and therefore the cluster manager type cannot be reconstructed.
    Instead we can construct ProxyCluster objects which allow limited interactivity with a local cluster in the same way
    you would with a regular cluster, allowing you to retrieve logs, get stats, etc.

    This discovery works by checking all local services listening on ports, then attempting to connect a
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
    open_ports = {8786}

    # with contextlib.suppress(
    #     psutil.AccessDenied
    # ):  # On macOS this needs to be run as root
    #     connections = psutil.net_connections()
    #     for connection in connections:
    #         if (
    #             connection.status == "LISTEN"
    #             and connection.family.name == "AF_INET"
    #             and connection.laddr.port not in open_ports
    #         ):
    #             open_ports.add(connection.laddr.port)

    async def try_connect(port):
        with contextlib.suppress(OSError, asyncio.TimeoutError):
            async with Client(
                f"tcp://localhost:{port}",
                asynchronous=True,
                timeout=1,  # Minimum of 1 for Windows
            ):
                return port
        return

    for port in await asyncio.gather(*[try_connect(port) for port in open_ports]):
        if port:
            yield (
                gen_name(port),
                ProxyCluster,
            )
