django-tornado-websockets
=========================

`//TODO: Write a real documentation`

Installation
------------

1. Clone this repo and run `pip install -e .`
2. Using pip `pip install this-package-is-not-already-on-pypi`

Configuration
-------------

At the end of your file `my_project/settings.py`, you can define a Tornado configuration where you will
be able to define the running port, handlers and settings for Tornado application:

.. code-block:: python

    # Simplest configuration
    TORNADO = {
        'port': 8080, # 8000 by default
        'handlers': [],
        'settings': {},
    }

To works with Django, module *tornado_websockets* provide an already working Django app, defined in
`this file <tornado_websockets/__init__.py>`_.

.. code-block:: python

    import tornado_websockets

    TORNADO = {
        # ...
        'handlers': [
            # ...
            tornado_websockets.django_app
        ]
    }

If you need static files support during your development, you can add another handler to your configuration:

.. code-block:: python

    # Django specific configuration
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

    TORNADO = {
        # ...
        'handlers': [
            (r'%s(.*)' % STATIC_URL, tornado.web.StaticFileHandler, {'path': STATIC_ROOT}),
            # ...
        ]
    }

To set Tornado settings, you need to read the official documentation about `Tornado application settings
<http://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings>`_ and define your settings like that:

.. code-block:: python

    TORNADO = {
        # ...
        'settings': {
            'debug': True
        }
    }

Quick start
-----------

Server side
'''''''''''

The WebSocket usage should be in your `my_app/views.py` file:

.. code-block:: python

    from tornado_websockets.websocket import WebSocket

    # Make a new instance of WebSocket and automatically add handler '/ws/chat' to Tornado handlers
    ws_chat = WebSocket('/chat')


To listen for an event you should use the decorator ``@ws.on``. It works for function and methods (and soon for
a whole class):

.. code-block:: python

    # Prototype: @ws.on(event_name) or @ws.on

    @ws_chat.on('my_first_event')
    def my_function():
        print('Catch "my_first_event" event')

    @ws_chat.on
    def my_second_event():
        print('Catch "my_second_event" event')


    class IndexView(TemplateView):
        template_name = 'my_app/my_template.html'

        @ws_chat.on
        def message(self, data):
            print('Got message: %s' % data.get('message'))


To emit an event, you can simple use the method ``ws.emit``:

.. code-block:: python

    # Prototype: ws_chat.emit(event_name: string, message: string OR data: dict)

    ws.emit('user_joined', 'An user joined the conversation')
    # is equivalent too
    ws.emit('user_joined', {'message': 'An user joined the conversation'})

    ws.emit('new_message', {
        'from': 'John',
        'message': '...'
    })

Client side
'''''''''''

You can use *raw implementation* of WebSocket in JavaScript, but a JavaScript wrapper is in preparation:

.. code-block:: javascript

    var ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");
    ws.onopen = function() {}
    ws.onclose = function() {}
    ws.onmessage = function() {}
    ws.onerror = function() {}
