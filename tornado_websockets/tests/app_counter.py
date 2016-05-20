from six import integer_types

from tornado_websockets.websocket import WebSocket

app_counter_ws = WebSocket('/counter', add_to_handlers=False)


class AppCounter(object):
    def __init__(self):
        app_counter_ws.context = self
        self.counter = 0

    @app_counter_ws.on
    def open(self, socket):
        app_counter_ws.emit('counter_connection', {
            'message': 'Got new connection.',
            'counter_value': self.counter,
        })

    @app_counter_ws.on
    def setup(self, socket, data):
        counter = data.get('counter_value')

        if not counter:
            socket.emit('counter_error', {
                'message': 'Setup initial counter value: FAIL.',
                'details': 'Can not get "value" from data.'
            })
        elif not isinstance(counter, integer_types):
            socket.emit('counter_error', {
                'message': 'Setup initial counter value: FAIL.',
                'details': '"value" is not an integer.'
            })
        else:
            self.counter = counter
            app_counter_ws.emit('counter_after_setup', {
                'message': 'Setup initial counter value: OK.',
                'counter_value': self.counter,
            })

    @app_counter_ws.on
    def increment(self, socket, data):
        self.counter += 1

        app_counter_ws.emit('counter_increment', {
            'counter_value': self.counter
        })


app_counter = AppCounter()
