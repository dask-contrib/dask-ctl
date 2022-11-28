dask-ctl
========


.. image:: https://img.shields.io/pypi/v/dask-ctl
   :target: https://pypi.org/project/dask-ctl/
   :alt: PyPI
.. image:: https://img.shields.io/readthedocs/dask-ctl
   :target: https://dask-ctl.readthedocs.io/
   :alt: Read the Docs
.. image:: https://github.com/dask-contrib/dask-ctl/workflows/Tests/badge.svg
   :target: https://github.com/dask-contrib/dask-ctl/actions?query=workflow%3ATests
   :alt: GitHub Actions - CI
.. image:: https://github.com/dask-contrib/dask-ctl/workflows/Linting/badge.svg
   :target: https://github.com/dask-contrib/dask-ctl/actions?query=workflow%3ALinting
   :alt: GitHub Actions - pre-commit
.. image:: https://img.shields.io/codecov/c/gh/dask-contrib/dask-ctl
   :target: https://app.codecov.io/gh/dask-contrib/dask-ctl
   :alt: Codecov

A set of tools to provide a control plane for managing the lifecycle of Dask clusters.

.. code-block:: bash

    $ dask cluster list
    NAME               ADDRESS               TYPE          WORKERS  THREADS  MEMORY    CREATED   STATUS
    proxycluster-8786  tcp://localhost:8786  ProxyCluster        4       12  17.18 GB  Just now  Running
