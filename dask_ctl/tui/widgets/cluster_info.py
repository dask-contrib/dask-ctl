from rich.text import Text

from textual.reactive import Reactive
from textual.widget import Widget

from dask.utils import format_bytes, typename

from ...renderables import get_created, get_status, get_workers


class ClusterInfo(Widget):
    data: Reactive[dict] = Reactive({})

    async def on_mount(self, event):
        await self.update_data()
        self.set_interval(5, self.update_data)

    async def update_data(self):
        workers = get_workers(self.app.cluster)
        self.data = {
            "name": self.app.cluster.name,
            "address": self.app.cluster.scheduler_address,
            "type": typename(type(self.app.cluster)),
            "workers": str(len(workers)),
            "threads": str(sum(w["nthreads"] for w in workers)),
            "memory": format_bytes(sum([w["memory_limit"] for w in workers])),
            "created": get_created(self.app.cluster),
            "status": get_status(self.app.cluster),
        }

    def render(self) -> Text:
        outs = []
        for item in self.data:
            outs.append((f"{item}: ", "bold orange3"))
            outs.append(f"{self.data[item]}\n")
        return Text.assemble(*outs)
