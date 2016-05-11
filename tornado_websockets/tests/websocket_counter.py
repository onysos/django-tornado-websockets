from tornado_websockets.websocket import WebSocket

ws_counter = WebSocket('/counter')


class WSCounter(object):
    def __init__(self):
        self.counter = 0
        ws_counter.context = self

    @ws_counter.on
    def connection(self):
        print("-- Got new connection")

        ws_counter.emit('connection', 'New connection')

    @ws_counter.on
    def setup_counter(self, data):
        self.counter = data.get('value', 100)

    @ws_counter.on
    def update_counter(self, data):
        self.counter = data.get('counter')

        ws_counter.emit('incremented_counter', {
            'value': self.counter
        })

    @ws_counter.on
    def close(self):
        print('-- WebSocket is closed')
