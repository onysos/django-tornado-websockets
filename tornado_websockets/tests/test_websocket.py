# coding: utf-8

from __future__ import absolute_import, division, print_function, with_statement

# I just took the official websocket test file from Tornado
# https://github.com/tornadoweb/tornado/blob/master/tornado/test/websocket_test.py
# and modify it for my project.
import os
import traceback

import time

import sys
from unittest import skip

from tornado.concurrent import Future
from tornado import gen
from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPError
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

from tornado_websockets.exceptions import *
from tornado_websockets.tornadowrapper import TornadoWrapper
from tornado_websockets.websocket import WebSocket
from tornado_websockets.websockethandler import WebSocketHandler
from tornado_websockets.tests.app_counter import app_counter, app_counter_ws
from tornado_websockets.tests.app_test import app_test_ws

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

from tornado.websocket import websocket_connect

try:
    from tornado import speedups
except ImportError:
    speedups = None

# For Travis
if os.environ.get('TRAVIS') is None:
    SLEEPING_TIME = 0
else:
    SLEEPING_TIME = 2


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


# --- HERE BEGIN REAL TESTS ---------------------------------------------------------------------------------------- #

class WebSocketTest(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()

        return Application([
            ('/ws/test', TestWebSocketHandler, {'websocket': app_test_ws, 'close_future': self.close_future}),
        ])

    @gen_test
    def test_connection_existing_websocket(self):
        ws_test = yield self.ws_connect('/ws/test')

        time.sleep(SLEEPING_TIME)

        # Useless, but just in case of. :-))
        self.assertEqual(None, ws_test.close_code)
        self.assertEqual(None, ws_test.close_reason)

    @gen_test
    def test_connection_no_existing_websocket(self):
        with self.assertRaises(HTTPError) as e:
            yield self.ws_connect('/ws/i/do/not/exist')

        time.sleep(SLEEPING_TIME)

        self.assertEqual(e.exception.message, 'Not Found')
        self.assertEqual(e.exception.code, 404)

    @gen_test
    def test_namespace(self):
        ws1 = WebSocket('/prefixed_with_slash')
        ws2 = WebSocket('not_prefixed_with_slash')
        ws3 = WebSocket('   /prefixed_with_slash_with_spaces    ')
        ws4 = WebSocket('   not_prefixed_with_slash             ')

        time.sleep(SLEEPING_TIME)

        self.assertEqual(ws1.namespace, '/prefixed_with_slash')
        self.assertEqual(ws2.namespace, '/not_prefixed_with_slash')
        self.assertEqual(ws3.namespace, '/prefixed_with_slash_with_spaces')
        self.assertEqual(ws4.namespace, '/not_prefixed_with_slash')

    @gen_test
    def test_add_to_tornado_handlers(self):
        TornadoWrapper.reset()
        self.assertListEqual(TornadoWrapper.handlers, [])

        ws = WebSocket('/my_ws')
        self.assertListEqual(TornadoWrapper.handlers, [
            ('/ws/my_ws', WebSocketHandler, {'websocket': ws})
        ])

    @gen_test
    def test_not_add_to_handlers(self):
        TornadoWrapper.reset()
        self.assertListEqual(TornadoWrapper.handlers, [])

        ws = WebSocket('/my_ws', False)
        self.assertListEqual(TornadoWrapper.handlers, [])
    
    @gen_test
    def test_decorator_on_on_not_callable(self):
        ws = WebSocket('/abc')

        time.sleep(SLEEPING_TIME)

        with self.assertRaises(NotCallableError) as e:
            @ws.on('my_event')
            def my_method():
                pass

        self.assertEqual(e.exception.thing, 'my_event')
        self.assertEqual(
            str(e.exception),
            'Used @WebSocket.on decorator on a thing that is not callable, got: "%s".' % 'my_event'
        )

    @gen_test
    def test_decorator_on_on_callable(self):
        ws = WebSocket('/abc')

        time.sleep(SLEEPING_TIME)

        @ws.on
        def my_method():
            pass

    @gen_test
    def test_decorator_on_with_already_binded_event(self):
        ws = WebSocket('/abc')

        time.sleep(SLEEPING_TIME)

        @ws.on
        def my_method():
            pass

        with self.assertRaises(WebSocketEventAlreadyBinded) as e:
            @ws.on
            def my_method():
                pass

        self.assertEqual(e.exception.event, 'my_method')
        self.assertEqual(e.exception.namespace, '/abc')
        self.assertEqual(
            str(e.exception),
            'The event "%s" is already binded for "%s" namespace.' % ('my_method', '/abc')
        )

    @gen_test
    def test_emit_outside_on_decorator(self):
        ws = WebSocket('/abc')

        time.sleep(SLEEPING_TIME)

        with self.assertRaises(EmitHandlerError) as e:
            ws.emit('my_event', 'my_message')

        self.assertEqual(e.exception.event, 'my_event')
        self.assertEqual(e.exception.namespace, '/abc')
        self.assertEqual(
            str(e.exception),
            'Can not emit "%s" event in "%s" namespace, emit() should be used in a function or class method'
            ' decorated by @WebSocket.on decorator.' % ('my_event', '/abc')
        )

    @gen_test
    def test_emit_with_bad_handlers(self):
        ws = WebSocket('/abc')
        ws.handlers = ['not_an_handler']

        time.sleep(SLEEPING_TIME)

        with self.assertRaises(InvalidInstanceError) as e:
            ws.emit('my_event')

        self.assertEqual(e.exception.actual_instance, 'not_an_handler')
        self.assertEqual(e.exception.expected_instance_name, 'tornado_websockets.websockethandler.WebSocketHandler')
        self.assertEqual(
            str(e.exception),
            'Expected instance of "%s", got "%s" instead.' % (
                'tornado_websockets.websockethandler.WebSocketHandler', repr('not_an_handler')
            )
        )

    @gen_test
    def test_emit_with_bad_parameter_event(self):
        ws = WebSocket('/abc')
        ws.handlers = ['not_an_handler']

        time.sleep(SLEEPING_TIME)

        with self.assertRaises(TypeError) as e:
            ws.emit(12345)

        self.assertEqual(str(e.exception), 'Event should be a string.')

    @gen_test
    def test_emit_with_good_parameter_event(self):
        ws = WebSocket('/abc')
        ws.handlers = ['not_an_handler']

        time.sleep(SLEEPING_TIME)

        # It raises an InvalidInstanceError because we override ws's handlers to dodge EmitHandlerError exception,
        # and we can't get a real WebSocketHandler to use with this ws. But it works
        with self.assertRaises(InvalidInstanceError) as e:
            ws.emit('my_event')

    @gen_test
    def test_emit_with_bad_parameter_data(self):
        ws = WebSocket('/abc')
        ws.handlers = ['handler']

        time.sleep(SLEEPING_TIME)

        with self.assertRaises(TypeError) as e:
            ws.emit('my_event', 123)

        self.assertEqual(str(e.exception), 'Data should be a string or a dictionary.')

    @gen_test
    def test_emit_with_good_parameter_data(self):
        ws = WebSocket('/abc')
        ws.handlers = ['not_an_handler']

        time.sleep(SLEEPING_TIME)

        # It raises an InvalidInstanceError because we override ws's handlers to dodge EmitHandlerError exception,
        # and we can't get a real WebSocketHandler to use with this ws. But it works.
        with self.assertRaises(InvalidInstanceError):
            ws.emit('my_event')

        with self.assertRaises(InvalidInstanceError):
            ws.emit('my_event', {'a': 'dictionary'})

        with self.assertRaises(InvalidInstanceError):
            ws.emit('my_event', 'a_string')


class WebSocketTestAppTest(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()

        return Application([
            ('/ws/test', TestWebSocketHandler, {'websocket': app_test_ws, 'close_future': self.close_future}),
        ])

    @gen_test
    def test_send_invalid_json(self):
        ws = yield self.ws_connect('/ws/test')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message('Not a JSON string.')
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'Invalid JSON was sent.',
            }
        })

        yield ws.write_message(json_encode({'event': 'close'}))

    @gen_test
    def test_send_without_event(self):
        ws = yield self.ws_connect('/ws/test')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'json': 'I am a JSON'
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'There is no event in this JSON.',
            }
        })

    @skip('Write error on <socket.[...] object>: [Errno 9] Bad file descriptor')
    @gen_test
    def test_send_with_registered_event(self):
        ws = yield self.ws_connect('/ws/test')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'existing_event'
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'existing_event',
            'data': {
                'message': 'I am "existing_event" from "{}" websocket application.'.format(app_test_ws)
            }
        })

    @gen_test
    def test_send_with_not_registered_event(self):
        ws = yield self.ws_connect('/ws/test')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'not_registered_event'
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'The event "not_registered_event" does not exist for websocket "%s".' % app_test_ws,
            }
        })

    @gen_test
    def test_send_with_existing_event_and_invalid_data_format(self):
        ws = yield self.ws_connect('/ws/test')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'existing_event',
            'data': 'not a dictionary'
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'The data should be a dictionary.',
            }
        })


