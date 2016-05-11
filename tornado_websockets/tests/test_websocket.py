from __future__ import absolute_import, division, print_function, with_statement

# I just took the official websocket test file from Tornado
# https://github.com/tornadoweb/tornado/blob/master/tornado/test/websocket_test.py
# and modify it for my project.

import traceback

from tornado.concurrent import Future
from tornado import gen
from tornado.testing import AsyncHTTPTestCase, gen_test

from tornado_websockets.tests.websocket_counter import ws_counter
from tornado_websockets.tornadowrapper import TornadoWrapper

try:
    import tornado.websocket  # noqa
    from tornado.util import _websocket_mask_python
except ImportError:
    # The unittest module presents misleading errors on ImportError
    # (it acts as if websocket_test could not be found, hiding the underlying
    # error).  If we get an ImportError here (which could happen due to
    # TORNADO_EXTENSION=1), print some extra information before failing.
    traceback.print_exc()
    raise

from tornado.websocket import WebSocketHandler, websocket_connect

try:
    from tornado import speedups
except ImportError:
    speedups = None


class TestWebSocketHandler(WebSocketHandler):
    """Base class for testing handlers that exposes the on_close event.
    This allows for deterministic cleanup of the associated socket.
    """

    def initialize(self, close_future, compression_options=None):
        self.close_future = close_future
        self.compression_options = compression_options

    def get_compression_options(self):
        return self.compression_options

    def on_close(self):
        self.close_future.set_result((self.close_code, self.close_reason))


class WebSocketBaseTestCase(AsyncHTTPTestCase):
    @gen.coroutine
    def ws_connect(self, path, compression_options=None):
        ws = yield websocket_connect(
            'ws://127.0.0.1:%d%s' % (self.get_http_port(), path),
            compression_options=compression_options)
        raise gen.Return(ws)

    @gen.coroutine
    def close(self, ws):
        """Close a websocket connection and wait for the server side.
        If we don't wait here, there are sometimes leak warnings in the
        tests.
        """
        ws.close()
        yield self.close_future


class WebSocketTest(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()

        # TornadoWrapper.add_handlers([
        #     ('/ws/counter', WebSocketHandler, dict(websocket=ws_counter, close_future=self.close_future)),
        # ])
        TornadoWrapper.start_app([], {})
        return TornadoWrapper.tornado_app

    def test_http_request(self):
        # WS server, HTTP client.
        response = self.fetch('/ws/counter')
        self.assertEqual(response.code, 400)

    @gen_test
    def test_websocket_gen(self):
        ws = yield self.ws_connect('/ws/counter')
        yield ws.write_message('hello')
        response = yield ws.read_message()
        self.assertEqual(response, 'hello')
        yield self.close(ws)
