Cluster specs
=============

``dask-ctl`` can create Dask clusters for you from spec files.

These files describe the Python cluster manager which should be used along with any arguments.

.. code-block:: yaml

    # /path/to/spec.yaml
    version: 1
    module: "dask.distributed"
    class: "LocalCluster"
    args: []
    kwargs:
        n_workers: 2
        threads_per_worker: 1
        memory_limit: '1GB'

You can then create the cluster from the command line.

.. code-block:: bash

    $ dask cluster create -f /path/to/spec.yaml

Or using the Python API.

.. code-block:: python

    from dask_ctl import create_cluster

    cluster = create_cluster("/path/to/spec.yaml")

Both of these examples are equivalent to running the following Python code.

.. code-block:: python

    from dask.distributed import LocalCluster

    cluster = LocalCluster(n_workers=2, threads_per_worker=1, memory_limit='1GB')
