import datetime

import click
from rich import box
from rich.table import Table
from rich.text import Text

from dask.utils import format_bytes, format_time_ago, typename
from distributed.core import Status

from .discovery import (
    discover_clusters,
    list_discovery_methods,
)


def get_created(cluster):
    try:
        return format_time_ago(
            datetime.datetime.fromtimestamp(float(cluster.scheduler_info["started"]))
        )
    except KeyError:
        return "Unknown"


def get_status(cluster):
    cluster_status = cluster.status.name.title()
    if cluster.status == Status.created:
        cluster_status = Text(cluster_status, style="yellow")
    elif cluster.status == Status.running:
        cluster_status = Text(cluster_status, style="green")
    else:
        cluster_status = Text(cluster_status, style="red")
    return cluster_status


def get_workers(cluster):
    try:
        return cluster.scheduler_info["workers"].values()
    except KeyError:
        return []


async def generate_table(discovery=None, status=None, console=None):
    table = Table(box=box.SIMPLE)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Address")
    table.add_column("Type")
    table.add_column("Discovery")
    table.add_column("Workers")
    table.add_column("Threads")
    table.add_column("Memory")
    table.add_column("Created")
    table.add_column("Status")

    discovery_methods = list_discovery_methods()
    for discovery_method in discovery_methods:
        if status:
            status.update(f"[bold green]Discovering {discovery_method}s...")
        if discovery_methods[discovery_method]["enabled"] and (
            discovery is None or discovery == discovery_method
        ):
            try:
                async for cluster in discover_clusters(discovery=discovery_method):
                    workers = get_workers(cluster)
                    table.add_row(
                        cluster.name,
                        cluster.scheduler_address,
                        typename(type(cluster)),
                        discovery_method,
                        str(len(workers)),
                        str(sum(w["nthreads"] for w in workers)),
                        format_bytes(sum([w["memory_limit"] for w in workers])),
                        get_created(cluster),
                        get_status(cluster),
                    )
            except Exception as e:
                if console:
                    if discovery is None:
                        console.print(
                            f":warning: Discovery {discovery_method} failed. "
                            f"Run `dask cluster list {discovery_method}` for more info.",
                            style="yellow",
                        )
                    else:
                        console.print_exception(show_locals=True)
                        raise click.Abort()
                else:
                    raise e
    return table
