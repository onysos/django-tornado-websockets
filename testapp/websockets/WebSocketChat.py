from tornado_websockets.WebSocket import WebSocket


class WebSocketChat(WebSocket):
    def register_events(self):
        @self.on
        def connection():
            self.emit('connection', {
                'message': 'Someone join the chat'
            })

        @self.on
        def message(data):
            self.emit('message', 'Someone said: %s' % data.get('message'))

        @self.on
        def close():
            self.emit('close', {
                'message': 'Someone leave the chat'
            })
