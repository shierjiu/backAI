# AiServer/urls.py
from django.urls import path
from .views import *


urlpatterns = [
    path('model/list', AiServerModelList.as_view(), name='AiServerModelList'),
    path('model/info', AiServerModelInfo.as_view(), name='AiServerModelInfo'),
    path('agent/list', AiServerAgentList.as_view(), name='AiServerAgentList'),
    path('agent/info', AiServerAgentInfo.as_view(), name='AiServerAgentInfo'),
    path('agent/server', AiServerAgentServer.as_view(), name='AiServerAgentServer'),
    path('agent/server_stream', AiServerAgentServerStream.as_view(), name='AiServerAgentServerStream'),



    # TODO ceshi
    path('agent/groups', AiServerAgentGroupList.as_view(), name='AiServerAgentGroupList'),
    path('agent/by_group', AiServerAgentByGroup.as_view(), name='AiServerAgentByGroup'),
]