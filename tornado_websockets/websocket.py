import inspect

from six import string_types, wraps

import tornado_websockets.exceptions
import tornado_websockets.wrappers


class WebSocket(object):
    """
        Class that you SHOULD use to use Tornado websockets
    """

    def __init__(self, url):
        self.events = {}
        self.context = None
        self.handlers = []

        self.namespace = url.strip()
        if self.namespace[0:1] is not '/':
            self.namespace = '/' + self.namespace

        tornado_websockets.wrappers.TornadoWrapper.add_handlers([
            ('/ws' + self.namespace, tornado_websockets.wrappers.WebSocketHandlerWrapper, {
                'websocket': self
            })
        ])

    def on(self, *args):
        def decorator(_fn):
            @wraps(_fn)
            def wrapper(self, *args, **kwargs):
                print('WRAPPER(%s, %s, %s)' % (self, args, kwargs))
                return _fn(self, *args, **kwargs)

            return wrapper

        # print('ON ARGS: %s' % args)

        if len(args) < 1:
            raise ValueError('WebSocket.on decorator take at least one argument.')

        if isinstance(args[0], string_types): # we got an event name
            event = args[0]
            callback = decorator
        elif callable(args[0]): # we got a function
            event = args[0].__name__
            callback = args[0]
        elif inspect.isclass(args[0]):
            raise NotImplementedError('WebSocket.on decorator is not already implemented for classes.')
        else:
            raise ValueError('How the f*ck did you use this decorator???')

        if self.events.get(event) is not None:
            raise tornado_websockets.exceptions.WebSocketEventAlreadyBinded(
                'The event "%s" is already binded for "%s" namespace' % (event, self.namespace)
            )

        print('-- Binding "%s" event for "%s" namespace with callback "%s"' % (event, self.namespace, callback))
        self.events[event] = callback
        return callback

    def emit(self, event, data):
        print('-- WebSocket.emit(%s, %s)' % (event, data))

        if not self.handlers:
            raise tornado_websockets.exceptions.EmitHandlerError(
                'WebSocket handler for "%s" is actually not defined, you should use emit in a function or method '
                'decorated with @websocket.on'
            )

        for handler in self.handlers:
            if not isinstance(handler, tornado_websockets.wrappers.WebSocketHandlerWrapper):
                raise tornado_websockets.exceptions.InvalidInstanceError(
                    'WebSocket handler is not an instance of WebSocketHandlerWrapper, actually it is "%s"' % repr(handler)
                )

            if isinstance(data, string_types):
                data = {'message': data}

            handler.write_message({
                'event': event,
                'data': data
            })
