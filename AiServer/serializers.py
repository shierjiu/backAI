# AiServer/serializers.py
from rest_framework import serializers
from .models import *


class AiServerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiServerModel
        fields = '__all__'


class AiServerAgentSerializer(serializers.ModelSerializer):
    model = serializers.PrimaryKeyRelatedField(queryset=AiServerModel.objects.all())

    class Meta:
        model = AiServerAgent
        fields = '__all__'

    def to_representation(self, instance):
        # 在序列化时，将 agent_model 字段嵌套为完整的 agent_model 对象
        representation = super().to_representation(instance)
        representation['model'] = AiServerModelSerializer(instance.model).data
        return representation
