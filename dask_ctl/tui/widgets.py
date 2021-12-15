import sys

from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from .. import __version__
import dask
import distributed


class Logo(Widget):

    mouse_over = Reactive(False)

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

    mouse_over = Reactive(False)

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
        for version in self.versions:
            outs.append((f"{version}: ", "bold orange3"))
            outs.append(f"{self.versions[version]}\n")
        return Text.assemble(*outs)


class Help(Widget):

    mouse_over = Reactive(False)

    def render(self) -> Text:
        commands = {
            ":": "new command",
            "q": "quit",
            "esc": "drop focus",
        }
        outs = [("Commands", "bold"), "\n"]
        for command in commands:
            outs.append((command, "bold on blue"))
            outs.append(f" {commands[command]}\n")
        return Text.assemble(*outs)


class CommandPrompt(Widget):

    mouse_over = Reactive(False)

    def render(self) -> Prompt:
        return Prompt()


class ClusterTable(Widget):

    selected = Reactive(0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None
        self.clusters = [
            [
                "FooCluster",
                "tcp://localhost:8786",
                "LocalCluster",
                "FooBar",
                "100",
                "100",
                "2TB",
                "Just Now",
                "Running",
            ],
            [
                "BarCluster",
                "tcp://localhost:6786",
                "LocalCluster",
                "FooBar",
                "108",
                "108",
                "2TB",
                "Just Now",
                "Running",
            ],
        ]

    async def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if self.selected > 0:
                self.selected -= 1
        if event.key == "down":
            if self.selected + 1 < len(self.clusters):
                self.selected += 1

    def render(self) -> Panel:
        self.table = Table(box=box.SIMPLE, expand=True, style="white")
        self.table.add_column("Name", style="cyan", no_wrap=True)
        self.table.add_column("Address")
        self.table.add_column("Type")
        self.table.add_column("Discovery")
        self.table.add_column("Workers")
        self.table.add_column("Threads")
        self.table.add_column("Memory")
        self.table.add_column("Created")
        self.table.add_column("Status")

        for cluster in self.clusters:
            self.table.add_row(*cluster)

        self.table.rows[self.selected].style = "black on blue"

        return Panel(self.table, style="blue", title="Clusters", title_align="left")
