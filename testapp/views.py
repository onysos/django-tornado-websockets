import threading
import time

from django.views.generic import TemplateView

from tornado_websockets.modules.progress_bar import ProgressBar
from tornado_websockets.websocket import WebSocket

# WebSocket echo server
ws_echo = WebSocket('/echo')


@ws_echo.on
def message(socket, data):
    socket.emit('message', data)


# WebSocket chat server, using Django for template rendering
ws_chat = WebSocket('/my_chat')


class MyChat(TemplateView):
    """
        Proof of concept about a really simple web chat using websockets and supporting messages history
    """

    template_name = 'testapp/index.html'
    messages = []

    def __init__(self, **kwargs):
        super(MyChat, self).__init__(**kwargs)

        # Otherwise, 'self' parameter for method decorated by @ws_chat.on will not be defined
        ws_chat.context = self

    @ws_chat.on
    def connection(self, socket, data):
        """
            Called when the client send the event "connection".

            :param data: Data sent by a client
            :param socket: WebSocket of the current client
            :type data: dict
            :type socket: tornado_websockets.websockethandler.WebSocketHandler
            :return: None
        """

        [socket.emit('new_message', __) for __ in self.messages]
        ws_chat.emit('new_connection', '%s just joined the webchat.' % data.get('username', '<Anonymous>'))

    @ws_chat.on
    def message(self, socket, data):
        """
            Called when the client send a new message

            :param data: Data sent by a client
            :param socket: WebSocket of the current client
            :type data: dict
            :type socket: tornado_websockets.websockethandler.WebSocketHandler

            :return: None
        """

        message = {
            'username': data.get('username', '<Anonymous>'),
            'message': data.get('message', 'Empty message')
        }

        ws_chat.emit('new_message', message)
        self.messages.append(message)

    @ws_chat.on
    def clear_history(self, socket, data):
        """
            Called when a client wants to clear messages history.
            Used only for client-side JavaScript unit tests
        """

        self.messages = []


# WebSocket module progress bar
ws_pb = ProgressBar('/my_progress_bar', max=100)


class MyProgressBar(TemplateView):
    template_name = 'testapp/progress_bar.html'

    def __init__(self, **kwargs):
        super(MyProgressBar, self).__init__(**kwargs)
        ws_pb.context = self

    @ws_pb.on
    def go(self, socket):
        ws_pb.reset()
        self.start_thread()

    def start_thread(self):
        def my_function():
            for value in range(0, ws_pb.max):
                time.sleep(.1)
                ws_pb.tick(label="[%d/%d] Tâche %d terminée" % (ws_pb.value, ws_pb.max, value))

        threading.Thread(None, my_function, None).start()
