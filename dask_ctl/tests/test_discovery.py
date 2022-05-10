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
        async for name, _ in discover():
            assert str(SCHEDULER_PORT) in name


@pytest.mark.asyncio
async def test_discover_clusters():
    with LocalCluster(scheduler_port=SCHEDULER_PORT) as cluster:
        discovered_names = [c.name async for c in discover_clusters()]
        assert cluster.name in discovered_names
