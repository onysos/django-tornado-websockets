class TornadoWebSocketsError(Exception):
    """
        Base exception of all django-tornado-websockets exceptions.
    """
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
        return 'The event "%s" is already binded for "%s" namespace.' % (self.event, self.namespace)


class InvalidInstanceError(TornadoWebSocketsError, ValueError):
    """
        Exception thrown when an instance is not the expected one.

        * ``actual_instance`` - actual instance which is trying to appear as ``expected_instance_name``.
        * ``expected_instance_name`` - name of expected instance.
    """

    def __init__(self, actual_instance, expected_instance_name):
        self.actual_instance = actual_instance
        self.expected_instance_name = expected_instance_name
        super(InvalidInstanceError, self).__init__(actual_instance, expected_instance_name)

    def __str__(self):
        return 'Expected instance of "%s", got "%s" instead.' % (
            self.expected_instance_name, repr(self.actual_instance)
        )


class EmitHandlerError(TornadoWebSocketsError):
    """
        Exception thrown when an user try to emit an event without being in a function or class method decorated
        by :meth:`@WebSocket.on() <tornado_websockets.websocket.WebSocket.on>` decorator.

        * ``event`` - name of the event under investigation.
        * ``namespace`` - namespace where the offence have taken place.
    """

    def __init__(self, event, namespace):
        self.event = event
        self.namespace = namespace
        super(EmitHandlerError, self).__init__(event, namespace)

    def __str__(self):
        return 'Can not emit "%s" event in "%s" namespace, please use emit() in a function or class method' \
               ' decorated by @WebSocket.on.' % (self.event, self.namespace)


class NotCallableError(TornadoWebSocketsError):
    """
        Exception thrown when an user try to use a decorator on a non-callable thing.

        * ``thing`` - « The Thing ».
    """

    def __init__(self, thing):
        self.thing = thing
        super(NotCallableError, self).__init__(thing)

    def __str__(self):
        return 'You used @WebSocket.on decorator on a thing that is not callable, got: "%s".' % self.thing
