import asyncio
import copy

from textual.app import App, DockLayout, DockView
from textual.views import WindowView
from textual.widgets import Header, Placeholder
from textual.binding import BindingStack, Bindings
from textual.reactive import Reactive
from textual._callback import invoke, count_parameters

from dask_ctl.proxy import ProxyCluster

from ..lifecycle import get_cluster
from .widgets import (
    Logo,
    Info,
    ClusterTable,
    KeyBindings,
    ClusterInfo,
    CommandReference,
)
from .prompt import CommandPrompt
from .events import ClusterSelected

DEFAULT_BINDINGS = Bindings()
DEFAULT_BINDINGS.bind("q", "quit", "Quit")
DEFAULT_BINDINGS.bind("r", "refresh", "Refresh")
DEFAULT_BINDINGS.bind("ctrl+c", "quit", show=False, allow_forward=False)


class DaskCtlTUI(App):
    cluster = None
    commands = []

    async def on_load(self, event):
        pass

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""
        await self.load_view_main()

    async def action_blur_all(self):
        self.command_prompt.set_value("")
        await self.set_focus(None)

    async def action_focus_prompt(self):
        self.command_prompt.set_value("")
        await self.set_focus(self.command_prompt)

    async def action_scale(self):
        self.command_prompt.set_value(f"scale {self.cluster_table.selected_cluster} ")
        await self.set_focus(self.command_prompt)

    async def action_close(self):
        self.command_prompt.set_value(f"close {self.cluster_table.selected_cluster}")
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
        bindings = copy.deepcopy(DEFAULT_BINDINGS)
        bindings.bind("escape", "blur_all", show=False)
        bindings.bind("s", "scale", "Scale cluster")
        bindings.bind("c", "close", "Close cluster")
        bindings.bind(":", "focus_prompt", "New command")
        self.bindings = bindings

        # Draw widgets
        grid = await self.view.dock_grid(edge="top", name="header")

        grid.add_column(fraction=2, name="left", min_size=20)
        grid.add_column(fraction=1, name="lcentre", min_size=20)
        grid.add_column(fraction=1, name="rcentre", min_size=20)
        grid.add_column(size=20, name="right")

        grid.add_row(size=10, name="top")
        grid.add_row(fraction=1, name="middle")
        grid.add_row(size=3, name="bottom")

        grid.add_areas(
            info="left,top",
            key_bindings="lcentre,top",
            command_reference="rcentre,top",
            logo="right,top",
            cluster_table="left-start|right-end,middle",
            command_prompt="left-start|right-end,bottom",
        )

        self.command_prompt = CommandPrompt(name="prompt")
        self.cluster_table = ClusterTable()

        grid.place(
            info=Info(name="info"),
            key_bindings=KeyBindings(name="help"),
            command_reference=CommandReference(),
            logo=Logo(name="logo"),
            cluster_table=self.cluster_table,
            command_prompt=self.command_prompt,
        )

    async def load_view_cluster(self, cluster) -> None:
        await self.unload_view()
        self.cluster = await get_cluster(cluster, asynchronous=True)

        # Set bindings
        bindings = copy.deepcopy(DEFAULT_BINDINGS)
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

    async def on_key(self, event):
        """If prompt not focussed send all keys to the table."""
        if self.focused != self.command_prompt:
            await self.cluster_table.forward_event(event)

    async def handle_prompt_on_submit(self, message) -> None:
        self.log(f"Handling prompt command '{message.command}'")

        command, *params = message.command.strip().split(" ")
        method_name = f"command_{command}"

        if command:
            method = getattr(self, method_name, None)
            if method is not None:
                if count_parameters(method) != len(params):
                    self.command_prompt.out = f"Error: '{command}' accepts {count_parameters(method)} parameters"
                else:
                    self.command_prompt.out = await invoke(method, *params)
            else:
                self.command_prompt.out = f"Unknown command '{command}'"

    async def command_quit(self):
        """Quit"""
        await self.shutdown()

    async def command_q(self):
        await self.shutdown()

    command_wq = command_q

    async def command_scale(self, cluster_name, replicas):
        """Scale cluster"""
        try:
            cluster = await get_cluster(cluster_name, asynchronous=True)
        except:
            return f"No such cluster {cluster_name}"
        try:
            await cluster.scale(replicas)
        except Exception as e:
            return str(e)
        return f"Cluster {cluster_name} scaled to {replicas}"

    async def command_close(self, cluster_name):
        """Close cluster"""
        try:
            cluster = await get_cluster(cluster_name, asynchronous=True)
        except:
            return f"No such cluster {cluster_name}"
        try:
            await cluster.close()
        except Exception as e:
            return str(e)
        return f"Cluster {cluster_name} closed"

    async def on_cluster_selected(self, event: ClusterSelected):
        self.log(f"Cluster selected {event.cluster_name}")
        await self.load_view_cluster(event.cluster_name)
