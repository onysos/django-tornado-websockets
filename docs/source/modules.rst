Modules
=======

Progress bar
------------

Provide an interface to easily handle a progress bar on both server and client sides.

.. automodule:: tornado_websockets.modules.progress_bar

    Example
    ^^^^^^^

    Server-side
    '''''''''''

    .. code-block:: python

        import time
        import threading
        from tornado_websockets.modules.progress_bar import ProgressBar

        ws_pb = ProgressBar('/my_progress_bar', min=0, max=100)

        # Client emitted ``start_progression`` event
        @ws_pb.on
        def start_progression():

            def my_func():
                for value in range(ws_pb.min, ws_pb.max):
                    time.sleep(.1)  # Emulate a slow task :^)
                    ws_pb.tick(label="[%d/%d] Task #%d is done" % (ws_pb.value, ws_pb.max, value))

            threading.Thread(None, my_func, None).start()

    Client-side
    '''''''''''

    .. code-block:: javascript

        // Soon

    Usage
    ^^^^^

    Construction
    '''''''''''''
    .. autoclass:: ProgressBar

    Methods
    '''''''

    .. automethod:: ProgressBar.reset
    .. automethod:: ProgressBar.tick
    .. automethod:: ProgressBar.is_done

    Events
    ''''''

    .. automethod:: ProgressBar.on
    .. automethod:: ProgressBar.emit_init
    .. automethod:: ProgressBar.emit_update
    .. automethod:: ProgressBar.emit_done
