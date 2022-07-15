import rich.box
from rich.table import Table
from rich.progress import (
    Progress as RichProgress,
    BarColumn,
    TimeRemainingColumn,
)

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from rich.panel import Panel

from ... import get_cluster


class Progress(Widget):
    state = Reactive({})
    title = "Progress"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bar_column = BarColumn(bar_width=None)
        self.progress = RichProgress(
            "[white]{task.description}[/white]",
            bar_column,
            "[white]{task.completed}/{task.total}[/white]",
            TimeRemainingColumn(),
            auto_refresh=False,
            expand=True,
        )

    async def on_mount(self, event):
        # won't start correctly without a single task?
        self.task1 = self.progress.add_task("Task...", total=100, visible=False)
        self.tasks = {}
        self.set_interval(0.3, self.get_progress)

    async def get_progress(self):
        self.state = await self.get_task_groups()
        names = list(self.state.keys())

        # remove computed/deleted tasks
        keys = list(self.tasks.keys())
        for name in keys:
            if name not in names:
                t = self.tasks.pop(name)
                self.progress.remove_task(t)

        # add progress bars for new tasks
        for name in reversed(names):
            if name not in self.tasks.keys():
                a = self.state[name]["total"]
                self.tasks[name] = self.progress.add_task(name, total=a)
            t = self.tasks[name]
            total = self.state[name]["released"] + self.state[name]["memory"]
            self.progress.update(t, completed=total)

        totals = {}
        for task in self.state:
            for state in self.state[task]:
                if state in totals:
                    totals[state] += self.state[task][state]
                else:
                    totals[state] = self.state[task][state]

        # Update title
        if self.tasks:
            self.title = "Progress \u2500\u2500 " + ", ".join(
                [f"{key}: {value}" for key, value in totals.items()]
            )
        else:
            self.title = "Progress"

    async def get_task_groups(self):
        state = await self.app.cluster.scheduler_comm.get_task_prefix_states()

        for group in state:
            state[group] = {"total": sum(state[group].values()), **state[group]}
        return state

    def render(self) -> Table:
        self.progress.refresh()
        return Panel(
            self.progress,
            title=self.title,
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
        await self.view.dock(Progress(), edge="top")


if __name__ == "__main__":
    Demo.run(title="Progress", log="textual_debug.log")
