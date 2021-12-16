from textual.events import Event
from textual.message import MessageTarget


class ClusterSelected(Event, verbosity=3, bubble=True):
    __slots__ = ["cluster_name"]

    def __init__(self, sender: MessageTarget, cluster_name: str) -> None:
        super().__init__(sender)
        self.cluster_name = cluster_name
