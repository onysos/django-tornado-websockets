Django integration and configuration
====================================

Integration
-----------

In your ``settings.py`` file, you need to add ``tornado_websockets`` to your Django ``INSTALLED_APPS`` :

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'tornado_websockets',
    ]

Configuration
-------------

Since we use Tornado as a replacement of a WSGI server (Gunicorn, uWSGI, ...), you need to configure it a bit before
using ``django-tornado-websockets``.

Basic configuration
^^^^^^^^^^^^^^^^^^^

You can provide a Tornado configuration in your ``settings.py`` file like this:

.. code-block:: python

    # At the end of settings.py file

    TORNADO = {
        'port': 1337,    # 8000 by default
        'handlers': [],  # [] by default
        'settings': {},  # {} by default
    }

1. ``port`` is the port which Tornado main loop will listen for its ``HTTPServer``,
2. ``handlers`` is a list of tuples where you can make a link between a route and an handler,
3. ``settings`` is a dictionary used to customize various aspects of Tornado (autoreload, debug, ...).

Read more about Tornado ``handlers`` and ``settings`` in the Tornado documentation: `Application configuration <http://www.tornadoweb.org/en/stable/web.html#application-configuration>`_

Adding Django
^^^^^^^^^^^^^

To makes Django work with Tornado, you need to add a new handler to Tornado configuration.
Tornado can `runs WSGI apps <http://www.tornadoweb.org/en/stable/wsgi.html#running-wsgi-apps-on-tornado-servers>`_
(like Django) by using ``tornado.wsgi.WSGIContainer``, and we provide an already defined Django WSGI app that you can
easily use; Or you can make your own Django WSGI app using the `tornado_websockets/__init__.py <https://github.com/Kocal/django-tornado-websockets/blob/develop/tornado_websockets/__init__.py#L4>`_
file.

.. code-block:: python

    import tornado_websockets

    # ...

    TORNADO = {
        # ...
        'handlers': [
            # ...
            tornado_websockets.django_app,  # django_app is using a "wildcard" route, so it should be the last element
        ],
    }

Static files support
^^^^^^^^^^^^^^^^^^^^

If you need static files support during your development (so you are not running a configured nginx/Apache for static
files), you can add another handler to your configuration:

.. code-block:: python

    import tornado.web

    # ...

    # Django specific configuration about static files
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

    TORNADO = {
        # ...
        'handlers': [
            (r'%s(.*)' % STATIC_URL, tornado.web.StaticFileHandler, {'path': STATIC_ROOT}),
            # ...
        ]
    }

Additional settings
^^^^^^^^^^^^^^^^^^^

You can pass additional settings to Tornado with ``TORNADO['settings']`` dictionary.
For example, it can be useful to set ``True`` value ``debug`` key if you are still in a development phase:

.. code-block:: python

    TORNADO = {
        # ...
        'settings': {
            'debug': True,
        }
    }
