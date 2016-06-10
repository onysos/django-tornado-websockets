# Thanks to Ben Darnell for his file which show how to makes Tornado runs fine with Django and other WSGI Handler:
#   https://github.com/bdarnell/django-tornado-demo/blob/master/testsite/tornado_main.py
#
# I also made a more advanced file for a Django WSGIHandler, a Tornado WebSocketHandler, and a Tornado RequestHandler:
#   https://github.com/Kocal/django-test-websockets/blob/tornado-websocket/DjangoTestWebsockets/tornado_main.py

import django
import django.core.handlers.wsgi
import tornado.ioloop
import tornado.web
import tornado.wsgi
from django.apps import AppConfig
from django.conf import settings
from django.core.management import BaseCommand

from tornado_websockets.tornadowrapper import TornadoWrapper

if django.VERSION[1] > 5:
    django.setup()


class ReturnValueForTestMode(Exception):
    def __init__(self, value):
        self.value = value


class Command(BaseCommand, AppConfig):
    help = 'Run Tornado web server with Django and WebSockets support'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.django = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())

        self.default_port = 8000

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='?', help='Optional port number', type=int)
        parser.add_argument(
            '--test-mode',
            action='store_true',
            dest='test_mode',
            default=False,
            help='Enable test mode and do not run the Tornado server'
        )

        pass

    def handle(self, *args, **options):
        test_mode = options.get('test_mode')

        if test_mode:
            # self.stdout.write('== Running in test mode, Tornado server will not be started')
            pass

        # 1 - Read Tornado settings from Django settings file
        try:
            tornado_configuration = settings.TORNADO
        except AttributeError as e:
            tornado_configuration = {}

        if not tornado_configuration:
            tornado_configuration = {}

        if test_mode is 'configuration':
            raise ReturnValueForTestMode(tornado_configuration)

        # 2 - Get port for Tornado
        tornado_port = options.get('port')

        if not tornado_port:
            tornado_port = tornado_configuration.get('port')
        if not tornado_port:
            tornado_port = self.default_port

        if test_mode is 'port':
            raise ReturnValueForTestMode(tornado_port)

        # 4 - Set-up Tornado handlers
        tornado_handlers = tornado_configuration.get('handlers', [])

        if test_mode is 'handlers':
            raise ReturnValueForTestMode(tornado_handlers)

        # 5 - Set up Tornado settings
        tornado_settings = tornado_configuration.get('settings', {})

        if test_mode is 'settings':
            raise ReturnValueForTestMode(tornado_settings)

        # 6 - Run Tornado
        if not test_mode:
            TornadoWrapper.start_app(tornado_handlers, tornado_settings)
            TornadoWrapper.listen(tornado_port)
            TornadoWrapper.loop()
