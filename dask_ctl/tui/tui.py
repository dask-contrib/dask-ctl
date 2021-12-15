import asyncio

from textual.app import App, DockLayout
from textual.widgets import Header

from .widgets import Logo, Info, ClusterTable, Help
from .prompt import CommandPrompt


class DaskCtlTUI(App):
    async def on_load(self, event):
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "blur_all")
        await self.bind(":", "focus_prompt")

    async def action_blur_all(self):
        await self.set_focus(None)

    async def action_focus_prompt(self):
        await self.set_focus(self.command_prompt)

    async def unload_view(self) -> None:
        if isinstance(self.view.layout, DockLayout):
            self.view.layout.docks.clear()
        self.view.widgets.clear()

    async def load_view_splash(self) -> None:
        await self.view.dock(Logo(), edge="top")

        async def load_main_view():
            await asyncio.sleep(2)
            await self.unload_view()
            await self.load_view_main()

        await self.call_later(load_main_view)

    async def load_view_main(self) -> None:
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

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""
        await self.load_view_splash()
