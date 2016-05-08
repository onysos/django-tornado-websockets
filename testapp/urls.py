from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^chat/', views.IndexView.as_view()),
    url(r'^admin/', admin.site.urls)
]
