import pytest
import ast

import dask.config
from dask.distributed import LocalCluster

from dask_ctl.lifecycle import create_cluster, get_snippet
from dask_ctl.exceptions import DaskClusterConfigNotFound


def test_create_cluster(simple_spec_path):
    cluster = create_cluster(simple_spec_path)

    assert isinstance(cluster, LocalCluster)


def test_create_cluster_fallback():
    with pytest.raises(DaskClusterConfigNotFound, match="dask-cluster.yaml"):
        cluster = create_cluster()

    with dask.config.set({"ctl.cluster-spec": "foo.yaml"}):
        with pytest.raises(DaskClusterConfigNotFound, match="foo.yaml"):
            cluster = create_cluster()

    cluster = create_cluster(local_fallback=True)
    assert isinstance(cluster, LocalCluster)


@pytest.mark.xfail(reason="Proxy cluster discovery not working")
def test_snippet():
    with LocalCluster(scheduler_port=8786) as _:
        snippet = get_snippet("proxycluster-8786")

        # Check is valid Python
        ast.parse(snippet)

        assert "proxycluster-8786" in snippet
