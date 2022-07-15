from math import floor
from functools import lru_cache
from typing import Iterable, TYPE_CHECKING

from rich.color import ANSI_COLOR_NAMES
from rich.segment import Segment
from rich.measure import Measurement
from rich.style import Style

if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console, ConsoleOptions

BAR_COLORS = [
    color
    for color in ANSI_COLOR_NAMES
    if "black" not in color and "white" not in color and "grey" not in color
]


@lru_cache(maxsize=None)
def number_shorthand(number):
    if number < 1e3:
        return number
    for cutoff, short in [
        (1e3, "k"),
        (1e6, "m"),
        (1e9, "b"),
        (1e12, "t"),
    ]:
        if number > cutoff:
            return f"{int(number // cutoff)}{short}"


class HBar:
    def __init__(
        self,
        data,
        tick="▇",
        colors=BAR_COLORS,
        label_color="cyan",
        value_color="white",
        show_labels=True,
        show_values=True,
        expand=False,
        x_width=None,
        formatter=number_shorthand,
    ):
        self.data = data
        self.tick = tick
        self.expand = expand
        self.colors = colors
        self.label_color = label_color
        self.value_color = value_color
        self.show_labels = show_labels
        self.show_values = show_values
        self.x_width = x_width
        self.formatter = formatter

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Iterable[Segment]:
        yield from self.render(
            console=console,
            max_width=options.max_width if self.expand else min(options.max_width, 70),
        )

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        min_width = 0  # TODO Calculate actual min width
        max_width = options.max_width
        return Measurement(min_width, max_width)

    def render(self, console: "Console", max_width: int) -> Iterable["Segment"]:
        if self.show_labels:
            labels_length = max([len(key) for key in self.data]) + 1
        else:
            labels_length = 0

        if self.show_values:
            values_length = (
                max([len(str(self.formatter(value))) for value in self.data.values()])
                + 1
            )
        else:
            values_length = 0

        max_width -= labels_length + values_length

        for i, (label, value) in enumerate(self.data.items()):
            label_text = str(label).ljust(labels_length)
            value_text = f" {self.formatter(value)}"
            try:
                bar_width = floor(
                    ((max_width / self.x_width or max(self.data.values())) * value)
                )
            except ZeroDivisionError:
                bar_width = 0

            if isinstance(self.tick, list):
                bar = self.tick[i % len(self.tick)] * bar_width
            else:
                bar = self.tick * bar_width

            if self.show_labels:
                yield Segment(label_text, Style.parse(self.label_color))
            yield Segment(bar, Style.parse(self.colors[i % len(self.colors)]))
            if self.show_values:
                yield Segment(f"{value_text}", Style.parse(self.value_color))
            yield Segment("\n")


class HBarStack(HBar):
    def __init__(self, *args, show_legend=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.labels, *_ = list(self.data.values())
        self.show_legend = show_legend

    def render(self, console: "Console", max_width: int) -> Iterable["Segment"]:
        if self.show_labels:
            labels_length = max([len(key) for key in self.labels]) + 1
        else:
            labels_length = 0
        values = []
        for i, _ in enumerate(self.labels):
            values.append([sl[i] for sl in list(self.data.values())[1:]])
        if self.show_values:
            values_length = max([len(str(sum(value))) for value in values])
        else:
            values_length = 0
        bar_width = max_width - (labels_length + values_length)
        x_width = self.x_width or max([sum(value) for value in values])
        value_multiplier = bar_width / x_width

        if self.show_legend:
            for segment in self.render_legend(console=console, max_width=max_width):
                yield segment

        for i, label in enumerate(self.labels):
            total = sum(values[i])

            label_text = str(label).ljust(labels_length)
            value_text = str(self.formatter(total))

            if self.show_labels:
                yield Segment(label_text, Style.parse(self.label_color))
            for j, value in enumerate(values[i]):
                yield Segment(
                    self.tick * floor((value * value_multiplier)),
                    Style.parse(self.colors[j % len(self.colors)]),
                )
            if self.show_values:
                yield Segment(f" {value_text}", Style.parse(self.value_color))
            yield Segment("\n")

    def render_legend(self, console: "Console", max_width: int) -> Iterable["Segment"]:
        groups = list(self.data)[1:]

        offset = max_width - sum([len(group) + 3 for group in groups])
        yield Segment(" " * offset)

        for i, group in enumerate(groups):
            yield Segment(f" {self.tick} ", Style.parse(self.colors[i]))
            yield Segment(group)

        yield Segment("\n")


if __name__ == "__main__":  # pragma: no cover
    from rich.console import Console  # noqa

    console = Console()

    console.print()
    console.print("Default graph")
    graph = HBar({"foo": 2000, "bar": 6000, "baz": 700, "fizz": 3000, "buzz": 4600})
    console.print(graph)
    console.print()

    console.print("Expand to fit")
    graph = HBar({"hello": 5, "world": 9}, expand=True)
    console.print(graph)
    console.print()

    console.print("Custom tick")
    graph = HBar(
        {"hello": 5, "world": 9},
        tick=["\u2591", "▒"],
    )
    console.print(graph)
    console.print()

    console.print("Custom colors")
    graph = HBar(
        {"foo": 2000, "bar": 6000, "baz": 700, "fizz": 3000, "buzz": 4600},
        colors=["medium_orchid3", "sky_blue1"],
        label_color="light_steel_blue1",
        value_color="light_steel_blue1",
    )
    console.print(graph)
    console.print()

    console.print("Stack")
    graph = HBarStack(
        {
            "fruits": [
                "Apples",
                "Pears",
                "Nectarines",
                "Plums",
                "Grapes",
                "Strawberries",
            ],
            "2015": [2, 1, 4, 3, 2, 4],
            "2016": [5, 3, 4, 2, 4, 6],
            "2017": [3, 2, 4, 4, 5, 3],
            "2018": [4, 3, 5, 5, 6, 4],
        },
    )
    console.print(graph)
    console.print()

    console.print("Dask memory")
    graph = HBarStack(
        {
            "workers": [
                "0",
                "1",
                "2",
                "3",
            ],
            "memory": [157563760, 156347164, 162519752, 156064568],
            "new": [4228, 4116, 4256, 4200],
            "released": [2962444, 1488080, 119960, 648288],
        },
        show_legend=False,
        show_labels=False,
        show_values=False,
        colors=["blue1", "dodger_blue1", "grey54"],
    )
    console.print(graph)
    console.print()
