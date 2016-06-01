Usage
=====

.. contents::
    :local:
    :backlinks: none

Run Tornado server
------------------

Django-tornado-websockets provides an easy solution to run your Tornado server. When you add ``tornado_websockets``
to your ``INSTALLED_APPS``, you obtain a new management command called ``runtornado``:

.. code-block:: bash

    $ python manage.py runtornado

Using WebSockets (server side)
------------------------------

It's preferable to write your WebSocket applications in your ``views.py`` file, or import these in ``views.py``.

Create a WebSocket application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You should use the :class:`~tornado_websockets.websocket.WebSocket` class to use... WebSockets 🤔.
It takes only one parameter and it's the ``path``. This path should be unique because it's automatically adding a new
handler to Tornado handlers (``your_path <=> your_websocket``):

.. code-block:: python

    from tornado_websockets.websocket import WebSocket

    # Make a new instance of WebSocket and automatically add handler '/ws/my_ws' to Tornado handlers
    my_ws = WebSocket('/my_ws')


.. note::
    If you are using this decorator on a class method (a wild ``self`` parameter appears!), you need to define a
    context for the WebSocket instance because ``@my_ws.on`` decorator can not know by itself what value ``self``
    should take (or maybe I am doing it wrong?):

    .. code-block:: python

        class MyClass(object):

            def __init__(self):
                my_ws.context = self

Receive an event from a client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To listen an incoming event, you should use the ``@my_ws.on`` decorator (where ``my_ws`` is an instance of
:class:`~tornado_websockets.websocket.WebSocket`) on a function or a class method.

Functions and class methods **should take two named parameters**:

- ``socket``: client who sent the event (instance of :class:`~tornado_websockets.websockethandler.WebSocketHandler`),
- ``data``: data sent by the client (dictionary).

**Usage example:**

.. code-block:: python

    # On a function
    @my_ws.on
    def my_event(socket, data):
        print('Catch "my_event" event from a client')
        print('But I know this client, it is the one using this websocket connection: %s' % socket)


    # On a class method
    class MyClass(object):

        def __init__(self):
            # Do not forget the context, otherwise the `self` value for all class methods decorated by `@my_ws.on`
            # decorator will be `None`
            my_ws.context = self

        @wy_ws.on
        def my_other_event(self, socket, data):
            # `self` value is a MyClass instance due to `my_ws.context = self` in `__init__()` method
            print('Catch "my_other_event" from a client')
            print('And same as before, I know that this client is using this websocket connection: %s' % socket)

.. _emit-an-event:

Send an event to a client
^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    You can only emit an event in a function or method decorated by ``@my_ws.on`` decorator.

There is three ways to emit an event:

1. For **all clients connected to your WebSocket application**, you should use ``my_ws.emit`` method,
2. For **the client who just sent an event**, you should use ``socket.emit`` method,
3. For **a specific client**, it's not officially implemented but you can take a look at ``my_ws.handlers``.
   It's a :class:`~tornado_websockets.websockethandler.WebSocketHandler` list and represents all clients connected to
   your application, so you can use ``my_ws.handlers[0].emit`` method.

**Usage example (echo server):**

.. code-block:: python

    from tornado_websockets.websocket import WebSocket

    ws_echo = WebSocket('/echo')

    @ws_echo.on
    def open(socket):
        # Notify all clients about a new connection
        ws_echo.emit('new_connection')

    @ws_echo.on
    def message(socket, data):
        # Reply to the client
        socket.emit('message', data)

        # Wow we got a spammer, let's inform the first client :^)
        if 'spam' in data.message:
            # wow
            ws_echo[0].emit('got_spam', {
                'message': data.get('message'),
                'socket': socket
            })

For more examples, you can read `testapp/views.py <https://github.com/Kocal/django-tornado-websockets/blob/develop/
testapp/views.py>`_ file.

Using WebSockets (client side)
------------------------------

