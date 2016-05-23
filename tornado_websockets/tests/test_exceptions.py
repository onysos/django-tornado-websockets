# coding: utf-8

import unittest

from tornado_websockets.exceptions import *


class TestExceptions(unittest.TestCase):
    def test_tornadowebsocketerror(self):
        with self.assertRaises(TornadoWebSocketsError) as e:
            raise TornadoWebSocketsError

        self.assertIsInstance(e.exception, Exception)

    def test_websocketeventalreadybinded(self):
        event = 'my_event'
        path = '/ws/my_path'

        with self.assertRaises(WebSocketEventAlreadyBinded) as e:
            raise WebSocketEventAlreadyBinded(event=event, path=path)

        self.assertIsInstance(e.exception, NameError)
        self.assertIsInstance(e.exception, TornadoWebSocketsError)
        self.assertIsInstance(e.exception, Exception)

        self.assertEqual(e.exception.event, event)
        self.assertEqual(e.exception.path, path)

        self.assertEqual(
            str(e.exception),
            'The event "%s" is already binded for "%s" path.' % (event, path)
        )

    def test_invalidinstanceerror(self):
        actual_instance = object()
        expected_instance_name = 'my_expected_instance_name'

        with self.assertRaises(InvalidInstanceError) as e:
            raise InvalidInstanceError(actual_instance=actual_instance, expected_instance_name=expected_instance_name)

        self.assertIsInstance(e.exception, TypeError)
        self.assertIsInstance(e.exception, TornadoWebSocketsError)
        self.assertIsInstance(e.exception, Exception)

        self.assertEqual(e.exception.actual_instance, actual_instance)
        self.assertEqual(e.exception.expected_instance_name, expected_instance_name)

        self.assertEqual(
            str(e.exception),
            'Expected instance of "%s", got "%s" instead.' % (expected_instance_name, actual_instance)
        )

    def test_emithandlererror(self):
        event = 'my_event'
        path = '/ws/my_path'

        with self.assertRaises(EmitHandlerError) as e:
            raise EmitHandlerError(event=event, path=path)

        self.assertIsInstance(e.exception, TornadoWebSocketsError)
        self.assertIsInstance(e.exception, Exception)

        self.assertEqual(e.exception.event, event)
        self.assertEqual(e.exception.path, path)

        self.assertEqual(
            str(e.exception),
            'Can not emit "%s" event in "%s" path, emit() should be used in a function or class method decorated by'
            ' @WebSocket.on decorator.' % (event, path)
        )

    def test_notcallableerror(self):
        thing = 'something'

        with self.assertRaises(NotCallableError) as e:
            raise NotCallableError(thing=thing)

        self.assertIsInstance(e.exception, TornadoWebSocketsError)
        self.assertIsInstance(e.exception, Exception)

        self.assertEqual(e.exception.thing, thing)

        self.assertEqual(
            str(e.exception),
            'Used @WebSocket.on decorator on a thing that is not callable, got: "%s".' % thing
        )
