import pprint

import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web

import tornado_websockets

pp = pprint.PrettyPrinter(indent=4)


class TornadoWrapper:
    tornado_app = None
    tornado_server = None
    tornado_handlers = None
    tornado_settings = None

    # Default values for user configuration
    tornado_port = 8000
    handlers = []

    @classmethod
    def start_app(cls, tornado_handlers, tornado_settings):
        # Not `tornado_handlers += cls.handlers` because wildcard handler should be the last
        # http://www.tornadoweb.org/en/stable/_modules/tornado/web.html#Application.add_handlers
        tornado_handlers = cls.handlers + tornado_handlers

        cls.tornado_app = tornado.web.Application(tornado_handlers, **tornado_settings)

    @classmethod
    def listen(cls, tornado_port):
        cls.tornado_port = tornado_port
        tornado_server = tornado.httpserver.HTTPServer(cls.tornado_app)
        tornado_server.listen(cls.tornado_port)

    @classmethod
    def loop(cls):
        print('== Using port %s' % cls.tornado_port)
        print('== Using handlers:')
        pp.pprint(cls.tornado_app.handlers)
        print('== Using settings:')
        pp.pprint(cls.tornado_app.settings)

        tornado.ioloop.IOLoop.instance().start()

    @classmethod
    def add_handlers(cls, handlers):
        if TornadoWrapper.tornado_app is not None:
            TornadoWrapper.tornado_app.add_handlers('.*', handlers)
            print('== Adding handlers to already running Tornado application. New handlers are:')
            pp.pprint(cls.tornado_app.handlers)
        else:
            print('== Prepare new handlers for Tornado application :')
            pp.pprint(handlers)
            cls.handlers = handlers + cls.handlers
