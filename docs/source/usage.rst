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

It's preferable to write your WebSocket applications in your ``views.py`` file.

Create a WebSocket
^^^^^^^^^^^^^^^^^^

You should use the :class:`~tornado_websockets.websocket.WebSocket` class to use... WebSockets 🤔.
It takes only one parameter and it's the ``url``. This url should be unique because it's automatically adding a new
handler to Tornado handlers (``your_url <=> your_websocket``):

.. code-block:: python

    from tornado_websockets.websocket import WebSocket

    # Make a new instance of WebSocket and automatically add handler '/ws/my_ws' to Tornado handlers
    my_ws = WebSocket('/my_ws')

Listening to an event
^^^^^^^^^^^^^^^^^^^^^

To listen an incoming event, you should use the ``@my_ws.on`` decorator (where ``my_ws`` is an instance of
:class:`~tornado_websockets.websocket.WebSocket`) on a function or a class method.

Functions and class methods **should take two named parameters**:

- ``socket``: client who sent the event (instance of :class:`~tornado_websockets.wrappers.WebSocketHandlerWrapper`),
- ``data``: data sent by the client (dictionary).

.. note::
    If you are using this decorator on a class method (a wild ``self`` parameter appears!), you need to define a
    context for the WebSocket instance because ``@my_ws.on`` decorator can not know by itself what value ``self``
    should take (or maybe I am doing it wrong?):

    .. code-block:: python

        class MyClass(object):

            def __init__(self):
                my_ws.context = self

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

Emit an event
^^^^^^^^^^^^^

.. warning::
    You can only emit an event in a function or method decorated by ``@my_ws.on`` decorator.

- If you want to emit an event for **all clients connected to your WebSocket application**, you should use ``my_ws.emit`` method,
- If you want to emit an event for **the client that sent the event**, you should use ``socket.emit`` method,
- If you want to emit an event for **a specific client**, it's not officially implemented but you can take a look at ``my_ws.handlers`` list. It contains all clients connected to your application, so you can use ``my_ws.handlers[0].emit`` method.

**Usage example:**

.. code-block:: python

    import time

    from tornado_websockets.websocket import WebSocket

    my_ws = WebSocket('/party')


    class MyParty(object):

        def __init__(self):
            my_ws.context = self

        @my_ws.on
        def connection(self, socket, data):
            user = data.get('user')  # 'Robert' for example

            # Inform all users that Robert joined the party
            my_ws.emit('user_joined', {
                'message': 'Hey guys, %s just joined the party!' % user,
                'timestamp': time.time()
            })

            # Said welcome to Robert
            socket.emit('welcome', 'Welcome to the party %s!' % user)
            # is equivalent to
            socket.emit('welcome', {'message': 'Welcome to the party %s!' % user})

            # For the organiser (let's say the first guy who joined the party is the organiser)
            my_ws.handlers[0].emit('receive_client', {'user': user})

Using WebSockets (client side)
------------------------------

.. todo:: Develop a JavaScript library/wrapper and write this section.
