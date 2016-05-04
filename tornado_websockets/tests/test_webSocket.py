from unittest import TestCase

import tornado.escape
import websocket


def toJson(value):
    return tornado.escape.json_encode(value)


def fromJson(value):
    return tornado.escape.json_decode(value)


class TestWebSocket(TestCase):
    stacktrace = False
    timeout = 1
    ws1 = None
    ws2 = None

    def setUp(self):
        websocket.enableTrace(self.stacktrace)

        self.ws1 = websocket.create_connection('ws://127.0.0.1:8000/ws/test/first', timeout=self.timeout)
        self.ws2 = websocket.create_connection('ws://127.0.0.1:8000/ws/test/second', timeout=self.timeout)

        with self.assertRaises(websocket.WebSocketBadStatusException) as ex:
            websocket.create_connection('ws://127.0.0.1:8000/ws/i/am/not/in/handlers', timeout=self.timeout)

        self.assertEqual(str(ex.exception), 'Handshake status 404')

    def test_connection(self):
        self.assertEqual(self.ws1.getstatus(), 101)
        self.assertEqual(self.ws2.getstatus(), 101)

    def test_on_connection(self):
        self.ws1.send(toJson({
            'event': 'connection',
        }))

        self.ws2.send(toJson({
            'event': 'connection',
        }))

        self.assertDictEqual(fromJson(self.ws1.recv()), {
            'event': 'connection',
            'data': {
                'message': 'New connection'
            }
        })

        self.assertDictEqual(fromJson(self.ws2.recv()), {
            'event': 'error',
            'data': {
                'message': 'Event "connection" is not implemented'
            }
        })

