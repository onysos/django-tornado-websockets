from six import string_types

import tornado_websockets.tornadowrapper
import tornado_websockets.websockethandler
from tornado_websockets.exceptions import *


class WebSocket(object):
    """
        Class that you should use Tornado WebSockets
    """

    def __init__(self, url):
        self.events = {}
        self.context = None
        self.handlers = []

        self.namespace = url.strip()
        if self.namespace[0:1] is not '/':
            self.namespace = '/' + self.namespace

        tornado_websockets.tornadowrapper.TornadoWrapper.add_handlers([
            ('/ws' + self.namespace, tornado_websockets.websockethandler.WebSocketHandler, {
                'websocket': self
            })
        ])

    def on(self, *args):
        # print('ON ARGS: %s' % args)

        if len(args) < 1:
            raise ValueError('WebSocket.on decorator take at least one argument.')

        if not callable(args[0]):
            raise NotCallableError(args[0])

        event = args[0].__name__
        callback = args[0]

        if self.events.get(event) is not None:
            raise WebSocketEventAlreadyBinded(event, self.namespace)

        print('-- Binding "%s" event for "%s" namespace with callback "%s"' % (event, self.namespace, callback))
        self.events[event] = callback
        return callback

    def emit(self, event, data):
        print('-- WebSocket.emit(%s, %s)' % (event, data))

        if not self.handlers:
            raise EmitHandlerError(event, data)

        for handler in self.handlers:
            if not isinstance(handler, tornado_websockets.websockethandler.WebSocketHandler):
                raise InvalidWebSocketHandlerInstanceError(handler)

            if isinstance(data, string_types):
                data = {'message': data}

            handler.emit(event, data)
