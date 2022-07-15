import rich.box
from rich.panel import Panel
from rich.table import Table

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget

from dask_ctl import get_cluster
from dask_ctl.tui.graphs import TaskStream as TaskStreamGraph


class TaskStream(Widget):

    taskstream = Reactive([])
    max = 0

    def on_mount(self, event):
        self.set_interval(0.3, self.get_taskstream)

    async def get_taskstream(self):
        self.taskstream = await self.app.cluster.scheduler_comm.get_task_stream(
            count=1000
        )

    def render(self) -> Table:
        if self.taskstream:
            graph = TaskStreamGraph(self.taskstream)
            self.log(graph.data[0])
        else:
            graph = "Loading data"
        return Panel(
            graph,
            title="Task stream",
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
        await self.view.dock(TaskStream(), edge="top")


if __name__ == "__main__":
    Demo.run(title="Task Stream", log="textual.log")