Django-tornado-websockets uses its own wrapper for using JavaScript WebSocket in client-side: `django-tornado-websockets-client
<https://github.com/Kocal/django-tornado-websockets-client>`_. By using this wrapper, you will be able to write:

.. code-block:: javascript

    var ws = new TornadoWebSocket(...);

    ws.on('open', () => {
        ws.emit('my_event', { foo: 'bar' });
    });

    // instead of
    var ws = new WebSocket(...);

    ws.onopen = () => {
        ws.send({ event: 'my_event', data: { foo: 'bar' }});
    };

But you can simply ignore this wrapper and use `raw WebSocket <https://developer.mozilla.org/en/docs/WebSockets>`_
if you want. Just remember that data passed by Django-tornado-websockets are in JSON: ``{event: 'evt', data: {}}``.

----------------------------------------------------------------------------------------------------------------------

Linking JS wrapper into your Django template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Link ``django-tornado-websockets-client.js`` (symbolic link to `main.min.js <https://github.com/Kocal/
django-tornado-websockets-client/blob/master/dist/main.min.js>`_) file in your Django template:

.. code-block:: html+django

    {% load static %}
    <script src="{% static 'tornado_websockets/client.js' %}"></script>

Create a WebSocket connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is three ways to create a WebSocket connection:

.. code-block:: javascript

    var ws = new TornadoWebSocket(path, options);
    var ws = TornadoWebSocket(path, options); // shortcut to new TornadoWebSocket(path, options)
    var ws = tws(path, options);  // shortcut to new TornadoWebSocket(path, options)

.. js:class:: TornadoWebSocket(String path, Object options)

    Initialize a new WebSocket object with given options.

    **Parameters:**

    - ``path``: same value than ``path`` parameter from :class:`~tornado_websockets.websocket.WebSocket`, see
      `create websocket application <http://django-tornado-websockets.readthedocs.io/en/latest/usage.html#create-a
      -websocket-application>`_,
    - ``options.host``: host used for connection (default: ``'localhost'``, but soon ``window.location``)
    - ``options.port``: port used for connection (default: ``8000``)
    - ``options.secure``: ``true`` for using a secure connection (default: ``false``)

Receive an event from the server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can listen to WebSocket's events ``onopen``, ``onclose`` and ``onerror`` (``onmessage`` too but you will rewrite
a core part).
You can also listen to your own events like ``my_event``, ``user_joined``, etc...

.. js:function:: TornadoWebSocket.on(String event, Function callback)

    Bind a function to an event.

    **Parameters:**

    - ``event``: Event name
    - ``callback``: Function to execute when event ``event`` is received

.. code-block:: javascript

    // Bind to WebSocket.onopen
    ws.on('open', event => {
        console.log('Connection: OPEN', event);

        // Add an event/callback combination into TornadoWebSocket.events private object.
        // Will be called when we receive a JSON like that: {event: 'my_event', data: {...}}
        ws.on('my_event', data => {
            console.log('Got data from « my_event »', data);
        });
    });

    // Bind to WebSocket.onclose
    ws.on('close', event => {
        console.log('Connection: ERROR', event);
    });

    // Bind to WebSocket.onerror
    ws.on('error', event => {
        console.log('Connection: CLOSED', event);
    });

Send an event to the server
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. js:function:: TornadoWebSocket.emit(String event, Object|* data)

    Send a pair event/data to the server.

    **Parameters:**

    - ``event``: Event name
    - ``data``: Data to send, can be an ``Object``, not an ``Object`` (will be replaced by
      ``{ data: { message: data }}``, or ``undefined`` (will be replaced by ``{}``)

.. code-block:: javascript

    ws.on('open', event => {
        ws.emit('my_event'); // will send {}

        ws.emit('my_event', 'My message'); // will send {message: 'My message'}

        ws.emit('my_event', {my: 'data'}); // will send {my: 'data}
    });
