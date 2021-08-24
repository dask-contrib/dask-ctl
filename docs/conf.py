# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import datetime
import dask_sphinx_theme
from dask_ctl import __version__

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import dask
import os
import sys

# Add the Dask config extension
sys.path.insert(
    0, os.path.join(os.path.abspath(dask.__path__[0]), "..", "docs", "source", "ext")
)


# -- Project information -----------------------------------------------------

project = "dask-ctl"
copyright = f"{datetime.now().year}, Dask Developers"
author = "Dask Developers"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx_click",
    "sphinx.ext.autosummary",
    "dask_config_sphinx_ext",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


version = __version__
# The full version, including alpha/beta/rc tags.
release = __version__

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = "dask_sphinx_theme"
html_theme_path = [dask_sphinx_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "dask": ("https://docs.dask.org/en/latest/", None),
    "distributed": ("https://distributed.dask.org/en/latest/", None),
}
