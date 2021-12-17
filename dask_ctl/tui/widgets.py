import copy
import sys

import rich.box
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from dask.utils import format_bytes, typename

from .. import __version__
from ..renderables import generate_table, get_created, get_status, get_workers
from .events import ClusterSelected
import dask
import distributed


class Logo(Widget):
    def render(self) -> Text:
        return Text(
            """                ╔
               ╠H
           _r,╝ ╠
     ┌╔╗mª^,φ╙╔ ╚⌐
     ╞L ,φR" é^ ╠
     ╣  '▌ ╔╩  ╔^
    ╣ _, ╬    #`
   "'"`  ▌ ┌#^
        A╨\"""",
            style="orange3",
        )


class Info(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.versions = {
            "python": sys.version.split("|")[0].strip(),
            "dask": dask.__version__,
            "distributed": distributed.__version__,
            "dask-ctl": __version__,
        }

    def render(self) -> Text:
        outs = []
        outs.append(("Dask Control\n", "bold blue"))
        for version in self.versions:
            outs.append((f"{version}: ", "bold orange3"))
            outs.append(f"{self.versions[version]}\n")
        return Text.assemble(*outs)


class ClusterInfo(Widget):
    data: Reactive[dict] = Reactive({})

    async def on_mount(self, event):
        await self.update_data()
        self.set_interval(5, self.update_data)

    async def update_data(self):
        workers = get_workers(self.app.cluster)
        self.data = {
            "name": self.app.cluster.name,
            "address": self.app.cluster.scheduler_address,
            "type": typename(type(self.app.cluster)),
            "workers": str(len(workers)),
            "threads": str(sum(w["nthreads"] for w in workers)),
            "memory": format_bytes(sum([w["memory_limit"] for w in workers])),
            "created": get_created(self.app.cluster),
            "status": get_status(self.app.cluster),
        }

    def render(self) -> Text:
        outs = []
        for item in self.data:
            outs.append((f"{item}: ", "bold orange3"))
            outs.append(f"{self.data[item]}\n")
        return Text.assemble(*outs)


class KeyBindings(Widget):
    def render(self) -> Text:
        outs = [("Key bindings", "bold"), "\n"]
        for binding in self.app.bindings.shown_keys:
            key = binding.key if binding.key_display is None else binding.key_display
            outs.append((key, "bold orange3"))
            outs.append(f" {binding.description}\n")
        return Text.assemble(*outs)


class CommandReference(Widget):
    def render(self) -> Text:
        outs = [("Command reference", "bold"), "\n"]

        for attr in dir(self.app):
            if attr.startswith("command_") and callable(getattr(self.app, attr)):
                command = getattr(self.app, attr)
                if command.__doc__:
                    outs.append((attr.replace("command_", ""), "bold orange3"))
                    outs.append(f" {command.__doc__}\n")
        return Text.assemble(*outs)


class CommandPrompt(Widget):
    def render(self) -> Prompt:
        return Prompt()


class ClusterTable(Widget):

    selected = Reactive(0)
    table: Reactive[Table] = Reactive(Table())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def selected_cluster(self):
        return list(self.table.columns[0].cells)[self.selected]

    async def reload_table(self):
        self.table = await generate_table()
        self.table.expand = True
        self.table.style = "white"

    async def on_mount(self, event):
        await self.reload_table()
        self.set_interval(5, self.reload_table)

    async def on_unmount(self, event):
        self.app.log("Table unmounted")

    async def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if self.selected > 0:
                self.selected -= 1
        elif event.key == "down":
            if self.selected + 1 < len(self.table.rows):
                self.selected += 1
        elif event.key == "enter":
            if self.table.row_count and self.selected < self.table.row_count:
                await self.post_message(ClusterSelected(self, self.selected_cluster))
        self.app.refresh()

    def render(self) -> Panel:
        table = copy.deepcopy(self.table)
        if table.row_count:
            table.rows[self.selected].style = "on bright_black"

        return Panel(
            table,
            style="blue",
            title="Clusters",
            title_align="left",
            box=rich.box.SQUARE,
        )
