from textual import events
from textual.reactive import reactive
from textual.widget import Widget
from textual.message import Message, MessageTarget

import rich.box
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style


class CommandPrompt(Widget, can_focus=True):

    value = reactive("")
    out = reactive("")
    history = reactive([])
    history_cursor = reactive(0)
    prompt = ">"
    cursor = (
        "|",
        Style(
            color="white",
            blink=True,
            bold=True,
        ),
    )
    _cursor_position = reactive(0)
    style = None

    class Submitted(Message):
        """Color selected message."""

        def __init__(self, sender: MessageTarget, value: str) -> None:
            self.value = value
            super().__init__(sender)

    def on_mount(self) -> None:
        pass

    def on_focus(self) -> None:
        self.out = ""

    def on_blur(self) -> None:
        self.reset()

    def render(self) -> RenderableType:
        cursor, cursor_style = self.cursor
        # TODO Handle cursor style
        # TODO highlight instead of insert character for cursor
        if self.has_focus:
            value = f"{self.prompt} {self.value[:self._cursor_position]}{cursor}{self.value[self._cursor_position:]}"
        else:
            value = self.out if self.out else self.value if self.value else self.prompt

        return Panel(
            value,
            title="",
            title_align="left",
            height=3,
            style=self.style or "",
            border_style="orange3" if self.has_focus else "blue",
            box=rich.box.DOUBLE if self.has_focus else rich.box.SQUARE,
        )

    def reset(self) -> None:
        self.value = ""
        self._cursor_position = 0

    def set_command(self, command) -> None:
        self.focus()
        self.value = command
        self._cursor_position = len(command)

    def set_out(self, output) -> None:
        self.out = output

    async def on_key(self, event: events.Key) -> None:
        # TODO handle up and down for history
        if event.key == "left":
            if self._cursor_position == 0:
                self._cursor_position = 0
            else:
                self._cursor_position -= 1

        elif event.key == "right":
            if self._cursor_position != len(self.value):
                self._cursor_position = self._cursor_position + 1

        elif event.key == "home":
            self._cursor_position = 0

        elif event.key == "end":
            self._cursor_position = len(self.value)

        elif event.key == "enter":
            if self.value:
                self.history.append(str(self.value))
                await self.emit(self.Submitted(self, str(self.value)))
            self.reset()
            self.app.set_focus(None)

        elif event.key == "tab":
            pass

        elif event.key == "backspace":
            if self._cursor_position == 0:
                return
            elif len(self.value) == 1:
                self.value = ""
                self._cursor_position = 0
            elif len(self.value) == 2:
                if self._cursor_position == 1:
                    self.value = self.value[1]
                    self._cursor_position = 0
                else:
                    self.value = self.value[0]
                    self._cursor_position = 1
            else:
                if self._cursor_position == 1:
                    self.value = self.value[1:]
                    self._cursor_position = 0
                elif self._cursor_position == len(self.value):
                    self.value = self.value[:-1]
                    self._cursor_position -= 1
                else:
                    self.value = (
                        self.value[: self._cursor_position - 1]
                        + self.value[self._cursor_position :]
                    )
                    self._cursor_position -= 1

        elif event.key == "delete":
            if self._cursor_position == len(self.value):
                return
            elif len(self.value) == 1:
                self.value = ""
            elif len(self.value) == 2:
                if self._cursor_position == 1:
                    self.value = self.value[0]
                else:
                    self.value = self.value[1]
            else:
                if self._cursor_position == 0:
                    self.value = self.value[1:]
                else:
                    self.value = (
                        self.value[: self._cursor_position]
                        + self.value[self._cursor_position + 1 :]
                    )
        else:
            if event.char:
                self.value += event.char
                self._cursor_position += 1
