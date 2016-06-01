from tornado import gen
from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect

from tornado_websockets.websockethandler import WebSocketHandler

try:
    from tornado import speedups
except ImportError:
    speedups = None


class TestWebSocketHandler(WebSocketHandler):
    """Base class for testing handlers that exposes the on_close event.
    This allows for deterministic cleanup of the associated socket.
    """

    def initialize(self, websocket, close_future, compression_options=None):
        super(TestWebSocketHandler, self).initialize(websocket)
        self.close_future = close_future
        self.compression_options = compression_options

    def get_compression_options(self):
        return self.compression_options

    def on_close(self):
        self.close_future.set_result((self.close_code, self.close_reason))


class EchoHandler(TestWebSocketHandler):
    def on_message(self, message):
        self.write_message(message, isinstance(message, bytes))


class WebSocketBaseTestCase(AsyncHTTPTestCase):
    @gen.coroutine
    def ws_connect(self, path, compression_options=None):
        ws = yield websocket_connect(
            'ws://127.0.0.1:%d%s' % (self.get_http_port(), path),
            compression_options=compression_options
        )

        raise gen.Return(ws)

    @gen.coroutine
    def close(self, ws):
        """Close a websocket connection and wait for the server side.
        If we don't wait here, there are sometimes leak warnings in the
        tests.
        """
        ws.close()
        yield self.close_future
