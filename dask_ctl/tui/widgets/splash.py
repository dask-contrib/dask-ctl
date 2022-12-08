from rich.text import Text
from textual.app import App
from textual.widget import Widget

from ... import __version__


class SplashInfo(Widget):
    CSS = """
        text-align: center;
        height: 2;
    """

    def render(self) -> Text:
        outs = []
        outs.append(("dask-ctl\n", "bold blue"))
        outs.append((__version__, "bold orange3"))
        return Text.assemble(*outs)


# Demo widget
class Demo(App):
    def compose(self):
        yield SplashInfo()


if __name__ == "__main__":
    Demo.run(title="SplashInfo")
