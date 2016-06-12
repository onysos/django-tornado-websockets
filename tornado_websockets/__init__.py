__version_info__ = ('0', '1', '1')
__version__ = '.'.join(__version_info__)

import django.core.handlers.wsgi
import tornado.wsgi

django_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
django_app = ('.*', tornado.web.FallbackHandler, dict(fallback=django_app))
