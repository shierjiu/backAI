# MessageServer/serializers.py
from rest_framework import serializers
from .models import *
class MessageServerTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageServerTemplate
        fields = '__all__'


class MessageServerWebhookSerializer(serializers.ModelSerializer):
    default_template = serializers.PrimaryKeyRelatedField(queryset=MessageServerTemplate.objects.all(), required=False, allow_null=True)
    class Meta:
        model = MessageServerWebhook
        fields = '__all__'

    def to_representation(self, instance):
        # 在序列化时，将 agent_model 字段嵌套为完整的 agent_model 对象
        representation = super().to_representation(instance)
        if instance.default_template:
            representation['default_template'] = MessageServerTemplateSerializer(instance.default_template).data
        return representation
