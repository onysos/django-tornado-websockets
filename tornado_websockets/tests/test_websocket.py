from unittest import TestCase

import tornado.escape
import tornado.web
import tornado.websocket
import websocket


def to_json(value):
    return tornado.escape.json_encode(value)


def from_json(value):
    return tornado.escape.json_decode(value)


class WebSocketTest(TestCase):
    def setUp(self):
        self.ws = websocket.create_connection('ws://127.0.0.1:8000/ws/test')

        with self.assertRaises(websocket.WebSocketBadStatusException) as ex:
            websocket.create_connection('ws://127.0.0.1:8000/ws/i/am/not/in/handlers')

        self.assertEqual(str(ex.exception), 'Handshake status 404')

    def test_connection(self):
        self.assertEqual(self.ws.getstatus(), 101)

    def test_emit_bad_json(self):
        self.ws.send('Not a valid JSON string')

        self.assertDictEqual(from_json(self.ws.recv()), {
            'event': 'error',
            'data': {
                'message': 'Invalid JSON was sent.'
            }
        })

    def test_emit_with_no_namespace(self):
        self.ws.send('{"event": "message", "data": {}}')

        self.assertDictEqual(from_json(self.ws.recv()), {
            'event': 'error',
            'data': {
                'message': 'There is no namespace in this JSON.'
            }
        })

    def test_emit_with_not_registered_namespace(self):
        self.ws.send('{"namespace": "/foobar", "event": "message", "data": {}}')

        self.assertDictEqual(from_json(self.ws.recv()), {
            'event': 'error',
            'data': {
                'message': 'The namespace "/foobar" does not exist.'
            }
        })

    def test_emit_with_no_event(self):
        self.ws.send('{"namespace": "/test", "data": {}}')

        self.assertDictEqual(from_json(self.ws.recv()), {
            'event': 'error',
            'data': {
                'message': 'There is no event in this JSON.'
            }
        })

    def test_emit_with_not_registered_event(self):
        self.ws.send('{"namespace": "/test", "event": "bad_event", "data": {}}')

        self.assertDictEqual(from_json(self.ws.recv()), {
            'event': 'error',
            'data': {
                'message': 'The event "bad_event" does not exist in the namespace "/test".'
            }
        })

    def test_emit_with_bad_data_format(self):
        self.ws.send('{"namespace": "/test", "event": "connection", "data": "not a dictionary"}')

        self.assertDictEqual(from_json(self.ws.recv()), {
            'event': 'error',
            'data': {
                'message': 'The data should be a dictionary (JavaScript object).'
            }
        })
