# coding: utf-8

import pprint
import unittest

import re
import tornado.httpserver
import tornado.web

from tornado_websockets.tornadowrapper import TornadoWrapper

pp = pprint.PrettyPrinter(indent=4)


class TestTornadoWrapper(unittest.TestCase):
    def test_tornado_reset(self):
        TornadoWrapper.reset()
        self.assertIsNone(TornadoWrapper.tornado_app)
        self.assertIsNone(TornadoWrapper.tornado_server)
        self.assertListEqual(TornadoWrapper.handlers, [])
        self.assertEqual(TornadoWrapper.tornado_port, 8000)

    def test_tornado_start_app_with_invalid_parameter_handlers(self):
        with self.assertRaises(TypeError) as e:
            TornadoWrapper.start_app('not a list', {})

        self.assertEqual(str(e.exception), 'Expected a list for Tornado handlers.')

    def test_tornado_start_app_with_invalid_parameter_settings(self):
        with self.assertRaises(TypeError) as e:
            TornadoWrapper.start_app([], 'not a dictionary')

        self.assertEqual(str(e.exception), 'Expected a dictionary for Tornado settings.')

    def test_tornado_start_app(self):
        TornadoWrapper.start_app([], {})

        self.assertIsNotNone(TornadoWrapper.tornado_app)
        self.assertIsInstance(TornadoWrapper.tornado_app, tornado.web.Application)

    def test_tornado_listen_with_invalid_parameter_port(self):
        TornadoWrapper.reset()

        with self.assertRaises(TypeError) as e:
            TornadoWrapper.listen('not an integer')

        self.assertEqual(str(e.exception), 'Expected an integer for Tornado port.')
        self.assertIsNone(TornadoWrapper.tornado_server)

        with self.assertRaises(TypeError) as e:
            TornadoWrapper.listen(8000)

        self.assertEqual(
            str(e.exception),
            'Tornado application was not instantiated, call TornadoWrapper.start_app method.'
        )
        self.assertIsNone(TornadoWrapper.tornado_server)

    def test_tornado_listen(self):
        TornadoWrapper.start_app()
        TornadoWrapper.listen(12345)

        self.assertEqual(TornadoWrapper.tornado_port, 12345)
        self.assertIsNotNone(TornadoWrapper.tornado_server)
        self.assertIsInstance(TornadoWrapper.tornado_server, tornado.httpserver.HTTPServer)

    def test_tornado_loop(self):
        TornadoWrapper.start_app()
        TornadoWrapper.listen(8000)
        TornadoWrapper.loop()
        TornadoWrapper.reset()

    def test_tornado_add_handlers_with_invalid_parameter_handlers(self):
        with self.assertRaises(TypeError) as e:
            TornadoWrapper.add_handlers('not a list or tuple')

        self.assertEqual(str(e.exception), 'Expected a list or a tuple for handlers.')

    def test_tornado_add_handler_when_tornadoapp_is_not_running(self):
        class MyHandler(tornado.web.RequestHandler):
            pass

        TornadoWrapper.reset()
        TornadoWrapper.add_handlers(
            ('.*', MyHandler)
        )

        self.assertEqual(TornadoWrapper.handlers[0][0], '.*')
        self.assertEqual(str(TornadoWrapper.handlers[0][1]), str(MyHandler))  # do not works without str() (???)

    def test_tornado_add_handlers_when_tornadoapp_is_not_running(self):
        class MyFirstHandler(tornado.web.RequestHandler):
            pass

        class MySecondHandler(tornado.web.RequestHandler):
            pass

        TornadoWrapper.reset()
        TornadoWrapper.add_handlers([
            ('/handler/first', MyFirstHandler),
            ('/handler/second', MySecondHandler)
        ])

        self.assertEqual(TornadoWrapper.handlers[0][0], '/handler/first')
        self.assertEqual(str(TornadoWrapper.handlers[0][1]), str(MyFirstHandler))

        self.assertEqual(TornadoWrapper.handlers[1][0], '/handler/second')
        self.assertEqual(str(TornadoWrapper.handlers[1][1]), str(MySecondHandler))

    def test_tornado_add_handler_when_tornadoapp_is_running(self):
        class MyHandler(tornado.web.RequestHandler):
            pass

        TornadoWrapper.reset()
        TornadoWrapper.start_app()
        TornadoWrapper.listen(11111)
        TornadoWrapper.loop()

        self.assertIsNotNone(TornadoWrapper.tornado_app)

        TornadoWrapper.add_handlers(
            ('.*', MyHandler)
        )

        handlers = TornadoWrapper.tornado_app.handlers[0][1]  # list of URLSpec

        self.assertEqual(handlers[0].regex, re.compile('.*$'))
        self.assertEqual(handlers[0].handler_class, MyHandler)  # do not works without str() (???)

    def test_tornado_add_handlers_when_tornadoapp_is_running(self):
        class MyFirstHandler(tornado.web.RequestHandler):
            pass

        class MySecondHandler(tornado.web.RequestHandler):
            pass

        TornadoWrapper.reset()
        TornadoWrapper.start_app()
        TornadoWrapper.listen(22222)
        TornadoWrapper.loop()

        self.assertIsNotNone(TornadoWrapper.tornado_app)

        TornadoWrapper.add_handlers([
            ('/handler/first', MyFirstHandler),
            ('/handler/second', MySecondHandler)
        ])

        handlers = TornadoWrapper.tornado_app.handlers[0][1]  # list of URLSpec

        self.assertEqual(handlers[0].regex, re.compile('/handler/first$'))
        self.assertEqual(handlers[0].handler_class, MyFirstHandler)

        self.assertEqual(handlers[1].regex, re.compile('/handler/second$'))
        self.assertEqual(handlers[1].handler_class, MySecondHandler)
