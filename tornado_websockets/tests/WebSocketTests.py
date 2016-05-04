from tornado_websockets.WebSocket import WebSocket


class WebSocketFirstTest(WebSocket):
    def register_events(self):
        @self.on
        def connection(data=None):
            print("@@ NEW CONNECTION")

            self.emit('got_connection', {
                'message': 'I got a new connection!'
            })

        @self.on('my_event')
        def my_method(data):
            print('EVENT_1')

        @self.on
        def quit(data):
            self.emit('quit', {
                'message': 'Someone quit the websocket'
            })


class WebSocketSecondTest(WebSocket):
    def register_events(self):
        @self.on('EVENT_2')
        def non(data):
            print('NON')
