from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^my_chat/$', views.MyChat.as_view(), name='index'),
    url(r'^my_progress_bar/$', views.MyProgressBar.as_view(), name='progress_bar'),
    url(r'^admin/', admin.site.urls)
]
