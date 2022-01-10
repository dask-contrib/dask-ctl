import rich.box
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget

from dask.utils import format_bytes

from dask_ctl import get_cluster
from dask_ctl.tui.graphs import HBarStack


class NBytes(Widget):

    nbytes = Reactive({})

    def on_mount(self, event):
        self.set_interval(0.3, self.get_nbytes)

    async def get_nbytes(self):
        self.nbytes = await self.app.cluster.scheduler_comm.get_worker_memory()

    def render(self) -> Table:
        layout = Layout()
        colors = [
            "blue1",
            "cornflower_blue",
            "dodger_blue1",
            "grey54",
            "orange3",
        ]
        if self.nbytes:
            data = {
                "workers": [i for i in range(len(self.nbytes))],
                "unmanaged_old": [ws["unmanaged_old"] for ws in self.nbytes],
                "unmanaged_recent": [ws["unmanaged_recent"] for ws in self.nbytes],
                "process": [ws["process"] for ws in self.nbytes],
                "managed_in_memory": [ws["managed_in_memory"] for ws in self.nbytes],
                "managed_spilled": [ws["managed_spilled"] for ws in self.nbytes],
            }

            max_limit = max(
                *[ws["limit"] for ws in self.nbytes],
                *[ws["process"] + ws["managed_spilled"] for ws in self.nbytes]
            )
            max_cluster_limit = max(
                sum([ws["limit"] for ws in self.nbytes]),
                sum([ws["process"] + ws["managed_spilled"] for ws in self.nbytes]),
            )

            cluster_graph = HBarStack(
                {k: [sum(v)] for k, v in data.items()},
                show_legend=False,
                show_labels=False,
                colors=colors,
                expand=True,
                x_width=max_cluster_limit,
                formatter=format_bytes,
            )

            # TODO If all the workers can't be displayed show a histogram instead

            worker_graph = HBarStack(
                data,
                show_legend=False,
                show_labels=False,
                colors=colors,
                expand=True,
                x_width=max_limit,
                formatter=format_bytes,
            )
        else:
            cluster_graph = "Waiting for data"
            worker_graph = "Waiting for data"

        layout.split_column(
            Layout(
                Panel(
                    cluster_graph,
                    title="Bytes stored",
                    title_align="left",
                    style="blue",
                    box=rich.box.SQUARE,
                ),
                name="upper",
            ),
            Layout(
                Panel(
                    worker_graph,
                    title="Bytes stored per worker",
                    title_align="left",
                    style="blue",
                    box=rich.box.SQUARE,
                ),
                name="lower",
            ),
        )
        layout["upper"].size = 3
        return layout


class Demo(App):
    cluster = get_cluster("proxycluster-8786")

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(NBytes(), edge="top")


if __name__ == "__main__":
    Demo.run(title="NBytes", log="textual.log")
