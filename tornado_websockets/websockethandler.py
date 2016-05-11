# coding: utf-8

import inspect

import tornado
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

import tornado_websockets.websocket
from tornado_websockets.exceptions import *


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
        Represents a WebSocket connection, wrapper of `tornado.websocket.WebSocketHandler <http://www.tornadoweb.org/en/stable/websocket.html#event-handlers>`_ class.

        This class should not be instantiated directly; use the :class:`~tornado_websockets.websocket.WebSocket` class
        instead.
    """

    def initialize(self, websocket):
        """
            Called when class initialization, makes a link between a :class:`~tornado_websockets.websocket.WebSocket`
            instance and this object.

            :param websocket: instance of WebSocket.
            :type websocket: WebSocket
        """

        if not isinstance(websocket, tornado_websockets.websocket.WebSocket):
            raise InvalidInstanceError(websocket, 'tornado_websockets.websocket.WebSocket')

        # Make a link between a WebSocket instance and this object
        self.websocket = websocket
        websocket.handlers.append(self)

    def on_message(self, message):
        """
            Handle incoming messages on the WebSocket.

            :param message: JSON string
            :type message: str
        """

        try:
            message = tornado.escape.json_decode(message)
            namespace = message.get('namespace')
            event = message.get('event')
            data = message.get('data')
        except ValueError:
            self.emit_error('Invalid JSON was sent.')
            return

        if not event:
            self.emit_error('There is no event in this JSON.')
            return
        elif self.websocket.events.get(event) is None:
            self.emit_error('The event "%s" does not exist for websocket "%s"' % (event, self.websocket))
            return

        if not data:
            data = {}
        elif data and not isinstance(data, dict):
            self.emit_error('The data should be a dictionary (JavaScript object).')
            return

        # print('NAMESPACE: %s' % namespace)
        # print('EVENT: %s' % event)
        # print('DATA: %s' % data)

        callback = self.websocket.events.get(event)
        spec = inspect.getargspec(callback)
        kwargs = {}

        # print('SPEC: %s' % str(spec))

        if 'self' in spec.args:
            kwargs['self'] = self.websocket.context
        if 'socket' in spec.args:
            kwargs['socket'] = self
        if 'data' in spec.args:
            kwargs['data'] = data

        # print('CALLBACK: %s' % callback)
        # print('KWARGS: %s' % kwargs)

        print('-- Triggering "%s" event from "%s" namespace' % (event, namespace))

        return callback(**kwargs)

    def on_close(self):
        """
            Called when the WebSocket is closed, delete the link between this object and its WebSocket.
        """

        self.websocket.handlers.remove(self)

    def emit(self, event, data):
        """
            Sends a given event/data combinaison to the client of this WebSocket.

            Wrapper for `tornado.websocket.WebSocketHandler.write_message <http://www.tornadoweb.org/en/stable/
            websocket.html#tornado.websocket.WebSocketHandler.write_message>`_ method.

            :param event: event name to emit
            :param data: associated data
            :type event: str
            :type data: dict
        """

        self.write_message({
            'event': event,
            'data': data
        })

    def emit_error(self, message):
        """
            Shortuct to emit an error.

            :param message: error message
            :type message: str
        """

        print('-- Error: %s' % message)
        return self.emit('error', {'message': message})
