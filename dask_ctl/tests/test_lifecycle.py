import pytest

from dask.distributed import LocalCluster

from dask_ctl.lifecycle import create_cluster


@pytest.mark.asyncio
async def test_create_cluster(simple_spec_path):
    cluster = await create_cluster(simple_spec_path)

    assert isinstance(cluster, LocalCluster)
