import random

from rich.table import Table
from rich.progress import Progress

from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget


class Progress(Widget):
    progress = Reactive(Progress(auto_refresh=False, expand=True))
    _tick = Reactive(False)

    def on_mount(self, event):
        self.task1 = self.progress.add_task("[red]Downloading...", total=100)
        self.set_interval(0.1, self.generate_data)

    def generate_data(self):
        self.progress.update(self.task1, completed=random.randrange(0, 100))
        self._tick = not self._tick
        self.log(self.progress.tasks[self.task1].percentage)

    def render(self) -> Table:
        self.progress.refresh()
        return self.progress


class Demo(App):
    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(Progress(), edge="top")


if __name__ == "__main__":
    Demo.run(title="Progress", log="textual.log")
