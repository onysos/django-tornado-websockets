class TornadoWebSocketsError(Exception):
    pass


class WebSocketNamespaceAlreadyRegistered(TornadoWebSocketsError, Exception):
    pass


class WebSocketEventAlreadyBinded(TornadoWebSocketsError, Exception):
    pass


class InvalidInstanceError(TornadoWebSocketsError, ValueError):
    pass


class EmitHandlerError(TornadoWebSocketsError, Exception):
    pass
