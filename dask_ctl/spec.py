import yaml


def load_spec(path):
    with open(path, "r") as fh:
        spec = yaml.safe_load(fh.read())

    version = spec["version"]
    if version == 1:
        return load_v1_spec(spec)
    else:
        raise KeyError(f"No such dask cluster spec version {version}")


def load_v1_spec(spec):
    cm_module = spec["module"]
    cm_class = spec["class"]
    args = spec.get("args", [])
    kwargs = spec.get("kwargs", {})
    return cm_module, cm_class, args, kwargs
