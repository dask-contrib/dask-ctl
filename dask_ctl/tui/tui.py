import copy

from textual import events
from textual.app import App, DockView, ViewType
from textual.binding import Bindings
from textual.geometry import Size
from textual._callback import invoke, count_parameters
from textual.widgets import Placeholder

from ..lifecycle import get_cluster
from .widgets import (
    Logo,
    Info,
    ClusterTable,
    KeyBindings,
    ClusterInfo,
    CommandReference,
    CommandPrompt,
)
from .events import ClusterSelected

DEFAULT_BINDINGS = Bindings()
DEFAULT_BINDINGS.bind("q", "quit", "Quit")
DEFAULT_BINDINGS.bind("r", "refresh", "Refresh")
DEFAULT_BINDINGS.bind("ctrl+c", "keyboard_interrupt", show=False, allow_forward=False)


class DaskCtlTUI(App):
    cluster = None
    commands = []
    command_prompt = None
    cluster_table = None
    _binding_stack = []

    async def on_load(self, event):
        self._binding_stack.append(self.bindings)
        self.command_prompt = CommandPrompt(name="prompt")
        self.cluster_table = ClusterTable()

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""
        await self.load_view_main()

    ################
    ## Workarounds for pushing and popping views and bindings.
    ## FIXME Will need to be removed/refactored with future textual releases.
    ## ref https://github.com/Textualize/textual/discussions/182
    ##

    async def push_view(self, view) -> None:
        """Push a new view onto the view stack and force a rerender."""
        view.start_messages()
        resize = events.Resize(self, Size(self.console.size))
        await view.on_resize(resize)
        await super().push_view(view)

    async def pop_view(self) -> ViewType:
        """Pop the top view from the stack and force a rerender."""
        if len(self._view_stack) > 1:
            view = self._view_stack.pop()
            await view.close_messages()
            await self.remove(view)
            self.refresh()
            return view

    async def push_bindings(self, bindings=None):
        self._binding_stack.append(self.bindings)
        if bindings is not None:
            self.bindings = bindings

    async def pop_bindings(self):
        bindings = self.bindings
        self.bindings = self._binding_stack.pop()
        return bindings

    ##
    ###########

    async def action_blur_all(self):
        self.command_prompt.clear()
        await self.set_focus(None)

    async def action_focus_prompt(self):
        self.command_prompt.clear()
        await self.set_focus(self.command_prompt)

    async def action_scale(self):
        self.command_prompt.set_value(f"scale {self.cluster_table.selected_cluster} ")
        await self.set_focus(self.command_prompt)

    async def action_close(self):
        self.command_prompt.set_value(f"close {self.cluster_table.selected_cluster}")
        await self.set_focus(self.command_prompt)

    async def action_refresh(self):
        self.command_prompt.set_out("Refreshing...")
        self.refresh()
        self.set_timer(0.5, self.command_prompt.clear)

    async def action_keyboard_interrupt(self):
        if self.focused == self.command_prompt:
            await self.action_blur_all()
        else:
            await self.action_quit()

    async def action_quit(self):
        self.command_prompt.set_out("Exiting...")
        self.refresh()  # Needed to show the output before shutting down
        await self.shutdown()

    async def action_back(self):
        await self.pop_view()
        await self.pop_bindings()

    async def load_view_main(self) -> None:
        # Set bindings
        bindings = copy.deepcopy(DEFAULT_BINDINGS)
        bindings.bind("escape", "blur_all", show=False)
        bindings.bind("s", "scale", "Scale cluster")
        bindings.bind("c", "close", "Close cluster")
        bindings.bind(":", "focus_prompt", "New command")
        self.bindings = bindings

        # Draw widgets
        grid = await self.view.dock_grid(edge="top", name="clustertable")

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

        grid.place(
            info=Info(name="info"),
            key_bindings=KeyBindings(name="help"),
            command_reference=CommandReference(),
            logo=Logo(name="logo"),
            cluster_table=self.cluster_table,
            command_prompt=self.command_prompt,
        )

    async def load_view_cluster(self, cluster) -> None:
        self.cluster = await get_cluster(cluster, asynchronous=True)

        # Set bindings
        bindings = copy.deepcopy(DEFAULT_BINDINGS)
        bindings.bind("escape", "back", "Back to cluster list")
        bindings
        await self.push_bindings(bindings)

        # Draw widgets
        await self.push_view(DockView())
        grid = await self.view.dock_grid(edge="top", name="cluster")

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
            memory=Placeholder(name="nbytes"),
            processing=Placeholder(name="processing"),
            task_steam=Placeholder(name="task stream"),
            progress=Placeholder(name="Progress Bars"),
        )

    async def on_key(self, event):
        """If prompt not focussed forward all key events to the cluster table."""
        if len(self._view_stack) == 1 and self.focused != self.command_prompt:
            await self.cluster_table.forward_event(event)

    async def handle_prompt_on_submit(self, message) -> None:
        """Handle command prompt submit events.

        Inspired by the way key bindings work we handle commands by
        attemping to call a method on the app class named ``command_<foo>``
        where ``foo`` is the subcommand submitted. Space separated arguments
        after the subcommand are passed as arguments to that method.

        The command ``hello world`` would result in a call of ``App.command_hello("world")``.

        Setting a docstring on the ``command_hello`` method would cause it to be listed by the
        :class:`dask_ctl.tui.widgets.CommandReference` widget.

        """
        self.log(f"Handling prompt command '{message.command}'")

        command, *params = message.command.strip().split(" ")
        method_name = f"command_{command}"

        if command:
            method = getattr(self, method_name, None)
            if method is not None:
                if count_parameters(method) != len(params):
                    self.command_prompt.set_out(
                        f"Error: '{command}' requires {count_parameters(method)} arguments"
                    )
                else:
                    self.command_prompt.set_out(await invoke(method, *params))
            else:
                self.command_prompt.set_out(f"Unknown command '{command}'")

    async def command_quit(self):
        """Quit daskctl"""
        await self.action_quit()

    async def command_q(self):
        await self.action_quit()

    command_wq = command_q

    async def command_scale(self, cluster_name, replicas):
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

    async def command_close(self, cluster_name):
        """Close cluster"""
        try:
            cluster = await get_cluster(cluster_name, asynchronous=True)
        except Exception:
            return f"No such cluster {cluster_name}"
        try:
            cluster.close()
        except Exception as e:
            return str(e)
        return f"Cluster {cluster_name} closed"

    async def on_cluster_selected(self, event: ClusterSelected):
        self.command_prompt.set_out(f"Connecting to {event.cluster_name}...")
        self.refresh()
        self.command_prompt.clear()
        await self.load_view_cluster(event.cluster_name)
