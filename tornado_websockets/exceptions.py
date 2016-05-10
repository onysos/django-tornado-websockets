class TornadoWebSocketsError(Exception):
    pass


class WebSocketNamespaceAlreadyRegistered(TornadoWebSocketsError, NameError):
    pass


class WebSocketEventAlreadyBinded(TornadoWebSocketsError, NameError):
    pass


class InvalidInstanceError(TornadoWebSocketsError, ValueError):
    pass


class EmitHandlerError(TornadoWebSocketsError):
    pass


class NotCallableError(TornadoWebSocketsError):
    pass
