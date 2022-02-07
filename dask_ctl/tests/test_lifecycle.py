import ast

from dask.distributed import LocalCluster, Client

from dask_ctl.lifecycle import create_cluster, get_snippet


def test_create_cluster(simple_spec_path):
    cluster = create_cluster(simple_spec_path)

    assert isinstance(cluster, LocalCluster)


def test_snippet():
    with LocalCluster(scheduler_port=8786) as cluster:
        with Client(cluster) as client:
            client.wait_for_workers(1)

            snippet = get_snippet("proxycluster-8786")

            # Check is valid Python
            ast.parse(snippet)

            assert "ProxyCluster" in snippet
            assert "proxycluster-8786" in snippet
