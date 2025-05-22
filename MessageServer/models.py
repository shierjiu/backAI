# MessageServer/models.py
from django.db import models
class MessageServerTemplate(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name='模板名称', max_length=128, unique=True)
    content = models.TextField(verbose_name='模板内容')

    class Meta:
        db_table = 'message_server_template'
        ordering = ['-id']

    def __str__(self):
        return self.id


class MessageServerWebhook(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=128, unique=True)
    url = models.CharField(verbose_name='地址', max_length=128)
    default_template = models.ForeignKey(MessageServerTemplate, verbose_name='默认模板', related_name="webhook", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'message_server_webhook'
        ordering = ['-id']

    def __str__(self):
        return self.id
