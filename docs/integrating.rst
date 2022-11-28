Adding dask-ctl support to your project
=======================================

``dask-ctl`` is an opt-in utility package for managing Dask cluster lifecycles.

In order for a cluster manager to work with ``dask-ctl`` it must have the following things:

- A discovery method registered as an entrypoint
- A ``from_name`` class method which reconstructs the cluster manager

Discovery
---------

In order for cluster to be visible in ``dask-ctl`` the cluster manager which created it must implement a ``discovery``
method and register it as an ``dask_cluster_discovery`` entrypoint.

.. code-block:: python

    import setuptools

    setuptools.setup(
        ...
        entry_points="""
            [dask_cluster_discovery]
            mycluster=my_package.discovery:discover
        """,
    )

This method must be an async generator which returns tuples of the cluster name and a class which can be used to reconstruct it.

.. code-block:: python

    from typing import Callable, AsyncIterator, Tuple

    from my_package.cluster import MyClusterManager  # A cluster manager class which supports the ``from_name`` classmethod


    async def discover() -> AsyncIterator[Tuple[str, Callable]]:

        # Discover cluster names in whatever way is appropriate
        cluster_names = [...]

        for cluster_name in cluster_names:
            yield (cluster_name, MyClusterManager)

From name
---------

When ``dask-ctl`` discovers clusters it iterates through all the registered discovery methods and constructs a list of
name/cluster manager pairs.

Then when making calls such as ``get_cluster`` it will attempt to call the ``from_name`` class method on the cluster manager
and pass in the name that was provided during discovery.

Cluster managers are contructed from name during almost all ``dask-ctl`` operations. Even calling ``dask cluster list`` on the CLI
will create all cluster managers in order to query information about them such as number of workers and resources via the scheduler comm.

Implementation of this method will vary drastically depending on how the cluster manager is implemented. But the interface should take the
``name`` argument and contruct a cluster manager class and return it.

.. code-block:: python

    from distributed.deploy.cluster import Cluster

    class MyClusterManager(Cluster):

        ...

        @classmethod
        def from_name(
            cls, name: str, loop: asyncio.BaseEventLoop = None, asynchronous: bool = False
        ):
            cluster = cls(name=name, asynchronous=asynchronous)

            # Connect to the scheduler comm
            cluster.scheduler_comm = rpc(...)

            # Put the cluster manager into a started and running state
            ...

            return cluster


Testing integration
-------------------

A useful test to ensure your cluster manager will be compliant with ``dask-ctl`` would be to follow these steps:

- Create a cluster using your cluster manager class
- Record the name of that cluster
- Run ``dask-ctl`` discovery and ensure the cluster is listed
- Ensure the cluster is not created when the cluster manager is destroyed
- Delete the cluster manager object
- Recreate the cluster manager object from the name
- Check that the cluster is working as expected

.. code-block:: python

    import pytest

    from dask.distributed import Client
    from dask_ctl.discovery import (
        list_discovery_methods,
        discover_cluster_names,
    )

    from my_package.cluster import MyClusterManager

    @pytest.mark.asyncio
    async def test_from_name():
        # Create cluster
        cluster = await MyClusterManager(*args, **kwargs)
        await cluster.scale(1)
        name = cluster.name

        # Check cluster listed in discovery
        discovery = "mycluster"
        assert discovery in list_discovery_methods()
        clusters_names = [
            cluster async for cluster in discover_cluster_names(discovery=discovery)
        ]
        assert len(clusters_names) == 1
        discovered_name, discovered_class = cluster_names[0]
        assert discovered_name == name
        assert discovered_class == MyClusterManager

        # Delete cluster manager
        cluster.shutdown_on_close = False
        del cluster

        # Recreate cluster manager from name
        cluster = await MyClusterManager.from_name(name, asynchronous=True)
        assert "id" in cluster.scheduler_info
        assert cluster.status == Status.running

        # Ensure work can be run on cluster
        async with Client(cluster, asynchronous=True) as client:
            # Ensure that inter-worker communication works well
            futures = client.map(lambda x: x + 1, range(10))
            total = client.submit(sum, futures)
            assert (await total) == sum(map(lambda x: x + 1, range(10)))
            assert all((await client.has_what()).values())

