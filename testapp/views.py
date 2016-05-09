from django.views.generic import TemplateView

from tornado_websockets.websocket import WebSocket

ws_chat = WebSocket('/my_chat')


class MyChat(TemplateView):
    """
        Proof of concept about a really simple web chat using websockets
    """

    template_name = 'testapp/index.html'

    def __init__(self, **kwargs):
        super(MyChat, self).__init__(**kwargs)

        ws_chat.context = self  # Otherwise, 'self' parameter for method decorated by @ws_chat.on will not be defined

    @ws_chat.on
    def connection(self, data):
        """
            Called when the client send the event "connection".

            :param data: Data sent by the client
            :type data: dict
            :return: None
        """
        ws_chat.emit('new_connection', '%s just joined the webchat' % data.get('username', '<Anonymous>'))

    @ws_chat.on
    def message(self, data):
        """
            Called when the client send a new message

            :param data: Data sent by the client
            :type data: dict
            :return: None
        """

        ws_chat.emit('new_message', {
            'username': data.get('username', '<Anonymous>'),
            'message': data.get('message', 'Empty message')
        })
