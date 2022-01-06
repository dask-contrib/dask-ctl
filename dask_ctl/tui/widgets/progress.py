from rich.table import Table
from rich.progress import Progress

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from rich.panel import Panel
from distributed.core import rpc


class Progress(Widget):
    progress = Reactive(Progress(auto_refresh=False, expand=True))
    _tick = Reactive(False)

    async def on_mount(self, event):
        # won't start correctly without a single task?
        self.task1 = self.progress.add_task("Task...", total=100, visible=False)
        self.tasks = {}
        self.set_interval(0.3, self.get_progress)
        self.r = None

    async def get_progress(self):
        state = await self.get_task_groups()
        names = list(state.keys())

        # remove computed/deleted tasks
        keys = list(self.tasks.keys())
        for name in keys:
            if name not in names:
                t = self.tasks.pop(name)
                self.progress.remove_task(t)

        # add progress bars for new tasks
        for name in reversed(names):
            if name not in self.tasks.keys():
                a = state[name]["all"]
                self.log(a, name)
                self.tasks[name] = self.progress.add_task(name, total=a)
            t = self.tasks[name]
            totals = state[name]["released"] + state[name]["memory"]
            self.log(totals, name)
            self.progress.update(t, completed=totals)

        self._tick = not self._tick

    async def get_task_groups(self):
        if self.r is None:
            if hasattr(self.app, "cluster"):
                self.r = self.app.cluster.scheduler_comm
            # probably in testing mode with a localcluster on 8786
            else:
                self.r = rpc("localhost:8786")

        state = await self.r.get_task_prefix_states()

        for group in state:
            state[group]["all"] = sum(state[group].values())
        return state

    def render(self) -> Table:
        self.progress.refresh()
        return Panel(self.progress)


class Demo(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(Progress(), edge="top")


if __name__ == "__main__":
    Demo.run(title="Progress", log="textual_debug.log")
