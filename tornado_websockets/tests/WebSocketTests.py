from tornado_websockets.WebSocket import WebSocket


class WebSocketFirstTest(WebSocket):
    def register_events(self):
        @self.on
        def connection():
            print("@@ NEW CONNECTION")

            self.emit('connection', 'New connection')

        @self.on('my_event')
        def my_method(data):
            self.emit('my_event', {
                'message': ''
            })

        @self.on
        def close():
            self.emit('close', {
                'message': 'Someone close the websocket'
            })


class WebSocketSecondTest(WebSocket):
    def register_events(self):
        pass
