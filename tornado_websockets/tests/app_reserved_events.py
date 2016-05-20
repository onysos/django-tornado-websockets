from tornado_websockets.websocket import WebSocket

app_reserved_events_ws = WebSocket('/reserved_events', add_to_handlers=False)


class AppReservedEvents(object):
    def __init__(self):
        app_reserved_events_ws.context = self
        self.connections = []

    @app_reserved_events_ws.on
    def open(self, socket):
        self.connections.append(socket)

        app_reserved_events_ws.emit('new_connection', {
            'connections_count': len(self.connections)
        })

    @app_reserved_events_ws.on
    def close(self, socket):
        self.connections.remove(socket)

        app_reserved_events_ws.emit('close_connection', {
            'connections_count': len(self.connections)
        })


app_reserved_events = AppReservedEvents()
