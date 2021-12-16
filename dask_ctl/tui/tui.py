import asyncio
import copy

from textual.app import App, DockLayout, DockView
from textual.views import WindowView
from textual.widgets import Header, Placeholder
from textual.binding import BindingStack, Bindings
from textual.reactive import Reactive

from dask_ctl.proxy import ProxyCluster

from ..lifecycle import get_cluster
from .widgets import Logo, Info, ClusterTable, KeyBindings, ClusterInfo
from .prompt import CommandPrompt
from .events import ClusterSelected

DEFAULT_BINDINGS = Bindings()
DEFAULT_BINDINGS.bind("q", "quit", "Quit")
DEFAULT_BINDINGS.bind("r", "refresh", "Refresh")
DEFAULT_BINDINGS.bind("ctrl+c", "quit", show=False, allow_forward=False)


class DaskCtlTUI(App):
    cluster = None

    async def on_load(self, event):
        pass

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""
        await self.load_view_main()

    async def action_blur_all(self):
        await self.set_focus(None)

    async def action_focus_prompt(self):
        await self.set_focus(self.command_prompt)

    async def action_refresh(self):
        self.refresh()

    async def action_back(self):
        await self.load_view_main()

    async def unload_view(self) -> None:
        if isinstance(self.view.layout, DockLayout):
            self.view.layout.docks.clear()
        self.view.widgets.clear()

    async def load_view_main(self) -> None:
        await self.unload_view()

        # Set bindings
        bindings = copy.copy(DEFAULT_BINDINGS)
        bindings.bind("escape", "blur_all", show=False)
        bindings.bind(":", "focus_prompt", "New command")
        self.bindings = bindings

        # Draw widgets
        grid = await self.view.dock_grid(edge="top", name="header")

        grid.add_column(fraction=1, name="left", min_size=20)
        grid.add_column(fraction=1, name="centre", min_size=20)
        grid.add_column(size=20, name="right")

        grid.add_row(size=10, name="top")
        grid.add_row(fraction=1, name="middle")
        grid.add_row(size=3, name="bottom")

        grid.add_areas(
            area1="left,top",
            area2="centre,top",
            area3="right,top",
            area4="left-start|right-end,middle",
            area5="left-start|right-end,bottom",
        )

        self.command_prompt = CommandPrompt(name="prompt")

        grid.place(
            area1=Info(name="info"),
            area2=KeyBindings(name="help"),
            area3=Logo(name="logo"),
            area4=ClusterTable(),
            area5=self.command_prompt,
        )

    async def load_view_cluster(self, cluster) -> None:
        await self.unload_view()
        self.cluster = await get_cluster(cluster, asynchronous=True)

        # Set bindings
        bindings = copy.copy(DEFAULT_BINDINGS)
        bindings.bind("escape", "back", "Back to cluster list")
        self.bindings = bindings

        # Draw widgets
        grid = await self.view.dock_grid(edge="top", name="header")

        grid.add_column(fraction=1, name="left", min_size=20)
        grid.add_column(fraction=2, name="centre", min_size=20)
        grid.add_column(size=20, name="right")

        grid.add_row(size=10, name="top")
        grid.add_row(fraction=2, name="middle")
        grid.add_row(fraction=1, name="bottom")

        grid.add_areas(
            cluster_info="left,top",
            help="centre,top",
            logo="right,top",
            memory="left,middle",
            processing="left,bottom",
            task_steam="centre-start|right-end,middle",
            progress="centre-start|right-end,bottom",
        )

        grid.place(
            cluster_info=ClusterInfo(name="info"),
            help=KeyBindings(name="help"),
            logo=Logo(name="logo"),
            memory=Placeholder(name="memory"),
            processing=Placeholder(name="processing"),
            task_steam=Placeholder(name="task stream"),
            progress=Placeholder(name="progress"),
        )

    async def handle_prompt_on_submit(self, message) -> None:
        self.log(f"Handling prompt command '{message.command}'")
        if message.command.startswith("connect"):
            try:
                _, port = message.command.split(" ")
                self.clusters.append(
                    await ProxyCluster.from_port(port, asynchronous=True)
                )
                self.log(len(self.clusters))
            except:
                self.command_prompt.out = "Cannot connect"
        elif message.command in ["q", "wq", "quit", "shutdown", "exit"]:
            await self.shutdown()
        else:
            self.command_prompt.out = "Unknown command"

    async def on_cluster_selected(self, event: ClusterSelected):
        self.log(f"Cluster selected {event.cluster_name}")
        await self.load_view_cluster(event.cluster_name)
