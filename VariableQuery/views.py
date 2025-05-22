# VariableQuery/views.py
from rest_framework.views import APIView
from .serializers import *
from Public.api import *
from .utils import *
class VariableQueryDatabaseList(APIView):
    def post(self, request):
        return pagination_query(cls=VariableQueryDatabase, cls_serializer=VariableQueryDatabaseSerializer, request=request)

class VariableQueryDatabaseInfo(APIView):
    def get(self, request):
        return get_by_id(cls=VariableQueryDatabase, cls_serializer=VariableQueryDatabaseSerializer, request=request)

    def post(self, request):
        return post_by_id(cls=VariableQueryDatabase, cls_serializer=VariableQueryDatabaseSerializer, request=request)

    def delete(self, request):
        return delete_by_id(cls=VariableQueryDatabase, request=request)

class VariableQueryDatabaseServer(APIView):
    def post(self, request):
        try:
            variable = request.data.get('variable', None)
            if variable is None:
                return api_response(status=400, message='必填参数variable缺失')
            else:
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
                return api_response(status=200, message="操作成功", data=data)
        except Exception as e:
            return api_response(status=400, message=str(e))
