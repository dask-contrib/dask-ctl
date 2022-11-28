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
    BINDINGS = [
        Binding("q", "graceful_quit()", "Quit"),
        Binding("r", "refresh()", "Refresh list"),
        Binding("s", "set_scale_prompt()", "Scale cluster"),
        Binding("c", "set_close_prompt()", "Close cluster"),
        Binding("colon", "focus_prompt()", "New Command", key_display=":"),
        Binding("escape", "blur()", "Blur", show=False),
    ]
    COMMANDS = [
        Binding("quit", "quit()", "Quit"),
        Binding("q", "quit()", "Quit", show=False),
        Binding("scale", "scale()", "Scale cluster"),
        Binding("close", "close()", "Close cluster"),
    ]

    command_prompt = CommandPrompt(id="prompt", classes="box")
    cluster_table = ClusterTable(id="clusters", classes="box")

    def compose(self) -> ComposeResult:
        yield Info(id="info", classes="box")
        yield KeyBindings(id="bindings", classes="box")
        yield CommandReference(id="commands", classes="box")
        yield Logo(id="logo", classes="box")
        yield self.cluster_table
        yield self.command_prompt

    def on_load(self):
        self.log("Loaded Dask Control TUI")

    async def on_key(self, event: events.Key) -> None:
        # TODO actually use focus rather than fake it
        if self.command_prompt.has_focus:
            await self.command_prompt.on_key(event)
        else:
            await self.cluster_table.on_key(event)

    def action_graceful_quit(self) -> None:
        # TODO figure out how to disable bindings when prompt has focus
        if not self.command_prompt.has_focus:
            self.log("Quitting")
            return self.app.exit()

    async def action_refresh(self):
        # TODO figure out how to disable bindings when prompt has focus
        if not self.command_prompt.has_focus:
            self.command_prompt.set_out("Refreshing...")
            self.refresh()
            self.set_timer(0.5, self.command_prompt.reset)

    def action_set_scale_prompt(self) -> None:
        # TODO figure out how to disable bindings when prompt has focus
        if not self.command_prompt.has_focus:
            self.command_prompt.set_command(
                f"scale {self.cluster_table.selected_cluster} "
            )

    def action_set_close_prompt(self) -> None:
        # TODO figure out how to disable bindings when prompt has focus
        if not self.command_prompt.has_focus:
            self.command_prompt.set_command(
                f"close {self.cluster_table.selected_cluster}"
            )

    def action_focus_prompt(self):
        # TODO actually use focus rather than fake it
        if not self.command_prompt.has_focus:
            self.command_prompt.set_command("")

    def action_blur(self):
        self.command_prompt.reset()

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
                    self.command_prompt.set_out(
                        f"Error: '{command}' requires {count_parameters(method)} arguments {signature(method)}"
                    )
                else:
                    self.command_prompt.set_out(await invoke(method, *params))
        except ValueError:
            self.command_prompt.set_out(f"Unknown command '{command}'")

    async def on_cluster_table_cluster_selected(
        self, message: ClusterTable.ClusterSelected
    ) -> None:
        # TODO Open cluster dashboard
        pass
