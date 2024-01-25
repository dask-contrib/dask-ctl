from time import sleep
import sys
import warnings

import click
from rich import box
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, BarColumn

from . import __version__
from .utils import loop
from .discovery import (
    discover_cluster_names,
    list_discovery_methods,
)
from .lifecycle import create_cluster, get_cluster, delete_cluster, get_snippet
from .renderables import generate_table

from . import config  # noqa

console = Console()

# Only show warnings from dask_ctl
warnings.filterwarnings("ignore", module="^((?!dask_ctl).)*$")
# Customize warning output on the CLI
warnings.showwarning = lambda msg, *_: console.print(f":warning: {msg}", style="yellow")


def autocomplete_cluster_names(ctx, args, incomplete):
    async def _autocomplete_cluster_names():
        return [
            cluster
            async for cluster, _ in discover_cluster_names()
            if incomplete in cluster
        ]

    return loop.run_sync(_autocomplete_cluster_names)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
def cli():
    """[deprecated] use `dask cluster` instead of `daskctl`."""

    click.echo(
        "The command `daskctl` has been deprecated, please use `dask cluster` instead."
    )
    sys.exit(1)


@click.group()
def cluster():
    """Manage dask clusters.

    Create, List, Scale and Delete your dask clusters with dask-ctl.

    See https://dask-ctl.readthedocs.io/en/latest/cli.html for more info.
    """
    pass


@cluster.command()
@click.option("-f", "--spec-file-path")
def create(spec_file_path):
    """Create a Dask cluster from a spec file."""

    try:
        cluster = create_cluster(spec_file_path)
    except Exception:
        click.echo("Failed to create cluster.")
        raise click.Abort()
    else:
        click.echo(f"Created cluster {cluster.name}.")


@cluster.command()
@click.argument("discovery", type=str, required=False)
def list(discovery=None):
    """List Dask clusters.

    DISCOVERY can be optionally set to restrict which discovery method to use.
    Run `dask cluster discovery list` for all available options.
    """

    async def _list():
        with console.status("[bold green]Discovering clusters...") as status:
            table = await generate_table(
                discovery=discovery, status=status, console=console
            )

        console.print(table)

    loop.run_sync(_list)


@cluster.command()
@click.argument("name", shell_complete=autocomplete_cluster_names)
@click.argument("n-workers", type=int)
def scale(name, n_workers):
    """Scale a Dask cluster.

    NAME is the name of the cluster to scale.
    Run `dask cluster list` for all available options.

    N_WORKERS is the number of workers to scale to.

    """

    try:
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.fields[workers]}/{task.fields[n_workers]}",
            transient=True,
        ) as progress:
            scale_task = progress.add_task(
                "[blue]Preparing to scale...", start=False, workers="..", n_workers=".."
            )
            cluster = get_cluster(name)
            start_workers = len(cluster.scheduler_info["workers"])
            diff_workers = n_workers - start_workers

            if diff_workers != 0:
                progress.update(
                    scale_task,
                    workers=start_workers,
                    n_workers=n_workers,
                    total=abs(diff_workers),
                )
                if diff_workers > 0:
                    progress.update(scale_task, description="[green]Adding workers...")
                elif diff_workers < 0:
                    progress.update(scale_task, description="[red]Removing workers...")
                progress.start_task(scale_task)

                cluster.scale(n_workers)

                while len(cluster.scheduler_info["workers"]) != n_workers:
                    sleep(0.1)
                    progress.update(
                        scale_task,
                        completed=abs(
                            len(cluster.scheduler_info["workers"]) - start_workers
                        ),
                        workers=len(cluster.scheduler_info["workers"]),
                    )

                progress.update(scale_task, completed=diff_workers)
                progress.console.print(
                    f"Scaled cluster [blue]{name}[/blue] to {n_workers} workers."
                )
            else:
                progress.console.print(
                    f"Cluster [blue]{name}[/blue] already at {n_workers}, nothing to do."
                )

    except Exception as e:
        console.print(e)
        raise click.Abort()


@cluster.command()
@click.argument("name", shell_complete=autocomplete_cluster_names)
def delete(
    name,
):
    """Delete a Dask cluster.

    NAME is the name of the cluster to delete.
    Run `dask cluster list` for all available options.

    """
    try:
        delete_cluster(name)
    except Exception as e:
        click.echo(e)
        raise click.Abort()
    else:
        click.echo(f"Deleted cluster {name}.")


@cluster.command()
@click.argument("name", shell_complete=autocomplete_cluster_names)
def snippet(
    name,
):
    """Get code snippet for connecting to a cluster.

    NAME is the name of the cluster to get a snippet for.
    Run `dask cluster list` for all available options.

    """
    try:
        snip = get_snippet(name)
        snip = Syntax(
            snip,
            "python",
            theme="ansi_dark",  # Uses existing terminal theme
            background_color="default",  # Don't change background color
        )
    except Exception as e:
        click.echo(e)
    else:
        console.print(snip)


@cluster.group()
def discovery():
    """Cluster discovery subcommands."""
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


@discovery.command(name="enable")
@click.argument("name")
def enable_discovery(name):
    """Enable a discovery method."""
    console.print(
        "To enable discovery methods please update your configuration.\n"
        "See <TODO add docs link>"
    )


@discovery.command(name="disable")
@click.argument("name")
def disable_discovery(name):
    """Disable a discovery method."""
    console.print(
        "To disable discovery methods please update your configuration.\n"
        "See <TODO add docs link>"
    )


@cluster.command()
def version():
    """Show the dask-ctl version."""
    click.echo(f"dask-ctl: {__version__}")


def daskctl():
    cli()


if __name__ == "__main__":
    daskctl()
