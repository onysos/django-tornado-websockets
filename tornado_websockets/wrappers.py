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
    tornado_app = None
    tornado_server = None
    tornado_handlers = None
    tornado_settings = None

    # Default values for user configuration
    tornado_port = 8000
    handlers = []

    @classmethod
    def start_app(cls, tornado_handlers, tornado_settings):
        # Not `tornado_handlers += cls.handlers` because wildcard handler should be the last
        # http://www.tornadoweb.org/en/stable/_modules/tornado/web.html#Application.add_handlers
        tornado_handlers = cls.handlers + tornado_handlers

        cls.tornado_app = tornado.web.Application(tornado_handlers, **tornado_settings)

    @classmethod
    def listen(cls, tornado_port):
        cls.tornado_port = tornado_port
        tornado_server = tornado.httpserver.HTTPServer(cls.tornado_app)
        tornado_server.listen(cls.tornado_port)

    @classmethod
    def loop(cls):
        print('== Using port %s' % cls.tornado_port)
        print('== Using handlers:')
        pp.pprint(cls.tornado_app.handlers)
        print('== Using settings:')
        pp.pprint(cls.tornado_app.settings)

        tornado.ioloop.IOLoop.instance().start()

    @classmethod
    def add_handlers(cls, handlers):
        if TornadoWrapper.tornado_app is not None:
            TornadoWrapper.tornado_app.add_handlers('.*', handlers)
            print('== Adding handlers to already running Tornado application. New handlers are:')
            pp.pprint(cls.tornado_app.handlers)
        else:
            print('== Prepare new handlers for Tornado application :')
            pp.pprint(handlers)
            cls.handlers = handlers + cls.handlers


class WebSocketHandlerWrapper(tornado.websocket.WebSocketHandler):
    namespaces = {}

    def initialize(self, websocket):

        if not isinstance(websocket, tornado_websockets.websocket.WebSocket):
            raise tornado_websockets.exceptions.InvalidWebSocketInstance(
                '"websocket" parameter from "WebSocketHandlerWrapper.initialize" method '
                'should be an instance of "tornado_websockets.WebSocket", got "%s" instead' % repr(websocket))

        # Set link from websocket to handler
        websocket.handler = self

        # Set link from handler to websocket
        WebSocketHandlerWrapper.namespaces.update({
            websocket.namespace: websocket
        })

    def on_message(self, message):
        print('MESSAGE: %s' % message)
        socket = None

        try:
            message = tornado.escape.json_decode(message)
            namespace = message.get('namespace')
            event = message.get('event')
            data = message.get('data')
        except(ValueError):
            self.emit_error('Invalid JSON was sent.')
            return

        if not namespace:
            self.emit_error('There is no namespace in this JSON.')
            return
        else:
            socket = WebSocketHandlerWrapper.namespaces.get(namespace)

            if socket is None:
                self.emit_error('The namespace "%s" does not exist.' % namespace)
                return

        if not event:
            self.emit_error('There is no event in this JSON.')
            return
        elif socket.events.get(event) is None:
            self.emit_error('The event "%s" does not exist in the namespace "%s".' % (event, namespace))
            return

        if not data:
            data = {}
        elif data and not isinstance(data, dict):
            self.emit_error('The data should be a dictionary (JavaScript object).')
            return

        # print('NAMESPACE: %s' % namespace)
        # print('EVENT: %s' % event)
        # print('DATA: %s' % data)

        callback = socket.events.get(event)
        spec = inspect.getargspec(callback)
        kwargs = {}

        # print('SPEC: %s' % str(spec))

        if 'self' in spec.args:
            kwargs['self'] = socket.context
        if len(spec.args) > 1 and spec.args[1]:
            kwargs[spec.args[1]] = data

        # print('KWARGS: %s' % kwargs)

        print('-- Triggering "%s" event from "%s" namespace' % (event, namespace))
        callback(**kwargs)

    def emit(self, event, data):
        self.write_message(tornado.escape.json_encode({
            'event': event,
            'data': data
        }))

    def emit_error(self, message):
        print('-- Error: %s' % message)
        return self.emit('error', {'message': message})
