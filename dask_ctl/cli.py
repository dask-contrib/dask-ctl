import datetime

import click
from rich.console import Console
from rich.table import Table
from rich import box

from dask.utils import format_bytes, format_time_ago
from distributed.core import Status
from distributed.cli.utils import check_python_3
from distributed.utils import typename

from . import __version__
from .utils import loop
from .discovery import (
    discover_clusters,
    discover_cluster_names,
    list_discovery_methods,
)
from .lifecycle import (
    create_cluster,
    scale_cluster,
    delete_cluster,
)

console = Console()


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
@click.option("-f", "--spec-file-path")
def create(spec_file_path):
    """Create a Dask cluster from a spec file."""

    async def _create():
        try:
            cluster = await create_cluster(spec_file_path)
        except Exception:
            click.echo("Failed to create cluster.")
            raise click.Abort()
        else:
            click.echo(f"Created cluster {cluster.name}.")

    loop.run_sync(_create)


@cluster.command()
@click.argument("discovery", type=str, required=False)
def list(discovery=None):
    """List Dask clusters.

    DISCOVERY can be optionally set to restrict which discovery method to use.
    Run `daskctl list-discovery` for all available options.
    """

    async def _list():
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

        for discovery_method in list_discovery_methods():
            if discovery is None or discovery == discovery_method:
                try:
                    async for cluster in discover_clusters(discovery=discovery_method):
                        try:
                            workers = cluster.scheduler_info["workers"].values()
                        except KeyError:
                            workers = []
                        try:
                            created = format_time_ago(
                                datetime.datetime.fromtimestamp(
                                    float(cluster.scheduler_info["started"])
                                )
                            )
                        except KeyError:
                            created = "Unknown"

                        status = cluster.status.name.title()
                        if cluster.status == Status.created:
                            status = f"[yellow]{status}[/yellow]"
                        elif cluster.status == Status.running:
                            status = f"[green]{status}[/green]"
                        else:
                            status = f"[red]{status}[/red]"

                        table.add_row(
                            cluster.name,
                            cluster.scheduler_address,
                            typename(type(cluster)),
                            discovery_method,
                            str(len(workers)),
                            str(sum(w["nthreads"] for w in workers)),
                            format_bytes(sum([w["memory_limit"] for w in workers])),
                            created,
                            status,
                        )
                except Exception:
                    if discovery is None:
                        console.print(
                            f":warning: Discovery {discovery_method} failed. "
                            f"Run `daskctl cluster list {discovery_method}` for more info.",
                            style="yellow",
                        )
                    else:
                        console.print_exception(show_locals=True)
                        raise click.Abort()

        console.print(table)

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
        table = Table(box=box.SIMPLE)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Package", justify="right", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Path", style="yellow")
        table.add_column("Enabled", justify="right", style="green")

        for method_name, method in list_discovery_methods().items():
            table.add_row(
                method_name,
                method["package"],
                method["version"],
                method["path"],
                ":heavy_check_mark:" if method["enabled"] else ":cross_mark:",
            )
        console.print(table)

    loop.run_sync(_list_discovery)


@cli.command()
def version():
    """Show the daskctl version."""
    click.echo(__version__)


def daskctl():
    check_python_3()
    cli()


if __name__ == "__main__":
    daskctl()
