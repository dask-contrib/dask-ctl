from textual.events import Event
from textual.message import MessageTarget

from distributed.deploy.cluster import Cluster


class ClusterSelected(Event, verbosity=3, bubble=True):
    __slots__ = ["cluster"]

    def __init__(self, sender: MessageTarget, cluster: Cluster) -> None:
        super().__init__(sender)
        self.cluster = cluster
