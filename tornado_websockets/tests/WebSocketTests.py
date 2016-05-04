from tornado_websockets.WebSocket import WebSocket


class WebSocketFirstTest(WebSocket):
    def __init__(self, *args, **kwargs):
        super(WebSocketFirstTest, self).__init__(*args, **kwargs)
        self.counter = None

    def register_events(self):
        @self.on
        def connection():
            print("@@ NEW CONNECTION")

            self.emit('connection', 'New connection')

        @self.on
        def setup_counter(data):
            self.counter = data.get('value', 100)

        @self.on
        def increment_counter(data):
            self.counter += 1

            self.emit('incremented_counter', {
                'value': self.counter
            })

        @self.on
        def close():
            self.emit('close', {
                'message': 'Someone close the websocket'
            })


class WebSocketSecondTest(WebSocket):
    def register_events(self):
        pass
