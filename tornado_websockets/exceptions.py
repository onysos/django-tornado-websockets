class TornadoWebSocketsError(Exception):
    """
        Base exception of all django-tornado-websockets exceptions.
    """
    pass


class WebSocketNamespaceAlreadyRegistered(TornadoWebSocketsError, NameError):
    pass


class WebSocketEventAlreadyBinded(TornadoWebSocketsError, NameError):
    """
        Exception thrown when an user try to bind an already existing event for a given namespace.

        * ``event`` - name of the event under investigation.
        * ``namespace`` - namespace where the offence have taken place.
    """
    def __init__(self, event, namespace):
        self.event = event
        self.namespace = namespace
        super(WebSocketEventAlreadyBinded, self).__init__(event, namespace)

    def __str__(self):
        return 'The event "%s" is already binded for "%s" namespace' % (self.event, self.namespace)


class InvalidInstanceError(TornadoWebSocketsError, ValueError):
    pass


class EmitHandlerError(TornadoWebSocketsError):
    pass


class NotCallableError(TornadoWebSocketsError):
    """
        Exception thrown when an user try to use a decorator on a non-callable thing

        * ``thing`` - « The Thing »
    """
    def __init__(self, thing):
        self.thing = thing
        super(NotCallableError, self).__init__(thing)

    def __str__(self):
        return 'You used @WebSocket.on decorator on a thing that is not callable, got: "%s"' % self.thing
