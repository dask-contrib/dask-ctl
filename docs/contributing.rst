Contributing
============

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

Documentation
-------------

This project uses ``sphinx`` to build its documentation.

.. code-block:: bash

   $ pip install -r docs/requirements_docs.txt
   $ sphinx-autobuild docs docs/_build/html
   # Visit http://localhost:8000 in your browser
