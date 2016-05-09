django-tornado-websockets
=========================

`//TODO: Write a real documentation`

Installation
------------

1. Clone this repo and run `pip install -e .`
2. Using pip `pip install this-package-is-not-already-on-pypi`

Configuration
-------------

Add ``tornado_websockets`` to your ``INSTALLED_APPS``

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

Running server
''''''''''''''

.. code-block:: bash

    $ python manage.py runtornado

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
    def my_function(data): # data is a dictionnary
        print('Catch "my_first_event" event')

    @ws_chat.on
    def my_second_event(data):
        print('Catch "my_second_event" event')


    class IndexView(TemplateView):
        template_name = 'my_app/my_template.html'

        # If you are using a websocket into a class, you should set the attribute 'ws.context = self', otherwise "self"
        # parameter value for class methods will be set to None
        def __init__(self, **kwargs):
            super(IndexView, self).__init__(**kwargs)

            # Do not forget this line for a class
            ws_chat.context = self

        @ws_chat.on
        def message(self, data):
            # "self" is now this instance of IndexView and not None
            print('Got message: %s' % data.get('message'))


To emit an event, you can simply use the method ``ws.emit`` that **should be** called by or inside a function/method
decorated by ``@ws.on``. Also, you **can not** directly write ``ws.emit(...)`` in ``your_class.__init__()`` method,
even if this method is decorated by ``@ws.on``:

.. code-block:: python

    # Prototype: ws_chat.emit(event_name: string, message: string OR data: dict)

    from tornado_websockets.websocket import WebSocket

    ws = WebSocket('/my_ws')

    ws.emit('event', 'My message') # Raise EmitHandlerException

    def emit_message(message):
        ws.emit('message', {
            'from': 'John',
            'message': message
        })

    class MyWebSocket(object):

        def __init__(self):
            ws.context = self

            # Raise EmitHandlerException because directly used in __init__()
            ws.emit('something', 'foo')

            # Raise EmitHandlerException, because called in __init__() and no @ws.on decorator on ws.first_emit() method
            ws.first_emit()

            # Works because @ws.on decorator on ws.second_emit() method
            ws.second_emit()

        def first_emit(self):
            # Raise EmitHandlerException because no decorator on the method
            ws.emit('first', 'first foo')
            emit_message('My message')

        @ws.on
        def second_emit(self):
            # Works because of decorator on the method
            ws.emit('second', 'second foo')
            emit_message('My message')

        def third_emit(self):
            ws.emit('third', 'third foo')

        @ws.on('event')
        def my_method(self, data):

            # Works because of @ws.on('event') decorator
            ws.emit('event', 'bar')
            self.my_other_method()

Client side
'''''''''''

You can use *raw implementation* of WebSocket in JavaScript, but please wait a bit, I will write a JavaScript wrapper
for WebSocket class:

.. code-block:: javascript

    var ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");
    ws.onopen = function() {}
    ws.onclose = function() {}
    ws.onmessage = function() {}
    ws.onerror = function() {}
