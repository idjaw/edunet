from abc import abstractmethod, ABC


class Listener(ABC):
    """
    This base class provides the means to implement any listener type to handle incoming
    network requests.

    For example: TCP or UDP listening
    """

    @abstractmethod
    def accept_connection(self, *args, **kwargs):
        """
        Used to implement how connections are accepted
        """

    @abstractmethod
    def handle_request(self, *args, **kwargs):
        """
        Used to implement how connections should be handled
        """

    @abstractmethod
    def start(self, *args, **kwargs):
        """
        Used to implement the starting of the listener
        """

    @abstractmethod
    def stop(self, *args, **kwargs):
        """
        Used to implement the stopping of the listener
        """
