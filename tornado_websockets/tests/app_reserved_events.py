from tornado_websockets.websocket import WebSocket

app_reserved_events_ws = WebSocket('/reserved_events', add_to_handlers=False)


class AppReservedEvents(object):
    def __init__(self):
        app_reserved_events_ws.context = self
        self.users = []

    @app_reserved_events_ws.on
    def open(self, socket):
        print('APP_RESERVED_EVENTS: OPEN')
        self.users.append(socket)

    @app_reserved_events_ws.on
    def close(self, socket):
        print('APP_RESERVED_EVENTS: CLOSE')
        self.users.remove(self)


app_reserved_events = AppReservedEvents()
