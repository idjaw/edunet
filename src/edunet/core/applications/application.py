from abc import abstractmethod, ABC

from models.base_types import Request, Response


class Application(ABC):
    """
    Base Application implementation for any type of application that simply handles
    request and responses

    class MyApplication(Application):
        def handle_request(self, request):
            # implementation using request object that might be of type HTTP, TCP, UDP
            return some_response
    """

    @abstractmethod
    def handle_request(self, request_data: Request) -> Response:
        """
        Handling the request intended coming from a ConnectionHandler implementation

        e.g.
        class HTTPApplication(Application):
            ...
            def handle_request(self, foo, bar):
                self.custom_logic(foo, bar)
        """
