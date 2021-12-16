import asyncio
import copy

from textual.app import App, DockLayout, DockView
from textual.views import WindowView
from textual.widgets import Header
from textual.binding import BindingStack, Bindings

from .widgets import Logo, Info, ClusterTable, Help
from .prompt import CommandPrompt
from .events import ClusterSelected

DEFAULT_BINDINGS = Bindings()
DEFAULT_BINDINGS.bind("q", "quit", "Quit")
DEFAULT_BINDINGS.bind("ctrl+c", "quit", show=False, allow_forward=False)


class DaskCtlTUI(App):
    clusters = []
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
        header = await self.view.dock_grid(edge="top", name="header")

        header.add_column(fraction=1, name="left", min_size=20)
        header.add_column(fraction=1, name="centre", min_size=20)
        header.add_column(size=20, name="right")

        header.add_row(size=10, name="top")
        header.add_row(fraction=1, name="middle")
        header.add_row(size=3, name="bottom")

        header.add_areas(
            area1="left,top",
            area2="centre,top",
            area3="right,top",
            area4="left-start|right-end,middle",
            area5="left-start|right-end,bottom",
        )

        self.command_prompt = CommandPrompt(name="prompt")

        header.place(
            area1=Info(name="info"),
            area2=Help(name="help"),
            area3=Logo(name="logo"),
            area4=ClusterTable(),
            area5=self.command_prompt,
        )

    async def load_view_cluster(self, cluster) -> None:
        await self.unload_view()
        self.cluster = cluster

        # Set bindings
        bindings = copy.copy(DEFAULT_BINDINGS)
        bindings.bind("escape", "back")
        self.bindings = bindings

        await self.view.dock(Logo(), edge="top")

    async def handle_prompt_on_submit(self, message) -> None:
        self.log(f"Handling prompt command '{message.command}'")
        if message.command == "connect":
            await self.load_view_cluster(None)
        else:
            self.command_prompt.out = "Unknown command"

    async def on_cluster_selected(self, event: ClusterSelected):
        self.log("Cluster selected")
        await self.load_view_cluster(event.cluster)
