from rich.text import Text

from textual.reactive import watch, reactive
from textual.widget import Widget


class KeyBindings(Widget):

    bindings = reactive([])

    def on_mount(self) -> None:
        watch(self.screen, "focused", self._focus_changed)

    def _focus_changed(self, focused) -> None:
        self.bindings = [*self.app.BINDINGS]
        if focused:
            self.bindings += focused.BINDINGS
        self.refresh()

    def render(self) -> Text:
        outs = [("Key bindings", "bold"), "\n"]
        for binding in self.bindings:
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
