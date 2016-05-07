from django.views.generic import TemplateView

from tornado_websockets.websocket import WebSocket

ws_chat = WebSocket('/chat')


@ws_chat.on('connection')
def my_func():
    ws_chat.emit('connection', 'Got a new connection')


@ws_chat.on
def close():
    ws_chat.emit('close', 'WebSocket is closed')


class IndexView(TemplateView):
    template_name = 'testapp/index_old.html'

    @ws_chat.on
    def message(self, data):
        ws_chat.emit('message', data.get('message', 'Default message'))
