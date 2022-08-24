dask-ctl
========


.. image:: https://img.shields.io/pypi/v/dask-ctl
   :target: https://pypi.org/project/dask-ctl/
   :alt: PyPI
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

Installation
------------

.. code-block:: bash

   pip install dask-ctl
   # or
   conda install -c conda-forge dask-ctl


.. toctree::
   :maxdepth: 2
   :caption: Usage

   cli.rst
   api.rst
   configuration.rst
   spec.rst

.. toctree::
   :maxdepth: 2
   :caption: Integrating

   integrating.rst

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing.rst
   releasing.rst

