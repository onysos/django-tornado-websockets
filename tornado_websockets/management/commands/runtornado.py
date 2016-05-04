# Thanks to Ben Darnell for his file which show how to makes Tornado runs fine with Django and other WSGI Handler:
#   https://github.com/bdarnell/django-tornado-demo/blob/master/testsite/tornado_main.py
#
# I also made a more advanced file for a Django WSGIHandler, a Tornado WebSocketHandler, and a Tornado RequestHandler:
#   https://github.com/Kocal/django-test-websockets/blob/tornado-websocket/DjangoTestWebsockets/tornado_main.py

import pprint

import django
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from django.conf import settings
from django.core.management import BaseCommand

if django.VERSION[1] > 5:
    django.setup()

pp = pprint.PrettyPrinter(indent=4)


class Command(BaseCommand):
    help = 'Run Tornado web server with Django and WebSockets support'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.django = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

        self.default_port = 8000

        self.default_handlers = [
            ('.*', tornado.web.FallbackHandler, dict(fallback=self.django))
        ]

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='?', help='Optional port number')
        pass

    def handle(self, *args, **options):

        # 1 - Read Tornado settings from Django settings file
        try:
            tornado_settings = settings.TORNADO
        except AttributeError:
            tornado_settings = {}
            self.stderr.write(
                "Can't read Tornado settings from your settings file, you should set settings.TORNADO.")

        # 2 - Get port for Tornado
        tornado_port = options.get('port')

        if not tornado_port:
            tornado_port = tornado_settings.get('port')
        if not tornado_port:
            tornado_port = self.default_port

        # 3 - Set-up handlers and settings for Tornado

        # Handlers
        tornado_handlers = tornado_settings.get('handlers', self.default_handlers)

        # Settings
        tornado_settings = tornado_settings.get('settings', {})

        # 4 - Run Tornado
        self.stdout.write('== Using port %d\n' % tornado_port)
        self.stdout.write('== Using handlers:\n')
        pp.pprint(tornado_handlers)
        self.stdout.write('== Using settings:\n')
        pp.pprint(tornado_settings)

        tornado_app = tornado.web.Application(tornado_handlers, **tornado_settings)
        server = tornado.httpserver.HTTPServer(tornado_app)
        server.listen(tornado_port)

        tornado.ioloop.IOLoop.instance().start()
