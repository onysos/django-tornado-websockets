from tornado_websockets.websocket import WebSocket

app_test_ws = WebSocket('/test', add_to_handlers=False)


class AppTest(object):
    def __init__(self):
        app_test_ws.context = self

    @app_test_ws.on
    def existing_event(self, socket, data):
        app_test_ws.emit('existing_event', {
            'message': 'I am "existing_event" from "%s" websocket application.' % app_test_ws,
        })


app_test = AppTest()
