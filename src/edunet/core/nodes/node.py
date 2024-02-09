import logging
from abc import ABC, abstractmethod

from core.networking.listeners.listener import Listener

logger = logging.getLogger(__name__)


class Node(ABC):
    """
    Representation of a nodes that will allow to hold an optional service to handle
    requests, or if no service passed will act as a client nodes
    """

    def __init__(self, listener: Listener):
        self.listener = listener

    @abstractmethod
    def start(self, *args, **kwargs) -> None:
        """
        Used to implement how a Node starts
        """

    @abstractmethod
    def stop(self, *args, **kwargs) -> None:
        """
        Used to implement how a Node stops
        """
