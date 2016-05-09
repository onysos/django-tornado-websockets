import inspect
import pprint

import tornado
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

import tornado_websockets.exceptions
import tornado_websockets.websocket

pp = pprint.PrettyPrinter(indent=4)


class TornadoWrapper:
    """
        Wrapper for Tornado application and server handling.
        With this class, you can access to Tornado app, handlers and settings everywhere in your code (it's really
        useful for runtornado command and WebSockets)
    """

    tornado_app = None
    tornado_server = None
    tornado_handlers = None
    tornado_settings = None

    # Default values for user configuration
    tornado_port = 8000
    handlers = []

    @classmethod
    def start_app(cls, tornado_handlers, tornado_settings):
        """
            Initialize the Tornado web application with given handlers and settings

            :param tornado_handlers: Handlers (route) for Tornado
            :param tornado_settings: Settings for Tornado
            :type tornado_handlers: list
            :type tornado_settings: dict
            :return: None
        """

        # Not `tornado_handlers += cls.handlers` because wildcard handler should be the last value in handlers list
        # http://www.tornadoweb.org/en/stable/_modules/tornado/web.html#Application.add_handlers
        tornado_handlers = cls.handlers + tornado_handlers

        cls.tornado_app = tornado.web.Application(tornado_handlers, **tornado_settings)

    @classmethod
    def listen(cls, tornado_port):
        """
            Start the Tornado HTTP server on given port

            :param tornado_port: Port to listen
            :type tornado_port: int
            :return: None

            .. todo:: Add support for HTTPS server
        """
        cls.tornado_port = tornado_port
        tornado_server = tornado.httpserver.HTTPServer(cls.tornado_app)
        tornado_server.listen(cls.tornado_port)

    @classmethod
    def loop(cls):
        """
            Run Tornado main loop and display configuration about Tornado handlers and settings

            :return: None
        """
        print('== Using port %s' % cls.tornado_port)
        print('== Using handlers:')
        pp.pprint(cls.tornado_app.handlers)
        print('== Using settings:')
        pp.pprint(cls.tornado_app.settings)

        tornado.ioloop.IOLoop.instance().start()

    @classmethod
    def add_handlers(cls, handlers):
        """
            Add an handler to Tornado app if it's defined, otherwise it's add this handler to the
            TornadoWrapper.tornado_handlers list

            :param handlers: Handlers to add
            :type handlers: list
            :return: Tornado application handlers
            :rtype: list
        """

        if not TornadoWrapper.tornado_app:
            print('== Prepare new handlers for Tornado application:')
            pp.pprint(handlers)

            # ``cls.handlers = handlers + cls.handlers`` and not ``cls.handlers += handlers``,
            # see `TornadoWrapper.start_app` source to know why.
            cls.handlers = handlers + cls.handlers

            return cls.handlers

        print('== Adding handlers to already running Tornado application. New handlers are:')
        TornadoWrapper.tornado_app.add_handlers('.*', handlers)
        pp.pprint(cls.tornado_app.handlers)

        return cls.tornado_app.handlers


class WebSocketHandlerWrapper(tornado.websocket.WebSocketHandler):
    """


    """

    def __init__(self, application, request, **kwargs):
        super(WebSocketHandlerWrapper, self).__init__(application, request, **kwargs)

        self.websocket = None

    def initialize(self, websocket):

        if not isinstance(websocket, tornado_websockets.websocket.WebSocket):
            raise tornado_websockets.exceptions.InvalidInstanceError(
                '"websocket" parameter from "WebSocketHandlerWrapper.initialize" method '
                'should be an instance of "tornado_websockets.WebSocket", got "%s" instead' % repr(websocket))

        # Set link from handler to websocket
        self.websocket = websocket
        # Set link from websocket to handler
        websocket.handlers.append(self)

        print('HANDLER: %s' % self)
        print('WEBSOCKET: %s' % self.websocket)

    def on_message(self, message):
        # print('MESSAGE: %s' % message)

        try:
            message = tornado.escape.json_decode(message)
            namespace = message.get('namespace')
            event = message.get('event')
            data = message.get('data')
        except ValueError:
            self.emit_error('Invalid JSON was sent.')
            return

        if not event:
            self.emit_error('There is no event in this JSON.')
            return
        elif self.websocket.events.get(event) is None:
            self.emit_error('The event "%s" does not exist for websocket "%s"' % (event, self.websocket))
            return

        if not data:
            data = {}
        elif data and not isinstance(data, dict):
            self.emit_error('The data should be a dictionary (JavaScript object).')
            return

        # print('NAMESPACE: %s' % namespace)
        # print('EVENT: %s' % event)
        # print('DATA: %s' % data)

        callback = self.websocket.events.get(event)
        spec = inspect.getargspec(callback)
        kwargs = {}

        # print('SPEC: %s' % str(spec))

        if 'self' in spec.args:
            kwargs['self'] = self.websocket.context
        if len(spec.args) > 1 and spec.args[1]:
            kwargs[spec.args[1]] = data

        # print('CALLBACK: %s' % callback)
        # print('KWARGS: %s' % kwargs)

        print('-- Triggering "%s" event from "%s" namespace' % (event, namespace))

        return callback(**kwargs)

    def on_close(self):
        print('-- on_close()')
        self.websocket.handlers.remove(self)

    def emit(self, event, data):
        self.write_message(tornado.escape.json_encode({
            'event': event,
            'data': data
        }))

    def emit_error(self, message):
        print('-- Error: %s' % message)
        return self.emit('error', {'message': message})
