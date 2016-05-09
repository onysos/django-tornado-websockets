from django.views.generic import TemplateView

from tornado_websockets.websocket import WebSocket

ws_chat = WebSocket('/my_chat')

print('WS_CHAT: %s' % ws_chat)


class MyChat(TemplateView):
    template_name = 'testapp/index.html'

    def __init__(self, **kwargs):
        super(MyChat, self).__init__(**kwargs)
        ws_chat.context = self

    @ws_chat.on
    def connection(self, data):
        ws_chat.emit('new_connection', '%s just joined the webchat' % data.get('username', '<Anonymous>'))

    # @ws_chat.on('message')
    @ws_chat.on
    def message(self, data):
        ws_chat.emit('new_message', {
            'username': data.get('username', '<Anonymous>'),
            'message': data.get('message', 'Empty message')
        })

    @ws_chat.on
    def close(self, data):
        pass
