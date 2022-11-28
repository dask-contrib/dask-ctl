from rich.text import Text
from textual.widget import Widget


class CommandReference(Widget):
    def render(self) -> Text:
        outs = [("Command reference", "bold"), "\n"]
        for binding in self.app.COMMANDS:
            try:
                key, _, description = binding
            except TypeError:
                if not binding.show:
                    continue
                key = binding.key_display or binding.key
                description = binding.description
            outs.append((key, "bold orange3"))
            outs.append(f" {description}\n")
        return Text.assemble(*outs)
