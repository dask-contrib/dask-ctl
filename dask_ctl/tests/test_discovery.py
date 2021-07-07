import pytest

from typing import AsyncIterator

from dask.distributed import Client, LocalCluster
from dask_ctl.discovery import (
    discover_cluster_names,
    discover_clusters,
    list_discovery_methods,
)
from dask_ctl.proxy import discover


@pytest.mark.asyncio
async def test_discover_clusters():
    assert isinstance(discover_clusters(), AsyncIterator)
    async with LocalCluster(scheduler_port=8786, asynchronous=True) as cluster:
        [discovered_cluster] = [c async for c in discover_clusters()]
        assert discovered_cluster.scheduler_info == cluster.scheduler_info


def test_discovery_methods():
    assert "proxycluster" in list_discovery_methods()


@pytest.mark.asyncio
async def test_discover_cluster_names():
    assert isinstance(discover_cluster_names(), AsyncIterator)
    async with LocalCluster(scheduler_port=8786, asynchronous=True) as _:
        names = [name async for name in discover_cluster_names()]
        assert len(names) == 1


@pytest.mark.asyncio
async def test_cluster_client():
    port = 8786
    async with LocalCluster(scheduler_port=port, asynchronous=True) as _:
        async with Client(
            f"tcp://localhost:{port}", asynchronous=True, timeout=1
        ) as client:
            assert int(client.scheduler.address.split(":")[-1]) == port


@pytest.mark.asyncio
async def test_discovery_list():
    async with LocalCluster(scheduler_port=8786, asynchronous=True) as _:
        async for name, _ in discover():
            assert "_sched" in name
