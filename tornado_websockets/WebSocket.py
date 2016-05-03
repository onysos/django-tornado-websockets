import tornado.escape
import tornado.websocket


class WebSocket(tornado.websocket.WebSocketHandler):
    CHANNEL_DEFAULT = 'default'

    def __init__(self, *args, **kwargs):
        super(WebSocket, self).__init__(*args, **kwargs)

        self._channels = {self.CHANNEL_DEFAULT: []}
        self._events = {}

    def on_message(self, message):

        print('Message received: %s' % str(message))

        try:
            message = tornado.escape.json_decode(message)
            event = message.get('event', 'message')
            data = message.get('data', {})
        except ValueError:  # It's a JSON
            event = 'message'
            data = {'message': message}

        self.write_message('Event: %s\nData: %s' % (event, str(data)))

    def on(self):
        pass
