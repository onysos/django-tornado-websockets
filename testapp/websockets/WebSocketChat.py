from tornado_websockets.WebSocket import WebSocket


class WebSocketChat(WebSocket):
    def run(self):
        @self.on
        def connection(data):
            self.emit('connection', {
                'message': 'Someone join the chat'
            })

        @self.on
        def close(data):
            self.emit('close', {
                'message': 'Someone leave the chat'
            })
