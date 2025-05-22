# VariableQuery/urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('database/list', VariableQueryDatabaseList.as_view(), name='VariableQueryDatabaseList'),
    path('database/info', VariableQueryDatabaseInfo.as_view(), name='VariableQueryDatabaseInfo'),
    path('database/server', VariableQueryDatabaseServer.as_view(), name='VariableQueryDatabaseServer'),
]
