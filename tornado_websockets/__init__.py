import django.core.handlers.wsgi
import tornado.wsgi

django_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
django_app = ('.*', tornado.web.FallbackHandler, dict(fallback=django_app))

static_app = (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'})
