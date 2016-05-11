from six import string_types

import tornado_websockets.tornadowrapper
import tornado_websockets.websockethandler
from tornado_websockets.exceptions import *


class WebSocket(object):
    """
        Class that you should to make WebSocket applications 👍.
    """

    def __init__(self, url):
        self.events = {}
        self.handlers = []
        self.context = None

        self.namespace = url.strip()
        if self.namespace[:1] is not '/':
            self.namespace = '/' + self.namespace

        tornado_websockets.tornadowrapper.TornadoWrapper.add_handlers([
            ('/ws' + self.namespace, tornado_websockets.websockethandler.WebSocketHandler, {
                'websocket': self
            })
        ])

    def on(self, callback):
        """
            Execute a callback when an event is received from a client, should be used as a decorator for a function or a
            class method.

            Event name is determined by function/method ``__name__`` attribute.

            :param callback: Function or a class method.
            :type callback: Callable
            :return: ``callback`` parameter.

            :Example:
                 >>> ws = WebSocket('/example')
                 >>> @ws.on
                 ... def my_event(socket, data):
                 ...     print('Received "my_event" event from a client.')
        """

        if not callable(callback):
            raise NotCallableError(callback[0])

        event = callback.__name__

        if self.events.get(event) is not None:
            raise WebSocketEventAlreadyBinded(event, self.namespace)

        print('-- Binding "%s" event for "%s" namespace with callback "%s"' % (event, self.namespace, callback))
        self.events[event] = callback
        return callback

    def emit(self, event, data):
        """
            Send an event/data dictionnary to all clients connected to your WebSocket instance.
            To see all ways to emit an event, please read « :ref:`emit-an-event` » section.

            :param event: event name
            :param data: a dictionary or a string which will be converted to ``{'message': data}``
            :type event: str
            :type data: dict or str
            :raise: :class:`~tornado_websockets.exceptions.EmitHandlerError` if not used inside :meth:`@WebSocket.on() <tornado_websockets.websocket.WebSocket.on>` decorator.
            :raise: :class:`tornado.websocket.WebSocketClosedError` if connection is closed.

            .. warning::
                :meth:`WebSocket.emit() <tornado_websockets.websocket.WebSocket.emit>` method should be used inside
                a function or a class method decorated by :meth:`@WebSocket.on()
                <tornado_websockets.websocket.WebSocket.on>` decorator, otherwise it will raise a
                :class:`~tornado_websockets.exceptions.EmitHandlerError` exception.
        """

        print('-- WebSocket.emit(%s, %s)' % (event, data))

        if not self.handlers:
            raise EmitHandlerError(event, data)

        for handler in self.handlers:
            if not isinstance(handler, tornado_websockets.websockethandler.WebSocketHandler):
                raise InvalidInstanceError(handler, 'tornado_websockets.websockethandler.WebSocketHandler')

            if isinstance(data, string_types):
                data = {'message': data}

            handler.emit(event, data)
