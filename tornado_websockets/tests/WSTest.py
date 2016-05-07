from tornado_websockets.WebSocket import WebSocket

ws_first = WebSocket('/test')


class WSTest(object):
    def __init__(self):
        self.counter = None

    @ws_first.on
    def connection(self):
        print("-- Got new connection")

        ws_first.emit('connection', 'New connection')

    @ws_first.on('setup_counter')
    def my_method_lol(self, data):
        self.counter = data.get('value', 100)

    @ws_first.on
    def update_counter(self, data):
        self.counter = data.get('counter')

        ws_first.emit('incremented_counter', {
            'value': self.counter
        })

    @ws_first.on
    def close(self):
        print('-- WebSocket is closed')


class WebSocketSecondTest(object):
    pass
