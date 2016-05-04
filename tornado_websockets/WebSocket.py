import inspect

import tornado.escape
import tornado.websocket


class WebSocket(tornado.websocket.WebSocketHandler):
    CHANNEL_DEFAULT = 'default'

    instances = []

    def __init__(self, *args, **kwargs):
        super(WebSocket, self).__init__(*args, **kwargs)
        self._events = {}
        self.channels = {self.CHANNEL_DEFAULT: []}

        self.setup()

    def setup(self):
        self.register_events()

    def register_events(self):
        """
        Should be implemented by a
        :return:
        """
        raise NotImplementedError

    def on(self, *args):
        """
        Bind easily an event on a WebSocket method

        Example:
            @self.on
            def my_event(...):
                ...

            @self.on('my_event')
            def another_function(...):
                ...

        :param args: Event name or a function
        :return:
        """

        def decorator(func):
            return func

        if len(args) == 0:
            raise ValueError("WebSocket.on decorator should have at least one argument")

        # args[0] is a string
        event = args[0]
        callback = decorator

        # args[0] is a function
        if callable(args[0]):
            event = args[0].__name__
            callback = decorator(args[0])

        self._events[event] = callback

        return callback

    def emit(self, event, data):
        print('.. WebSocket.emit(%s, %s)' % (event, data))

        if not isinstance(data, dict):
            data = {'message': data}

        message = {
            'event': event,
            'data': data
        }

        message = tornado.escape.json_encode(message)
        self.write_message(message)

        pass

    def on_message(self, message):
        print('-- Message received: %s' % str(message))

        try:
            message = tornado.escape.json_decode(message)
            event = message.get('event', 'message')
            data = message.get('data', None)
        except ValueError:  # It's a JSON
            event = 'message'
            data = {'message': message}

        if not self._events.get(event):
            msg = 'Event "%s" is not implemented' % event

            print('-- Warning: %s' % msg)
            self.emit('error', {
                'message': msg
            })

            return

        spec = inspect.getargspec(self._events[event])

        if not spec.args:
            return self._events[event]()

        return self._events[event](data)
