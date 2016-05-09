Django integration and configuration
====================================

Integration
-----------

In your ``settings.py`` file, you need to add ``tornado_websockets`` to your Django ``INSTALLED_APPS`` :

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'tornado_websockets
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


Run Tornado
-----------

by adding tornado_websockets installed_apps lqksnd management command


