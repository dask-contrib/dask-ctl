import datetime

import click

from dask.utils import format_bytes, format_time_ago
from distributed.cli.utils import check_python_3

from . import __version__
from .utils import loop, format_table
from .discovery import (
    discover_clusters,
    discover_cluster_names,
    list_discovery_methods,
)
from .lifecycle import (
    scale_cluster,
    delete_cluster,
)


def autocomplete_cluster_names(ctx, args, incomplete):
    async def _autocomplete_cluster_names():
        return [
            cluster
            async for cluster, _ in discover_cluster_names()
            if incomplete in cluster
        ]

    return loop.run_sync(_autocomplete_cluster_names)


@click.group()
def cli():
    """daskctl controls Dask clusters."""
    pass


@cli.group()
def cluster():
    """Cluster commands."""
    pass


@cluster.command()
@click.argument("discovery", type=str, required=False)
def list(discovery=None):
    """List Dask clusters.

    DISCOVERY can be optionally set to restrict which discovery method to use.
    Run `daskctl list-discovery` for all available options.
    """

    async def _list():
        headers = [
            "Name",
            "Address",
            "Type",
            "Workers",
            "Threads",
            "Memory",
            "Created",
            "Status",
        ]
        output = []
        async for cluster in discover_clusters(discovery=discovery):

            threads = sum(
                w["nthreads"] for w in cluster.scheduler_info["workers"].values()
            )
            memory = format_bytes(
                sum(
                    [
                        w["memory_limit"]
                        for w in cluster.scheduler_info["workers"].values()
                    ]
                )
            )
            try:
                created = format_time_ago(
                    datetime.datetime.fromtimestamp(
                        float(cluster.scheduler_info["started"])
                    )
                )
            except KeyError:
                created = "Unknown"
            output.append(
                [
                    cluster.name,
                    cluster.scheduler_address,
                    type(cluster).__name__,
                    len(cluster.scheduler_info["workers"]),
                    threads,
                    memory,
                    created,
                    cluster.status.name.title(),
                ]
            )
        format_output(headers, output)

    loop.run_sync(_list)


@cluster.command()
@click.argument("name", autocompletion=autocomplete_cluster_names)
@click.argument("n-workers", type=int)
def scale(name, n_workers):
    """Scale a Dask cluster.

    NAME is the name of the cluster to scale.
    Run `daskctl list` for all available options.

    N_WORKERS is the number of workers to scale to.

    """
    try:
        scale_cluster(name, n_workers)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(f"Scaled cluster {name} to {n_workers} workers.")


@cluster.command()
@click.argument("name", autocompletion=autocomplete_cluster_names)
def delete(
    name,
):
    """Delete a Dask cluster.

    NAME is the name of the cluster to delete.
    Run `daskctl list` for all available options.

    """
    try:
        delete_cluster(name)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(f"Deleted cluster {name}.")


@cli.group()
def discovery():
    """Discovery commands."""
    pass


@discovery.command(name="list")
def list_discovery():
    """List installed discovery methods.

    Dask clusters can be created by many different packages. Each package has the option
    to register a method to discover clusters it creates. This command lists all discovery
    methods registered on your system.

    """

    async def _list_discovery():
        dm = list_discovery_methods()
        format_output(
            ["name", "package", "version", "path"],
            [[m, dm[m]["package"], dm[m]["version"], dm[m]["path"]] for m in dm],
        )

    loop.run_sync(_list_discovery)


@cli.command()
def version():
    """Show the daskctl version."""
    click.echo(__version__)


def format_output(headers, output):
    click.echo(format_table(output, headers=[h.upper() for h in headers]))


def daskctl():
    check_python_3()
    cli()


if __name__ == "__main__":
    daskctl()
