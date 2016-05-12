from six import integer_types

from tornado_websockets.websocket import WebSocket

app_counter_ws = WebSocket('/counter')


class AppCounter(object):
    def __init__(self):
        app_counter_ws.context = self
        self.counter = 0

    @app_counter_ws.on
    def connection(self, socket, data):
        app_counter_ws.emit('connection', {
            'message': 'Got new connection.',
            'counter_value': self.counter,
        })

    @app_counter_ws.on
    def setup(self, socket, data):
        counter = data.get('counter_value')

        if not counter:
            socket.emit('error', {
                'message': 'Setup initial counter value: FAIL.',
                'details': 'Can not get "value" from data.'
            })
        elif not isinstance(counter, integer_types):
            socket.emit('error', {
                'message': 'Setup initial counter value: FAIL.',
                'details': '"value" is not an integer.'
            })
        else:
            self.counter = counter
            app_counter_ws.emit('after_setup', {
                'message': 'Setup initial counter value: OK.',
                'counter_value': self.counter,
            })

    @app_counter_ws.on
    def increment(self, socket, data):
        self.counter += 1

        app_counter_ws.emit('incremented_counter', {
            'counter_value': self.counter
        })

    @app_counter_ws.on
    def close(self, socket, data):
        print('-- WebSocket is closed')


app_counter = AppCounter()
