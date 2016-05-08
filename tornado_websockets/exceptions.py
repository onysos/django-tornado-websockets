class WebSocketNamespaceAlreadyRegistered(Exception):
    pass


class WebSocketEventAlreadyBinded(Exception):
    pass


class InvalidWebSocketInstance(ValueError):
    pass


class EmitHandlerException(Exception):
    pass
