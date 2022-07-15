from rich.text import Text
from textual.widget import Widget


class CommandReference(Widget):
    def render(self) -> Text:
        outs = [("Command reference", "bold"), "\n"]

        for attr in dir(self.app):
            if attr.startswith("command_") and callable(getattr(self.app, attr)):
                command = getattr(self.app, attr)
                if command.__doc__:
                    outs.append((attr.replace("command_", ""), "bold orange3"))
                    outs.append(f" {command.__doc__}\n")
        return Text.assemble(*outs)
