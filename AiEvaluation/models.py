# AiEvaluationy/models.py
"""七张表"""
import json

from django.db import models
from django.utils import timezone

"""文件"""
class AiEvaluationFile(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name='文件名称', max_length=249)
    file = models.CharField(verbose_name='文件', max_length=248, unique=True)

    class Meta:
        db_table = 'ai_evaluation_file'
        ordering = ('-id',)
    def __str__(self):
        return self.name

"""数据集"""
class AiEvaluationDataset(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(max_length=240)
    parent = models.ForeignKey("self", verbose_name='父节点', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    file = models.ForeignKey('AiEvaluationFile', verbose_name='附件', on_delete=models.CASCADE, related_name='database', null=True, blank=True)

    class Meta:
        db_table = 'ai_evaluation_dataset'
        ordering = ('-id',)

"""数据集标签"""
class AiEvaluationDatasetTag(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=240, unique=True)

    class Meta:
        db_table = 'ai_valuation_dataset_tag'
        ordering = ('-id',)

    def __str__(self):
        return self.id


"""评测对象"""
class AiEvaluationEntity(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.TextField(verbose_name='名称')
    url = models.TextField(verbose_name='请求地址')
    method = models.TextField(verbose_name='方法')
    header = models.TextField(verbose_name='请求头')
    body = models.TextField(verbose_name='请求体')
    stream = models.BooleanField(verbose_name='流式输出', default=True)
    response_function = models.TextField(verbose_name='返回函数')

    class Meta:
        db_table = 'ai_evaluation_entity'
        ordering = ('-id',)

    def __str__(self):
        return str(self.id)
    def get_request_config(self) -> dict:
        """反序列化后直接可用于 GenericAIService"""
        try:
            headers = json.loads(self.header) if self.header else {}
        except json.JSONDecodeError:
            headers = {}
        try:
            body = json.loads(self.body) if self.body else {}
        except json.JSONDecodeError:
            body = {}

        return {
            "name":     self.name.lower(),
            "url":      self.url,
            "method":   (self.method or "POST").upper(),
            "headers":  headers,
            "body":     body,
            "stream":   self.stream,
            "timeout":  None,               # 由调用方注入
            "response_function": self.response_function or "",
        }




"""数据集明细"""

class AiEvaluationDatasetEntry(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    question = models.TextField(verbose_name='标准问题', max_length=2000)
    ground_truth = models.TextField(verbose_name='标准答案', max_length=1000)
    contexts = models.TextField(verbose_name='上下文', null=True, blank=True)
    answer = models.TextField(verbose_name='测评答案', max_length=2400,null=True, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间',  editable=False,null=True, blank=True)
    entity = models.ForeignKey(AiEvaluationEntity, verbose_name='测评对象', on_delete=models.CASCADE,related_name='object',null=True, blank=True)
    tag = models.ForeignKey(AiEvaluationDatasetTag, verbose_name='问题标签', on_delete=models.CASCADE,related_name='tag',null=True, blank=True)
    dataset = models.ForeignKey(AiEvaluationDataset, verbose_name='数据集', on_delete=models.CASCADE,related_name='dataset')
    status = models.CharField(verbose_name='状态',max_length=20,choices=(('pending', '待处理'),('false', '失败'),('completed', '已完成'),),default='pending',)

    class Meta:
        db_table = 'ai_evaluation_dataset_entry'
        ordering = ('-id',)

    def save(self, *args, **kwargs):
        """
        仅当 answer 字段由“空/None”变为非空时，刷新 update_time。
        其它字段的增删改均不会触发时间更新。
        （DatasetEvaluateView ）
        """
        if self.pk:  # 已存在 → 对比旧值
            old = AiEvaluationDatasetEntry.objects.filter(pk=self.pk) \
                .values('answer') \
                .first()
            if old and not old['answer'] and self.answer:
                self.update_time = timezone.now().replace(microsecond=0)
        else:  # 新建时不自动写更新时间
            # 保证导入 Excel 时可手动写入 update_time
            if self.update_time is None:
                self.update_time = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.id


"""历史记录"""
class AiEvaluationRecord(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)

    name = models.CharField(verbose_name='名称', max_length=128)
    dataset = models.CharField(verbose_name='数据集', max_length=1280)
    agent = models.CharField(verbose_name='智能体', max_length=1280)
    entity = models.CharField(verbose_name='测评对象', max_length=1280, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True, blank=True)
    STATUS_CHOICES = (('running', '运行中'), ('failed', '处理失败'), ('completed', '完成'),)
    status = models.CharField(verbose_name='状态', max_length=20, choices=STATUS_CHOICES, default='running', null=True,blank=True)
    score = models.FloatField(verbose_name='综合评分', null=True, blank=True)

    class Meta:
        db_table = 'ai_evaluation_record'
        ordering = ('-id',)

    def __str__(self):
        return self.id

    # id = models.AutoField(verbose_name='ID', primary_key=True)
    # name=models.CharField(verbose_name='名称', max_length=128)
    # dataset = models.CharField(verbose_name='数据集', max_length=1280)
    # agent = models.CharField(verbose_name='智能体', max_length=1280)
    # entity = models.CharField(verbose_name='测评对象', max_length=1280, null=True, blank=True)
    # create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True,null=True, blank=True)
    #
    # class Meta:
    #     db_table = 'ai_evaluation_record'
    #     ordering = ('-id',)
    #
    # def __str__(self):
    #     return self.id


"""历史明细"""
class AiEvaluationRecordEntry(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    result = models.TextField(verbose_name='结果', default='')
    record = models.ForeignKey(AiEvaluationRecord, verbose_name='历史记录', on_delete=models.CASCADE,related_name='record')

    class Meta:
        db_table = 'ai_evaluation_record_entry'
        ordering = ('-id',)

    def __str__(self):
        return self.id
