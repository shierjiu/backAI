# AiServer/models.py
from django.db import models
class AiServerModel(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name="模型名称", max_length=128)
    type = models.CharField(verbose_name='调用模式', max_length=128)
    key = models.CharField(verbose_name='api密钥', max_length=128)
    url = models.CharField(verbose_name='api地址', max_length=128)
    model = models.CharField(verbose_name='api模型', max_length=128)
    class Meta:
        db_table = 'ai_server_model'
        ordering = ('-id',)
    def __str__(self):
        return self.id
class AiServerAgent(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name="名称", max_length=128)
    code = models.CharField(verbose_name='key', max_length=128, unique=True)
    model = models.ForeignKey(AiServerModel, verbose_name='AI模型', on_delete=models.CASCADE, related_name='agent')
    temperature = models.DecimalField(verbose_name='温度值', max_digits=2, decimal_places=1, default=1.0)
    max_token = models.IntegerField(verbose_name='最大token', default=4096)
    system_content = models.TextField(verbose_name='提示词', null=True, blank=True)
    category = models.CharField(verbose_name="分类", max_length=128)
    group = models.CharField(verbose_name="组别", max_length=128, null=True, blank=True)
    class Meta:
        db_table = 'ai_server_agent'
        ordering = ('-id',)

    def __str__(self):
        return self.id