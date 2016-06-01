from tornado_websockets.websocket import WebSocket


class ProgressBar(object):
    """
        Initialize a new ProgressBar module instance.

        If ``min`` and ``max`` values are equal, this progress bar has its indeterminate state
        set to ``True``.

        :param path: WebSocket path, see ``tornado_websockets.websocket.WebSocket``
        :param min: Minimum _value
        :param max: Maximum _value
        :type path: str
        :type min: int
        :type max: int
    """

    def __init__(self, path, min=0, max=100, add_to_handlers=True):

        if max < min:
            raise ValueError('`max` value (%d) can not be lower than `min` value (%d).' % (max, min))

        self.min = min
        self.max = max
        self._value = min
        self.indeterminate = min is max

        self.path = path.strip()
        self.path = self.path if self.path.startswith('/') else '/' + self.path
        self.websocket = WebSocket('/module/progress_bar' + self.path, add_to_handlers)
        self.bind_default_events()

    def reset(self):
        """
            Reset progress bar's progression to its minimum value.
        """
        self._value = self.min

    def tick(self, label=None):
        """
            Increments progress bar's _value by ``1`` and emit ``update`` event. Can also emit ``done`` event if
            progression is done.

            Call :meth:`~tornado_websockets.modules.progress_bar.ProgressBar.emit_update` method each time this
            method is called.
            Call :meth:`~tornado_websockets.modules.progress_bar.ProgressBar.emit_done` method if progression is
            done.

            :param label: A label which can be displayed on the client screen
            :type label: str
        """

        if not self.indeterminate and self._value < self.max:
            self._value += 1

        self.emit_update(label)

        if self.is_done():
            self.emit_done()

    def is_done(self):
        """
            Return ``True`` if progress bar's progression is done, otherwise ``False``.

            Returns ``False`` if progress bar is indeterminate, returns ``True`` if progress bar is
            determinate and current value is equals to ``max`` value.
            Returns ``False`` by default.

            :rtype: bool
        """

        if self.indeterminate:
            return False

        if self.value is self.max:
            return True

        return False

    def bind_default_events(self):
        """
            Bind default events for WebSocket instance.

            Actually, it only binds ``open`` event.
        """

        @self.websocket.on
        def open():
            self.emit_init()

    def on(self, callback):
        """
            Shortcut for :meth:`tornado_websockets.websocket.WebSocket.on` decorator.

            :param callback: Function or a class method.
            :type callback: Callable
            :return: ``callback`` parameter.
        """

        return self.websocket.on(callback)

    def emit_init(self):
        """
            Emit ``before_init``, ``init`` and ``after_init`` events to initialize a client-side progress bar.

            If progress bar is not indeterminate, ``min``, ``max`` and ``value`` values are sent with ``init`` event.
        """

        data = {'indeterminate': self.indeterminate}

        if not self.indeterminate:
            data.update({
                'min': int(self.min),
                'max': int(self.max),
                'value': int(self._value),
            })

        self.websocket.emit('before_init')
        self.websocket.emit('init', data)
        self.websocket.emit('after_init')

    def emit_update(self, label=None):
        """
            Emit ``before_update``, ``update`` and ``after_update`` events to update a client-side progress bar.

            :param label: A label which can be displayed on the client screen
            :type label: str
        """

        data = {}

        if not self.indeterminate:
            data.update({'value': int(self._value)})

        if label:
            data.update({'label': label})

        self.websocket.emit('before_update')
        self.websocket.emit('update', data)
        self.websocket.emit('after_update')

    def emit_done(self):
        """
            Emit ``done`` event when progress bar's progression :meth:`~tornado_websockets.modules.progress_bar.ProgressBar.is_done`.
        """

        self.websocket.emit('done')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not self.indeterminate and not self.min <= value <= self.max:
            raise ValueError('Value is not in [%d; %d] range.' % (self.min, self.max))

        self._value = value

    @property
    def context(self):
        return self.websocket.context

    @context.setter
    def context(self, value):
        self.websocket.context = value
