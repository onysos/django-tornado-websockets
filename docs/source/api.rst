API
===

WebSocket
---------

.. automodule:: tornado_websockets.websocket

    .. autoclass:: WebSocket
    .. automethod:: WebSocket.on
    .. automethod:: WebSocket.emit

WebSocketHandler
----------------

.. automodule:: tornado_websockets.websockethandler

    .. autoclass:: WebSocketHandler

TornadoWrapper
--------------

.. automodule:: tornado_websockets.tornadowrapper

    .. autoclass:: TornadoWrapper
    .. automethod:: TornadoWrapper.add_handlers
    .. automethod:: TornadoWrapper.start_app
    .. automethod:: TornadoWrapper.loop
    .. automethod:: TornadoWrapper.listen

Exceptions
----------

.. automodule:: tornado_websockets.exceptions

    .. autoexception:: TornadoWebSocketsError
    .. autoexception:: EmitHandlerError
    .. autoexception:: InvalidWebSocketHandlerInstanceError
    .. autoexception:: NotCallableError
    .. autoexception:: WebSocketEventAlreadyBinded
