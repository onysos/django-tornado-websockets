#!/usr/bin/env python

# Thanks to Ben Darnell for his file which show how to makes Tornado runs fine with Django and other WSGI Handler:
#   https://github.com/bdarnell/django-tornado-demo/blob/master/testsite/tornado_main.py
#
# I also made a more advanced file for a Django WSGIHandler, a Tornado WebSocketHandler, and a Tornado RequestHandler:
#   https://github.com/Kocal/django-test-websockets/blob/tornado-websocket/DjangoTestWebsockets/tornado_main.py

import django
import django.core.handlers.wsgi
import tornado.wsgi
from django.conf import settings
from django.core.management import BaseCommand

if django.VERSION[1] > 5:
    django.setup()

class Command(BaseCommand):
    help = 'Run Tornado web server with Django and WebSockets support'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.default_port = 8000

        self.default_handlers = {
            '.*': tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
        }

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='?', help='Optional port number')
        pass

    def handle(self, *args, **options):
        print(settings)
        print(options)
        print(self)

        # 1: Read Tornado settings from Django settings file
        try:
            tornado_settings = settings.TORNADO
        except AttributeError:
            tornado_settings = {}
            self.stderr.write("Can't read Tornado settings from your settings file, you should set settings.TORNADO.")

        # 2: Get running port for Tornado
        port = options.get('port')

        if not port:
            port = tornado_settings.get('port')
        if not port:
            port = self.default_port

        # 3: Set-up for Tornado

        # Prepare Tornado
        self.default_handlers.update(tornado_settings.get('handlers', {}))
        handlers = self.default_handlers

        # 123: Run Tornado
        self.stdout.write('Using port %d\n' % port)
        self.stdout.write('Using handlers: %s\n' % handlers)