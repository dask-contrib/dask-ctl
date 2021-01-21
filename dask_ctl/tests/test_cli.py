from distributed import LocalCluster
from subprocess import check_output
from dask_ctl.cli import autocomplete_cluster_names


def test_list_discovery():
    assert b"proxycluster" in check_output(["daskctl", "list-discovery"])


def test_list():
    with LocalCluster(name="testcluster", scheduler_port=8786) as _:
        output = check_output(["daskctl", "list"])
        assert b"ProxyCluster" in output
        assert b"Running" in output


def test_autocompletion():
    with LocalCluster(scheduler_port=8786) as _:
        assert len(autocomplete_cluster_names(None, None, "")) == 1
        assert len(autocomplete_cluster_names(None, None, "proxy")) == 1
        assert len(autocomplete_cluster_names(None, None, "local")) == 0