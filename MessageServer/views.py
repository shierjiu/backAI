# MessageServer/views.py
from rest_framework.views import APIView
from VariableQuery.models import VariableQueryDatabase
from VariableQuery.utils import sql_server
from .serializers import *
from Public.api import *
from .utils import *
from django.http import JsonResponse
from .models import *



class MessageServerTemplateList(APIView):
    def post(self, request):
        return pagination_query(cls=MessageServerTemplate, cls_serializer=MessageServerTemplateSerializer, request=request)

class MessageServerTemplateInfo(APIView):
    def get(self, request):
        return get_by_id(cls=MessageServerTemplate, cls_serializer=MessageServerTemplateSerializer, request=request)

    def post(self, request):
        return post_by_id(cls=MessageServerTemplate, cls_serializer=MessageServerTemplateSerializer, request=request)

    def delete(self, request):
        return delete_by_id(cls=MessageServerTemplate, request=request)

class MessageServerWebhookList(APIView):
    def post(self, request):
        return pagination_query(cls=MessageServerWebhook, cls_serializer=MessageServerWebhookSerializer, request=request)

class MessageServerWebhookInfo(APIView):
    def get(self, request):
        return get_by_id(cls=MessageServerWebhook, cls_serializer=MessageServerWebhookSerializer, request=request)

    def post(self, request):
        return post_by_id(cls=MessageServerWebhook, cls_serializer=MessageServerWebhookSerializer, request=request)

    def delete(self, request):
        return delete_by_id(cls=MessageServerWebhook, request=request)

class MessageServerWebhookServer(APIView):
    def post(self, request):

        def get_variable_value(variable):
            try:
                db_config = VariableQueryDatabase.objects.get(variable=variable)
                data = sql_server(
                    db_type=db_config.db_type,
                    db_host=db_config.db_host,
                    db_port=db_config.db_port,
                    db_name=db_config.db_name,
                    db_username=db_config.db_username,
                    db_password=db_config.db_password,
                    sql_query=db_config.sql_query
                )
                return data["data"]
            except Exception:
                return "None"

        try:
            webhook_id = request.data.get('webhook', None)
            template_id = request.data.get('template', None)
            if webhook_id is None:
                return api_response(status=400, message='必填参数webhook缺失')
            else:
                webhook = MessageServerWebhook.objects.get(id=webhook_id).url
                if template_id is None:
                    template = "没有配置消息模板，发送了默认消息"
                else:
                    replacer = MarkdownVariableReplacer(get_value=get_variable_value)
                    template = MessageServerTemplate.objects.get(id=template_id).content
                    template = replacer.replace(template)
                data = send_message(webhook, template)
                return api_response(status=200, message="webhook消息发送成功", data=data)
        except Exception as e:
            return api_response(status=400, message=str(e))




