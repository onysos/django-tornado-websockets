# coding: utf-8

from __future__ import absolute_import, division, print_function, with_statement

# I just took the official websocket test file from Tornado
# https://github.com/tornadoweb/tornado/blob/master/tornado/test/websocket_test.py
# and modify it for my project.

import traceback
import pprint

from tornado.concurrent import Future
from tornado import gen
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.httpclient import HTTPError
from tornado.escape import json_decode, json_encode

from tornado_websockets.tests.app_test import app_test_ws
from tornado_websockets.tests.app_counter import app_counter
from tornado_websockets.tornadowrapper import TornadoWrapper

pp = pprint.PrettyPrinter(indent=2)

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


# --- HERE BEGIN REAL TESTS ---------------------------------------------------------------------------------------- #

class WebSocketTest(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()
        TornadoWrapper.start_app()
        return TornadoWrapper.tornado_app

    def tearDown(self):
        pass

    @gen_test
    def test_connection_existing_websocket(self):
        ws_test = yield self.ws_connect('/ws/counter')
        ws_counter = yield self.ws_connect('/ws/counter')

        # Useless, but just in case of. :-))
        self.assertEqual(None, ws_test.close_code)
        self.assertEqual(None, ws_test.close_reason)
        self.assertEqual(None, ws_counter.close_code)
        self.assertEqual(None, ws_counter.close_reason)

    @gen_test
    def test_connection_no_existing_websocket(self):
        with self.assertRaises(HTTPError) as e:
            yield self.ws_connect('/ws/i/do/not/exist')

        self.assertEqual(e.exception.message, 'Not Found')
        self.assertEqual(e.exception.code, 404)

    # --- Tests for WSTestApp

    @gen_test
    def test_testapp_send_invalid_json(self):
        ws = yield self.ws_connect('/ws/test')

        yield ws.write_message('Not a JSON string.')

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'Invalid JSON was sent.',
            }
        })

        yield ws.write_message(json_encode({'event': 'close'}))

    @gen_test
    def test_testapp_send_without_event(self):
        ws = yield self.ws_connect('/ws/test')

        yield ws.write_message(json_encode({
            'json': 'I am a JSON'
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'There is no event in this JSON.',
            }
        })

    @gen_test
    def test_testapp_send_with_not_registered_event(self):
        ws = yield self.ws_connect('/ws/test')

        yield ws.write_message(json_encode({
            'event': 'not_registered_event'
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'The event "not_registered_event" does not exist for websocket "%s".' % app_test_ws,
            }
        })

    @gen_test
    def test_testapp_send_with_registered_event(self):
        ws = yield self.ws_connect('/ws/test')

        yield ws.write_message(json_encode({
            'event': 'existing_event'
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'existing_event',
            'data': {
                'message': 'I am "existing_event" from "%s" websocket application.' % app_test_ws,
                'passed_data': {}
            }
        })

    @gen_test
    def test_testapp_send_with_invalid_data_format(self):
        ws = yield self.ws_connect('/ws/test')

        yield ws.write_message(json_encode({
            'event': 'existing_event', 'data': 'not a dictionary'
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'The data should be a dictionary.',
            }
        })

    @gen_test
    def test_testapp_send_with_registered_event(self):
        ws = yield self.ws_connect('/ws/test')

        yield ws.write_message(json_encode({
            'event': 'existing_event',
            'data': {
                'a_key': 'a_value'
            }
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'existing_event',
            'data': {
                'message': 'I am "existing_event" from "%s" websocket application.' % app_test_ws,
                'passed_data': {
                    'a_key': 'a_value'
                }
            }

        })

    # --- Tests for WSCounterApp

    @gen_test
    def test_counterapp_emit_connection(self):
        ws = yield self.ws_connect('/ws/counter')

        yield ws.write_message(json_encode({
            'event': 'connection'
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'connection',
            'data': {
                'message': 'Got new connection.',
                'counter_value': 0  # Initial value of counter
            }
        })

    @gen_test
    def test_counterapp_emit_setup_without_counter_value(self):
        ws = yield self.ws_connect('/ws/counter')

        yield ws.write_message(json_encode({
            'event': 'setup'
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'Setup initial counter value: FAIL.',
                'details': 'Can not get "value" from data.'
            }
        })

    @gen_test
    def test_counterapp_emit_setup_with_bad_counter_value_type(self):
        ws = yield self.ws_connect('/ws/counter')

        yield ws.write_message(json_encode({
            'event': 'setup',
            'data': {
                'counter_value': 'not_an_integer'
            }
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'Setup initial counter value: FAIL.',
                'details': '"value" is not an integer.'
            }
        })

    @gen_test
    def test_counterapp_emit_setup_with_good_value(self):
        counter_value = 50
        ws = yield self.ws_connect('/ws/counter')

        # Tests for first client

        self.assertEqual(app_counter.counter, 0)

        yield ws.write_message(json_encode({
            'event': 'setup',
            'data': {
                'counter_value': counter_value
            }
        }))

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'after_setup',
            'data': {
                'message': 'Setup initial counter value: OK.',
                'counter_value': counter_value
            }
        })

        self.assertEqual(app_counter.counter, counter_value)

        # Tests for second client

        counter_value += 1  # 51
        ws2 = yield self.ws_connect('/ws/counter')

        yield ws2.write_message(json_encode({'event': 'increment'}))

        response = yield ws2.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'incremented_counter',
            'data': {
                'counter_value': counter_value  # 51
            }
        })

        self.assertEqual(app_counter.counter, counter_value)
