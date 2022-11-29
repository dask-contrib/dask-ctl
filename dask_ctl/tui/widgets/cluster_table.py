import copy

import rich.box
from rich.panel import Panel
from rich.table import Table

from textual import events
from textual.reactive import reactive
from textual.widget import Widget
from textual.message import Message, MessageTarget


from ...renderables import generate_table


class ClusterTable(Widget, can_focus=True):

    selected = reactive(0)
    table = reactive(Table())
    update_interval = None

    class ClusterSelected(Message):
        """Cluster selected message."""

        def __init__(self, sender: MessageTarget, cluster: str) -> None:
            self.cluster = cluster
            super().__init__(sender)

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
        self.update_interval = self.set_interval(5, self.reload_table)

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
                await self.emit(self.ClusterSelected(self, self.selected_cluster))

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
