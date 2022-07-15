from rich.text import Text

from textual.widget import Widget


class KeyBindings(Widget):
    def render(self) -> Text:
        outs = [("Key bindings", "bold"), "\n"]
        for binding in self.app.bindings.shown_keys:
            key = binding.key if binding.key_display is None else binding.key_display
            outs.append((key, "bold orange3"))
            outs.append(f" {binding.description}\n")
        return Text.assemble(*outs)
