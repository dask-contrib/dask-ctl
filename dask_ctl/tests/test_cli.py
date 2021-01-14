from distributed import LocalCluster
from subprocess import check_output


def test_list_discovery():
    assert b"proxycluster" in check_output(["daskctl", "list-discovery"])


def test_list():
    with LocalCluster(name="testcluster", scheduler_port=8786) as _:
        output = check_output(["daskctl", "list"])
        assert b"ProxyCluster" in output
        assert b"Running" in output