class WebSocketCounterAppTest(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()
        return Application([
            ('/ws/counter', TestWebSocketHandler, {'websocket': app_counter_ws, 'close_future': self.close_future}),
        ])

    @gen_test
    def test_emit_connection(self):
        ws = yield self.ws_connect('/ws/counter')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'connection'
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'connection',
            'data': {
                'message': 'Got new connection.',
                'counter_value': 0  # Initial value of counter
            }
        })

    @gen_test
    def test_emit_setup_without_counter_value(self):
        ws = yield self.ws_connect('/ws/counter')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'setup'
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'Setup initial counter value: FAIL.',
                'details': 'Can not get "value" from data.'
            }
        })

    @gen_test
    def test_emit_setup_with_bad_counter_value_type(self):
        ws = yield self.ws_connect('/ws/counter')

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'setup',
            'data': {
                'counter_value': 'not_an_integer'
            }
        }))
        time.sleep(SLEEPING_TIME)

        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'error',
            'data': {
                'message': 'Setup initial counter value: FAIL.',
                'details': '"value" is not an integer.'
            }
        })

    @gen_test(timeout=20)
    def test_emit_setup_with_good_value(self):
        counter_value = 50
        ws = yield self.ws_connect('/ws/counter')

        # Tests for first client

        self.assertEqual(app_counter.counter, 0)

        time.sleep(SLEEPING_TIME)
        yield ws.write_message(json_encode({
            'event': 'setup',
            'data': {
                'counter_value': counter_value
            }
        }))
        time.sleep(SLEEPING_TIME)

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

        time.sleep(SLEEPING_TIME)
        yield ws2.write_message(json_encode({'event': 'increment'}))
        time.sleep(SLEEPING_TIME)

        response = yield ws2.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'incremented_counter',
            'data': {
                'counter_value': counter_value  # 51
            }
        })

        self.assertEqual(app_counter.counter, counter_value)
