from distributed import LocalCluster
from subprocess import check_output
from dask_ctl.cli import autocomplete_cluster_names


def test_list_discovery():
    assert b"proxycluster" in check_output(["daskctl", "discovery", "list"])


def test_list():
    with LocalCluster(name="testcluster", scheduler_port=8786) as _:
        output = check_output(["daskctl", "cluster", "list"])
        assert b"ProxyCluster" in output
        assert b"Running" in output


def test_create(simple_spec_path):
    output = check_output(["daskctl", "cluster", "create", "-f", simple_spec_path])
    assert b"Created" in output


def test_autocompletion():
    with LocalCluster(scheduler_port=8786) as _:
        names = autocomplete_cluster_names(None, None, "")
        assert len(names) == 1
        assert "_sched" in names[0]
        assert len(autocomplete_cluster_names(None, None, "local")) == 0
