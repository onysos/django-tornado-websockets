from tornado_websockets.WebSocket import WebSocket


class WebSocketChat(WebSocket):
    @WebSocket.on('connection')
    def on_connection(self, data):
        pass

    @WebSocket.on('foo')
    def on_foo(self, data):
        pass
