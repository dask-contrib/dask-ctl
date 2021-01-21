dask-ctl
========


.. image:: https://img.shields.io/pypi/v/dask-ctl
   :alt: PyPI

A set of tools to provide a control plane for managing the lifecycle of Dask clusters.

.. code-block:: bash

    $ daskctl list
    NAME               ADDRESS               TYPE          WORKERS  THREADS  MEMORY    CREATED   STATUS
    proxycluster-8786  tcp://localhost:8786  ProxyCluster        4       12  17.18 GB  Just now  Running