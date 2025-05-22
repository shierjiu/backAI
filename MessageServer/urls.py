# MessageServer/urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('webhook/list', MessageServerWebhookList.as_view(), name='MessageServerWebhookList'),
    path('webhook/info', MessageServerWebhookInfo.as_view(), name='MessageServerWebhookInfo'),
    path('webhook/server', MessageServerWebhookServer.as_view(), name='MessageServerWebhookServer'),
    path('template/list', MessageServerTemplateList.as_view(), name='MessageServerTemplateList'),
    path('template/info', MessageServerTemplateInfo.as_view(), name='MessageServerTemplateInfo'),
]
