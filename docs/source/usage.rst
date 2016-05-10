Usage
=====

Run Tornado server
------------------

We provide an easy solution to run your Tornado server. When you add ``tornado_websockets`` to your
``INSTALLED_APPS``, you obtain a new management command called ``runtornado``:

.. code-block:: bash

    $ python manage.py runtornado

Using WebSockets (server side)
------------------------------

It's preferable to write your WebSocket applications in your ``views.py`` file.

Create a WebSocket
^^^^^^^^^^^^^^^^^^

You should use the :class:`~tornado_websockets.websocket.WebSocket` class to use... WebSockets 🤔.
It takes only one parameter and it's the ``url``. This url should be unique because it's automatically adding a new
handler (``your_url <=> your_websocket``) to Tornado handlers:

.. code-block:: python

    from tornado_websockets.websocket import WebSocket

    # Make a new instance of WebSocket and automatically add handler '/ws/my_ws' to Tornado handlers
    my_ws = WebSocket('/my_ws')

Listening to an event
^^^^^^^^^^^^^^^^^^^^^

To listen an incoming event, you should use the decorator ``@my_ws.on`` (where ``my_ws`` is an instance of
:class:`~tornado_websockets.websocket.WebSocket`) on a function or a class method.

Functions and class methods take two named parameters:

- ``socket``: client who sent the event (instance of :class:`~tornado_websockets.wrappers.WebSocketHandlerWrapper`),
- ``data``: data sent by the client (dictionary).

.. note::
    You should indicate a context for ``my_ws``, because the first parameter of a class method is ``self`` and the
    decorator ``@ws.on`` can not know by itself this ``self`` value. (Or maybe I'm doing it wrong?)

    .. code-block:: python

        class MyClass(object):

            def __init__(self):
                my_ws.context = self

.. code-block:: python

    # On a function
    @my_ws.on
    def my_event(socket, data):
        print('Catch "my_event" event from a client')
        print('But I know this client, it is the one using this websocket connection: %s' % socket)


    # On a class method
    class MyClass(object):

        counter = 0

        def __init__(self):
            # Do not forget the context, otherwise the `self` value for all class methods decorated by `@my_ws.on`
            # decorator will be `None`
            my_ws.context = self

        @wy_ws.on
        def my_other_event(self, socket, data):
            print('Catch "my_other_event" from a client')
            print('And same as before, I know that this client is using this websocket connection: %s' % socket)
            print('Data sent: %s' % str(data))
            print('Got "foo"?: %s' % data.get('foo'))

