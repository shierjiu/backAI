# AiEvaluationy/serializers.py
from rest_framework import serializers
from AiEvaluationy.models import *
from AiServer.models import AiServerAgent


# 文件 Serializer
class AiEvaluationFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiEvaluationFile
        fields = '__all__'

# 数据集 Serializer
class AiEvaluationDatasetSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = AiEvaluationDataset
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态添加 children 字段
        self.fields['children'] = serializers.SerializerMethodField()

    def get_children(self, obj):
        # 递归调用序列化器来序列化子节点
        if hasattr(obj, 'children'):
            serializer = self.__class__(obj.children, many=True)
            return serializer.data
        return []

    def get_parent_id(self, obj):
        # 返回父级的 ID，如果没有父级则返回 None
        return obj.parent.id if obj.parent else None

# 数据集标签 Serializer
class AiEvaluationDatasetTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiEvaluationDatasetTag
        fields = '__all__'


# 评测对象 Serializer
class AiEvaluationEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AiEvaluationEntity
        fields = '__all__'


# 数据集明细 Serializer
class AiEvaluationDatasetEntrySerializer(serializers.ModelSerializer):
    # 写时传 id，读时展示嵌套
    dataset = serializers.PrimaryKeyRelatedField(queryset=AiEvaluationDataset.objects.all(),label="数据集ID")
    entity = serializers.PrimaryKeyRelatedField(queryset=AiEvaluationEntity.objects.all(),allow_null=True, required=False)
    tag = serializers.PrimaryKeyRelatedField(queryset=AiEvaluationDatasetTag.objects.all(),allow_null=True, required=False,label="标签ID")

    class Meta:
        model = AiEvaluationDatasetEntry
        fields = "__all__"
        extra_kwargs = {'entity': {'allow_null': True, 'required': False},'tag':    {'allow_null': True, 'required': False},}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # 嵌套 dataset
        ret['dataset'] = AiEvaluationDatasetSerializer(instance.dataset).data
        # 如果 entity 为空，直接返回 None，否则嵌套序列化
        if instance.entity is not None:
            ret['entity'] = AiEvaluationEntitySerializer(instance.entity).data
        else:
            ret['entity'] = None
        # 同理处理 tag
        if instance.tag is not None:
            ret['tag'] = AiEvaluationDatasetTagSerializer(instance.tag).data
        else:
            ret['tag'] = None
        return ret


# 历史记录 Serializer
class AiEvaluationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiEvaluationRecord
        fields = '__all__'

    # def to_representation(self, instance):
    #     # 先拿到原始的 dict
    #     ret = super().to_representation(instance)
    #
    #     # 1) dataset 字段（原来存的是 ID 字符串），转换成 dataset.name
    #     ds_id = ret.get('dataset')
    #     try:
    #         ds = AiEvaluationDataset.objects.get(pk=int(ds_id))
    #         ret['dataset'] = ds.name
    #     except Exception:
    #         # 如果查不到或者格式不对，就保持原值
    #         pass
    #
    #     # 2) agent 字段（原来存的是 "3,2" 这样的 ID 列表），转换成 [name1, name2]
    #     agent_ids = ret.get('agent')
    #     agent_names = []
    #     if agent_ids:
    #         for aid in agent_ids.split(','):
    #             try:
    #                 ag = AiServerAgent.objects.get(pk=int(aid))
    #                 agent_names.append(ag.name)
    #             except Exception:
    #                 continue
    #     ret['agent'] = agent_names
    #
    #     # 3) entity 字段（存的是单个 ID），转换成 entity.name
    #     ent_id = ret.get('entity')
    #     try:
    #         ent = AiEvaluationEntity.objects.get(pk=int(ent_id))
    #         ret['entity'] = ent.name
    #     except Exception:
    #         ret['entity'] = None
    #
    #     return ret
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        agent_str = ret.get('agent') or ""
        ret['agent'] = [name for name in agent_str.split(',') if name]
        # entity 本来就是名称，保持或设为 None
        ret['entity'] = ret.get('entity') or None

        return ret


# 历史记录明细 Serializer
class AiEvaluationRecordEntrySerializer(serializers.ModelSerializer):
    record = AiEvaluationRecordSerializer(read_only=True)  # Nested record serializer

    class Meta:
        model = AiEvaluationRecordEntry
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['record'] = AiEvaluationRecordSerializer(instance.record).data
        return representation


class AIChatSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    method = serializers.CharField(default="POST")
    url = serializers.URLField(required=True)
    headers = serializers.DictField(required=True)
    body = serializers.DictField(required=True)
    query = serializers.CharField(required=True)