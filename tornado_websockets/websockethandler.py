import inspect

import tornado
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

import tornado_websockets.exceptions
import tornado_websockets.websocket


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(WebSocketHandler, self).__init__(application, request, **kwargs)

    def initialize(self, websocket):

        if not isinstance(websocket, tornado_websockets.websocket.WebSocket):
            raise tornado_websockets.exceptions.InvalidInstanceError(
                '"websocket" parameter from "WebSocketHandlerWrapper.initialize" method '
                'should be an instance of "tornado_websockets.WebSocket", got "%s" instead' % repr(websocket))

        # Set link from handler to websocket
        self.websocket = websocket
        # Set link from websocket to handler
        websocket.handlers.append(self)

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
        if 'socket' in spec.args:
            kwargs['socket'] = self
        if 'data' in spec.args:
            kwargs['data'] = data

        # print('CALLBACK: %s' % callback)
        # print('KWARGS: %s' % kwargs)

        print('-- Triggering "%s" event from "%s" namespace' % (event, namespace))

        return callback(**kwargs)

    def on_close(self):
        print('-- on_close()')
        self.websocket.handlers.remove(self)

    def emit(self, event, data):
        self.write_message({
            'event': event,
            'data': data
        })

    def emit_error(self, message):
        print('-- Error: %s' % message)
        return self.emit('error', {'message': message})
