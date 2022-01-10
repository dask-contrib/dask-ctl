from math import floor, ceil
from typing import Iterable, TYPE_CHECKING

import numpy as np

from rich.segment import Segment
from rich.measure import Measurement
from rich.style import Style

if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console, ConsoleOptions


COLOR_LOOKUP = {
    0: "white",
    1: "cornflower_blue",
    2: "red",
    3: "orange3",
    4: "orange3",
    5: "black",
}

TASK_PALLETE = [
    "#440154",
    "#482878",
    "#3e4989",
    "#31688e",
    "#26828e",
    "#1f9e89",
    "#35b779",
    "#6ece58",
    "#b5de2b",
    "#fde725",
]


def color_to_int(color: str) -> int:
    return int(color.replace("#", ""), 16)


def int_to_color(i: int) -> str:
    return "#" + format(i, "#06x").replace("0x", "").upper().rjust(6, "0")


class TaskStream:
    def __init__(self, data, tick="\u2588"):
        self.data = []
        self.task_prefixes = []
        self.tick = tick
        self.options = None
        for task in data:
            for startstop in task["startstops"]:
                startstop["key"] = task["key"]
                startstop["thread"] = task["thread"]
                startstop["prefix"] = startstop["key"].split("-")[0]
                if startstop["prefix"] not in self.task_prefixes:
                    self.task_prefixes.append(startstop["prefix"])
                startstop["worker"] = task["worker"]
                self.data.append(startstop)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Iterable[Segment]:
        yield from self.render(
            console=console,
            max_width=options.max_width,
            max_height=options.max_height,
        )

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        min_width = 0  # TODO Calculate actual min width
        max_width = options.max_width
        return Measurement(min_width, max_width)

    def render(
        self, console: "Console", max_width: int, max_height: int
    ) -> Iterable["Segment"]:
        start = min([t["start"] for t in self.data])
        stop = max([t["stop"] for t in self.data])
        workers = list(set([t["worker"] for t in self.data]))
        interval_width = (stop - start) / max_width

        worker_height = max_height // len(workers)
        display = np.zeros((max_height, max_width))

        for task in self.data:
            worker = workers.index(task["worker"])
            for i in range(worker_height):
                i_start = floor((task["start"] - start) / interval_width)
                if task["stop"] - task["start"] < interval_width:
                    i_stop = i_start + 1
                else:
                    i_stop = ceil((task["stop"] - start) / interval_width)
                row = worker * worker_height + i

                if task["action"] == "compute":
                    value = color_to_int(
                        TASK_PALLETE[self.task_prefixes.index(task["prefix"])]
                    )
                elif task["action"] == "transfer":
                    value = color_to_int("#FF0000")
                else:
                    value = color_to_int("#000000")

                display[row, i_start:i_stop] = value

        for i in range(worker_height * len(workers)):
            for j in range(max_width):
                value = int(display[i, j])
                if not value:
                    yield Segment(" ")
                else:
                    yield Segment(self.tick, Style.parse(int_to_color(value)))

            yield Segment("\n")


if __name__ == "__main__":  # pragma: no cover
    from rich.console import Console  # noqa

    console = Console()
    console.print(TaskStream([]))
