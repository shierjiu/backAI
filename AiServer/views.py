from rest_framework.views import APIView
from django.http import StreamingHttpResponse
from .serializers import *
from Public.api import *
from .utils import *


class AiServerModelList(APIView):
    def post(self, request):
        return pagination_query(cls=AiServerModel, cls_serializer=AiServerModelSerializer,request=request)


class AiServerModelInfo(APIView):
    def get(self, request):
        return get_by_id(cls=AiServerModel, cls_serializer=AiServerModelSerializer,request=request)

    def post(self, request):
        return post_by_id(cls=AiServerModel, cls_serializer=AiServerModelSerializer,request=request)

    def delete(self, request):
        return delete_by_id(cls=AiServerModel,request=request)


class AiServerAgentList(APIView):
    def post(self, request):
        return pagination_query(cls=AiServerAgent, cls_serializer=AiServerAgentSerializer,request=request)


class AiServerAgentInfo(APIView):
    def get(self, request):
        return get_by_id(cls=AiServerAgent, cls_serializer=AiServerAgentSerializer,request=request)

    def post(self, request):
        return post_by_id(cls=AiServerAgent, cls_serializer=AiServerAgentSerializer,request=request)

    def delete(self, request):
        return delete_by_id(cls=AiServerAgent, request=request)


class AiServerAgentServer(APIView):
    def post(self, request):
        agent_id = request.data.get('agentId')
        user_content = request.data.get('userContent')

        data = AiServerAgent.objects.get(id=agent_id)
        agent_config = AiServerAgentSerializer(data).data
        res = AIAgentServer(agent_config=agent_config, user_content=user_content).agent_server()
        return api_response(status=200, message="查询成功", data=res)


class AiServerAgentServerStream(APIView):
    def post(self, request):
        agent_id = request.data.get('agentId')
        user_content = request.data.get('userContent')

        data = AiServerAgent.objects.get(id=agent_id)
        agent_config = AiServerAgentSerializer(data).data
        return StreamingHttpResponse(
            AIAgentServer(agent_config=agent_config, user_content=user_content).agent_server_stream(),
            content_type="text/event-stream"
        )



#  TODO CESHI
class AiServerAgentGroupList(APIView):
    """
    GET /ai_server/agent/groups
    返回所有去重后的 group 字符串列表
    """
    def get(self, request):
        # 先取出所有 group（可能会重复）
        all_groups = AiServerAgent.objects \
            .values_list('group', flat=True)

        # 用 dict.fromkeys 保持原始顺序去重
        unique_groups = list(dict.fromkeys(all_groups))

        return api_response(
            status=200,
            message="查询成功",
            data=unique_groups
        )

class AiServerAgentByGroup(APIView):
    """
    GET /ai_server/agent/by_group?group=<组名>
    根据 group 返回该组下的所有智能体
    """
    def get(self, request):
        group = request.query_params.get('group')
        if not group:
            return api_response(
                status=400,
                message="缺少 group 参数",
                data=[]
            )

        agents_qs = AiServerAgent.objects.filter(group=group)
        serializer = AiServerAgentSerializer(agents_qs, many=True)
        return api_response(
            status=200,
            message="查询成功",
            data=serializer.data
        )