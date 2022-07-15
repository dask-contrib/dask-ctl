import rich.box
from rich.panel import Panel
from rich.table import Table

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget

from dask_ctl import get_cluster
from dask_ctl.tui.graphs import HBar


class Processing(Widget):

    processing = Reactive([])
    max = 0

    def on_mount(self, event):
        self.set_interval(0.3, self.get_processing)

    async def get_processing(self):
        self.processing = await self.app.cluster.scheduler_comm.get_worker_processing()
        if self.processing is None or sum(self.processing) == 0:
            self.max = 0
        else:
            self.max = max(self.max, *self.processing)

    def render(self) -> Table:
        if not self.processing:
            graph = "Loading data"
        else:
            graph = HBar(
                {str(i): v for i, v in enumerate(self.processing)},
                show_labels=False,
                colors=["blue1"],  # TODO match colours from the dashboard
                x_width=self.max,
            )
        return Panel(
            graph,
            title="Processing",
            title_align="left",
            style="blue",
            box=rich.box.SQUARE,
        )


class Demo(App):
    def __init__(self, *args, **kwargs):
        self.cluster = get_cluster("proxycluster-8786")
        super().__init__(*args, **kwargs)

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(Processing(), edge="top")


if __name__ == "__main__":
    Demo.run(title="Processing", log="textual.log")
