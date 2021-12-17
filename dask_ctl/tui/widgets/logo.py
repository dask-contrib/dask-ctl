from rich.text import Text
from textual.widget import Widget


class Logo(Widget):
    def render(self) -> Text:
        return Text(
            """                ╔
               ╠H
           _r,╝ ╠
     ┌╔╗mª^,φ╙╔ ╚⌐
     ╞L ,φR" é^ ╠
     ╣  '▌ ╔╩  ╔^
    ╣ _, ╬    #`
   "'"`  ▌ ┌#^
        A╨\"""",
            style="orange3",
        )
