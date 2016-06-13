# coding: utf-8

import pprint

import tornado
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from six import integer_types

pp = pprint.PrettyPrinter(indent=4)


class TornadoWrapper:
    """
        Wrapper for Tornado application and server handling.

        It let you access to Tornado app, handlers and settings everywhere in your code (it's really
        useful when you run ``runtornado`` management command and WebSockets management).
    """

    tornado_app = None
    tornado_server = None

    # Default values for user configuration
    tornado_port = 8000
    handlers = []

    @classmethod
    def start_app(cls, tornado_handlers=None, tornado_settings=None):
        """
            Initialize the Tornado web application with given handlers and settings.

            :param tornado_handlers: Handlers (routes) for Tornado
            :param tornado_settings: Settings for Tornado
            :type tornado_handlers: list
            :type tornado_settings: dict
            :return: None
        """

        if not tornado_handlers:
            tornado_handlers = []

        if not tornado_settings:
            tornado_settings = {}

        if not isinstance(tornado_handlers, list):
            raise TypeError('Expected a list for Tornado handlers.')

        if not isinstance(tornado_settings, dict):
            raise TypeError('Expected a dictionary for Tornado settings.')

        # Not `tornado_handlers += cls.handlers` because wildcard handler should be the last value in handlers list
        # http://www.tornadoweb.org/en/stable/_modules/tornado/web.html#Application.add_handlers
        tornado_handlers = cls.handlers + tornado_handlers

        cls.tornado_app = tornado.web.Application(tornado_handlers, **tornado_settings)

    @classmethod
    def listen(cls, tornado_port):
        """
            Start the Tornado HTTP server on given port.

            :param tornado_port: Port to listen
            :type tornado_port: int
            :return: None

            .. todo:: Add support for HTTPS server.
        """

        if not isinstance(tornado_port, integer_types):
            raise TypeError('Expected an integer for Tornado port.')

        if not cls.tornado_app:
            raise TypeError('Tornado application was not instantiated, call TornadoWrapper.start_app method.')

        cls.tornado_port = tornado_port
        cls.tornado_server = tornado.httpserver.HTTPServer(cls.tornado_app)
        cls.tornado_server.listen(cls.tornado_port)

    @classmethod
    def loop(cls):
        """
            Run Tornado main loop and display configuration about Tornado handlers and settings.

            :return: None
        """
        # print('== Using port %s' % cls.tornado_port)
        # print('== Using handlers:')
        # pp.pprint(cls.tornado_app.handlers)
        # print('== Using settings:')
        # pp.pprint(cls.tornado_app.settings)

        tornado.ioloop.IOLoop.instance().start()

    @classmethod
    def add_handlers(cls, handlers):
        """
            Add an handler to Tornado app if it's defined, otherwise it add this handler to the
            TornadoWrapper.tornado_handlers list.

            :param handlers: Handler(s) to add
            :type handlers: list|tuple
            :return: Tornado application handlers
            :rtype: list
        """

        if isinstance(handlers, tuple):
            handlers = [handlers]
        elif not isinstance(handlers, list):
            raise TypeError('Expected a list or a tuple for handlers.')

        if not TornadoWrapper.tornado_app:
            # print('== Prepare new handlers for Tornado application:')
            # pp.pprint(handlers)

            # ``cls.handlers = handlers + cls.handlers`` and not ``cls.handlers += handlers``,
            # see `TornadoWrapper.start_app` source to know why.
            cls.handlers = handlers + cls.handlers

            return cls.handlers

        # print('== Adding handlers to already running Tornado application. New handlers are:')
        # pp.pprint(cls.tornado_app.handlers)
        TornadoWrapper.tornado_app.add_handlers('.*', handlers)

        return cls.tornado_app.handlers
