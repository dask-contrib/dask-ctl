from rich.text import Text

from textual import events
from textual.app import App
from textual.widget import Widget


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


class Demo(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(Logo(), edge="top")


if __name__ == "__main__":
    Demo.run(title="Logo", log="textual.log")
