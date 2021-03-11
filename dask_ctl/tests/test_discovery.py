import pytest

from typing import AsyncIterator

from distributed import LocalCluster
from dask_ctl.discovery import (
    discover_cluster_names,
    discover_clusters,
    list_discovery_methods,
)
from dask_ctl.proxy import ProxyCluster


def test_discovery_methods():
    assert "proxycluster" in list_discovery_methods()


@pytest.mark.asyncio
async def test_discover_cluster_names():
    assert isinstance(discover_cluster_names(), AsyncIterator)
    async with LocalCluster(scheduler_port=8786, asynchronous=True) as _:
        count = 0
        async for _ in discover_cluster_names():
            count += 1
        assert count == 1


@pytest.mark.asyncio
async def test_cluster_client():
    from dask.distributed import Client

    port = 8786
    async with LocalCluster(scheduler_port=port, asynchronous=True) as _:
        async with Client(
            f"tcp://localhost:{port}", asynchronous=True, timeout=1
        ) as client:
            assert int(client.scheduler.address.split(":")[-1]) == port


@pytest.mark.asyncio
async def test_discovery_list():
    from dask_ctl.proxy import discover

    port = 8786
    async with LocalCluster(scheduler_port=port, asynchronous=True) as _:
        async for name, _ in discover():
            assert str(port) in name


@pytest.mark.asyncio
async def test_discover_clusters():
    with LocalCluster() as cluster:
        async for discovered_cluster in discover_clusters():
            if isinstance(discovered_cluster, ProxyCluster):
                assert cluster.scheduler_info == discovered_cluster.scheduler_info
