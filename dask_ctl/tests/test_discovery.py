import pytest

from typing import AsyncIterator

from dask.distributed import LocalCluster
from dask_ctl.discovery import (
    discover_cluster_names,
    discover_clusters,
    list_discovery_methods,
)

SCHEDULER_PORT = 8786


def test_discovery_methods():
    assert "proxycluster" in list_discovery_methods()


@pytest.mark.asyncio
async def test_discover_cluster_names():
    assert isinstance(discover_cluster_names(), AsyncIterator)
    async with LocalCluster(scheduler_port=SCHEDULER_PORT, asynchronous=True) as _:
        count = 0
        async for _ in discover_cluster_names():
            count += 1
        assert count == 1


@pytest.mark.asyncio
async def test_cluster_client():
    from dask.distributed import Client

    async with LocalCluster(scheduler_port=SCHEDULER_PORT, asynchronous=True) as _:
        async with Client(
            f"tcp://localhost:{SCHEDULER_PORT}", asynchronous=True, timeout=1
        ) as client:
            assert int(client.scheduler.address.split(":")[-1]) == SCHEDULER_PORT


@pytest.mark.asyncio
async def test_discovery_list():
    from dask_ctl.proxy import discover

    async with LocalCluster(scheduler_port=SCHEDULER_PORT, asynchronous=True) as _:
        discovered_cluster_names = [name async for name, _ in discover()]
        assert discovered_cluster_names
        for name in discovered_cluster_names:
            assert str(SCHEDULER_PORT) in name


@pytest.mark.xfail(reason="Proxy cluster discovery not working")
@pytest.mark.asyncio
async def test_discover_clusters():
    async with LocalCluster(
        scheduler_port=SCHEDULER_PORT, asynchronous=True
    ) as cluster:
        discovered_clusters = [cluster async for cluster in discover_clusters()]
        assert discovered_clusters
        assert cluster.name in [c.name for c in discovered_clusters]
