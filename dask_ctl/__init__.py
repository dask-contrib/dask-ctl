from ._version import get_versions
from .exceptions import DaskClusterConfigNotFound  # noqa
import os.path

from dask.widgets import TEMPLATE_PATHS

__version__ = get_versions()["version"]
del get_versions

TEMPLATE_PATHS.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "widgets", "templates")
)
