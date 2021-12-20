import random

from rich.table import Table
from rich.progress import Progress

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from rich.panel import Panel
from dask.distributed import client
from distributed.core import rpc
import asyncio

class Progress(Widget):
    progress = Reactive(Progress(auto_refresh=False, expand=True))
    _tick = Reactive(False)

    async def on_mount(self, event):
        # won't start correctly without a single task?
        self.task1 = self.progress.add_task("Task...", total=100, visible=False)
        self.tasks = {}
        self.set_interval(0.5, self.generate_data)
        self.set_interval(0.3, self.get_progress)
        self.r = None

    async def generate_data(self):
        self.progress.update(self.task1, completed=100)
        self._tick = not self._tick


    async def get_progress(self):
        state, totals = await self.get_task_groups()
        # for r, m, e, p, a, l in zip(
        names = sorted(state["all"], key=state["all"].get, reverse=True)

        # remove computed/deleted tasks
        keys = list(self.tasks.keys())
        for name in keys:
            if name not in names:
                t = self.tasks.pop(name)
                self.progress.remove_task(t)


        # add progress bars for new tasks
        for name in names:
            if name not in self.tasks.keys():
                a = state['all'][name]
                self.log(a, name)
                self.tasks[name] = self.progress.add_task(name, total=a)
            t = self.tasks[name]
            totals = state['released'][name] + state['memory'][name]
            self.log(totals, name)
            self.progress.update(t, completed=totals)

        task_names = [t.description for t in self.progress.tasks]
        self._tick = not self._tick

    async def get_task_groups(self):
        if hasattr(self.app, 'cluster'):
            self.r = self.app.cluster.scheduler_comm if self.r is None else self.r
            foo = await self.r.task_prefix()
        # probably in testing mode with a localcluster on 8786
        else:
            self.r = rpc("localhost:8786") if self.r is None else self.r
        state = await self.r.task_prefix()

        state["all"] = {
                k: sum(v[k] for v in state.values()) for k in state["memory"]
            }

        totals = {
            k: sum(state[k].values())
            for k in ["all", "memory", "erred", "released", "waiting"]
        }

        totals["processing"] = totals["all"] - sum(
            v for k, v in totals.items() if k != "all"
        )

        #     self.root.title.text = (
        #         "Progress -- total: %(all)s, "
        #         "in-memory: %(memory)s, processing: %(processing)s, "
        #         "waiting: %(waiting)s, "
        #         "erred: %(erred)s" % totals
        #     )
        # task_groups
        return (state, totals)


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
