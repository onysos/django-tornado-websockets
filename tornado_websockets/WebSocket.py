import tornado.websocket


class WebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print("Someone said: %s" % message)
        self.write_message(u"You said: %s" % message)

    def on_close(self):
        print("WebSocket closed")
