import os
import sys

from rich.text import Text
from textual.app import App
from textual.widget import Widget
import dask
import distributed


class Info(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from ... import __version__

        self.versions = {}
        self.versions["python"] = sys.version.split("|")[0].strip()
        if env := os.environ.get("CONDA_DEFAULT_ENV"):
            self.versions["conda environment"] = env
        self.versions["dask"] = dask.__version__
        self.versions["distributed"] = distributed.__version__
        self.versions["dask-ctl"] = __version__

    def render(self) -> Text:
        outs = []
        outs.append(("Dask Control\n", "bold blue"))
        for version in self.versions:
            outs.append((f"{version}: ", "bold orange3"))
            outs.append(f"{self.versions[version]}\n")
        return Text.assemble(*outs)


# Demo widget
class Demo(App):
    def compose(self):
        yield Info()


if __name__ == "__main__":
    Demo.run(title="Info")
