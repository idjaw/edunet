class EduRouterException(Exception):
    """
    Base EduRouterException will be used for general application exceptions and to be
    inherited from edunet.by all other exceptions
    """

    pass


class TCPListenerError(EduRouterException):
    pass


class HTTPValidationError(EduRouterException):
    pass


class HTTPDataModelError(EduRouterException):
    pass
