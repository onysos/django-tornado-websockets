import inspect

import tornado.escape
import tornado.websocket


class WebSocketHandlerWrapper(tornado.websocket.WebSocketHandler):
    namespaces = {}

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
