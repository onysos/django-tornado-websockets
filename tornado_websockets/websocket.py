import inspect

from six import string_types

import tornado_websockets.exceptions
import tornado_websockets.wrappers


class WebSocket(object):
    def __init__(self, url):
        self.events = {}
        self.context = None
        self.handler = None

        self.namespace = url.strip()
        if self.namespace[0:1] is not '/':
            self.namespace = '/' + self.namespace

        tornado_websockets.wrappers.TornadoWrapper.add_handlers([
            ('/ws' + self.namespace, tornado_websockets.wrappers.WebSocketHandlerWrapper, {'websocket': self})
        ])

    def on(self, *args):
        def decorator(func):
            return func

        if len(args) < 1:
            raise ValueError('WebSocket.on decorator take at least one argument.')

        if isinstance(args[0], string_types):
            event = args[0]
            callback = decorator
        elif callable(args[0]):
            event = args[0].__name__
            callback = decorator(args[0])
        elif inspect.isclass(args[0]):
            raise NotImplementedError('WebSocket.on decorator is not already implemented for classes.')
        else:
            raise ValueError('How the f*ck did you use this decorator???')

        if self.events.get(event) is not None:
            raise tornado_websockets.exceptions.WebSocketEventAlreadyBinded(
                'The event "%s" is already binded for "%s" namespace' % (event, self.namespace)
            )

        print('-- Binding "%s" event for "%s" namespace' % (event, self.namespace))
        self.events[event] = callback
        return decorator

    def emit(self, event, data):
        print('-- WebSocket.emit(%s, %s)' % (event, data))
        print('-- HANDLER: %s' % self.handler)

        if not self.handler:
            raise tornado_websockets.exceptions.EmitHandlerException(
                'WebSocket handler for "%s" is actually not defined, you should use emit in a function or method '
                'decorated with @websocket.on'
            )

        pass
