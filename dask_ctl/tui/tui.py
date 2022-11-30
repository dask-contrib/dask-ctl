from inspect import signature

from textual.app import App, ComposeResult
from textual import events
from textual.binding import Binding
from textual._callback import invoke, count_parameters

from ..lifecycle import get_cluster

from .widgets import (
    Logo,
    Info,
    KeyBindings,
    CommandReference,
    ClusterTable,
    CommandPrompt,
)


class DaskCtlTUI(App):
    CSS_PATH = "tui.css"
    COMMANDS = [
        Binding("quit", "quit()", "Quit"),
        Binding("q", "quit()", "Quit", show=False),
        Binding("scale", "scale()", "Scale cluster"),
        Binding("close", "close()", "Close cluster"),
    ]

    command_prompt = CommandPrompt(id="prompt", classes="box")
    cluster_table = ClusterTable(id="clusters", classes="box")

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab" or event.key == "shift+tab":
            event.prevent_default()

    def compose(self) -> ComposeResult:
        yield Info(id="info", classes="box")
        yield KeyBindings(id="bindings", classes="box")
        yield CommandReference(id="commands", classes="box")
        yield Logo(id="logo", classes="box")
        yield self.cluster_table
        yield self.command_prompt

    def on_load(self):
        self.log("Loaded Dask Control TUI")

    def on_mount(self) -> None:
        # When the app starts, we force focus to the cluster table and then focus
        # won't be lost again.
        self.query_one(ClusterTable).focus()

    def on_focus(self) -> None:
        self.log("Focus changed")

    def on_cluster_table_graceful_quit(
        self, message: ClusterTable.GracefulQuit
    ) -> None:
        self.log("Quitting")
        return self.app.exit()

    async def on_cluster_table_refresh(self, message: ClusterTable.Refresh):
        await self.command_prompt.set_out("Refreshing...", timeout=0.5)
        self.cluster_table.refresh()

    def on_cluster_table_set_scale_prompt(
        self, message: ClusterTable.SetScalePrompt
    ) -> None:
        self.command_prompt.set_command(f"scale {message.cluster} ")

    def on_cluster_table_set_close_prompt(
        self, message: ClusterTable.SetClosePrompt
    ) -> None:
        self.command_prompt.set_command(f"close {message.cluster}")

    async def action_scale(self, cluster_name: str, replicas: int):
        """Scale cluster"""
        try:
            cluster = await get_cluster(cluster_name, asynchronous=True)
        except Exception:
            return f"No such cluster {cluster_name}"
        try:
            cluster.scale(int(replicas))
        except Exception as e:
            self.log(e)
            return str(e)
        return f"Cluster {cluster_name} scaled to {replicas}"

    async def action_close(self, cluster_name: str):
        try:
            cluster = await get_cluster(cluster_name, asynchronous=True)
        except Exception:
            return f"No such cluster {cluster_name}"
        try:
            cluster.close()
        except Exception as e:
            return str(e)
        return f"Cluster {cluster_name} closed"

    async def on_command_prompt_submitted(
        self, message: CommandPrompt.Submitted
    ) -> None:
        """Handle command prompt submit events.

        Inspired by the way key bindings work we handle commands by
        using a COMMANDS constant with bindings in. Space separated arguments
        after the subcommand are passed as arguments to the action.
        """
        self.set_focus(self.cluster_table)
        command, *params = message.value.strip().split(" ")
        try:
            [binding] = [c for c in self.COMMANDS if c.key == command]
            if "(" in binding.action and "()" not in binding.action:
                raise ValueError(
                    f"Bad command binding {binding.key}, actions take arguments from the command not the binding"
                )
            method_name = f"action_{binding.action}".replace("()", "")
            method = getattr(self, method_name, None)
            if method is not None:
                if count_parameters(method) != len(params):
                    await self.command_prompt.set_out(
                        f"Error: '{command}' requires {count_parameters(method)} arguments {signature(method)}"
                    )
                else:
                    await self.command_prompt.set_out(await invoke(method, *params))
        except ValueError:
            await self.command_prompt.set_out(f"Unknown command '{command}'")

    async def on_command_prompt_blurred(self, message: CommandPrompt.Blurred) -> None:
        self.cluster_table.focus()

    async def on_cluster_table_focus_prompt(self):
        self.command_prompt.focus()

    async def on_cluster_table_cluster_selected(
        self, message: ClusterTable.ClusterSelected
    ) -> None:
        # TODO Open cluster dashboard
        pass
