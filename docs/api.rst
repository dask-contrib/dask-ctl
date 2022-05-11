Python API
==========

.. currentmodule:: dask_ctl

Lifecycle
---------

Dask Control has a selection of lifecycle functions that can be used within Python to manage
your Dask clusters. You can list clusters, get instances of an existing cluster, create new ones, scale and delete them.

You can either use these in a regular synchronous way by importing them from ``dask_ctl``.

.. code-block:: python

      from dask_ctl import list_clusters

      clusters = list_clusters()

Or alternatively you can use them in async code by importing from the ``dask_ctl.asyncio`` submodule.

.. code-block:: python

      from dask_ctl.asyncio import list_clusters

      clusters = await list_clusters()

.. autosummary::
    get_cluster
    create_cluster
    scale_cluster
    delete_cluster
    list_clusters

.. autofunction:: get_cluster

.. autofunction:: create_cluster

.. autofunction:: scale_cluster

.. autofunction:: delete_cluster

.. autofunction:: list_clusters

.. autofunction:: get_snippet

Discovery
---------

.. autosummary::
    discover_cluster_names
    discover_clusters
    list_discovery_methods

.. autofunction:: discover_cluster_names

.. autofunction:: discover_clusters

.. autofunction:: list_discovery_methods
