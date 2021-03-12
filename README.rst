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

    $ daskctl cluster list
    NAME               ADDRESS               TYPE          WORKERS  THREADS  MEMORY    CREATED   STATUS
    proxycluster-8786  tcp://localhost:8786  ProxyCluster        4       12  17.18 GB  Just now  Running

Developing
----------

This project uses ``black`` to format code and ``flake8`` for linting. We also support ``pre-commit`` to ensure
these have been run. To configure your local environment please install these development dependencies and set up
the commit hooks.

.. code-block:: bash

   $ pip install black flake8 pre-commit
   $ pre-commit install

Testing
-------

This project uses ``pytest`` to run tests and also to test docstring examples.

Install the test dependencies.

.. code-block:: bash

   $ pip install -r requirements-test.txt

Run the tests.

.. code-block:: bash

   $ pytest
   === 3 passed in 0.13 seconds ===

Releasing
---------

Releases are published automatically when a tag is pushed to GitHub.

.. code-block:: bash

   # Set next version number
   export RELEASE=x.x.x

   # Create tags
   git commit --allow-empty -m "Release $RELEASE"
   git tag -a $RELEASE -m "Version $RELEASE"

   # Push
   git push upstream --tags
