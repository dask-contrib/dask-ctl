from collections import deque

from rich.text import Text

from textual.app import App
from textual.widget import Widget
from textual.reactive import reactive


LOGO = """
       :::
   :::::: ===
 ::: ====== ###
 :: === #######
 :  == ########
    =  ######
       ###
""".strip(
    "\n"
)


class Logo(Widget):
    color_key = reactive(
        {
            ":": "#FFC11E",
            "=": "#FC6E6B",
            "#": "#EF1161",
        }
    )

    def render(self) -> Text:
        text = Text()
        for char in LOGO:
            text.append(char, style=self.color_key.get(char, None))
        return text

    def rotate_colors(self) -> None:
        values_deque = deque(self.color_key.values())
        values_deque.rotate(-1)
        self.color_key = dict(zip(self.color_key.keys(), values_deque))

    def on_click(self) -> None:
        self.rotate_colors()


# Demo widget
class Demo(App):
    def compose(self):
        yield Logo()


if __name__ == "__main__":
    Demo.run(title="Logo")
