import os.path
import yaml

import dask.config

fn = os.path.join(os.path.dirname(__file__), "ctl.yaml")
dask.config.ensure_file(source=fn)

with open(fn) as f:
    defaults = yaml.safe_load(f)

dask.config.update_defaults(defaults)
