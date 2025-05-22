# VariableQuery/models.py
from django.db import models
class VariableQueryDatabase(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    variable = models.CharField(verbose_name='变量名', max_length=128, unique=True)
    db_type = models.CharField(verbose_name='数据库类型', max_length=128)
    db_host = models.CharField(verbose_name='数据库地址', max_length=128)
    db_port = models.IntegerField(verbose_name='数据库端口')
    db_name = models.CharField(verbose_name='数据库名称', max_length=128)
    db_username = models.CharField(verbose_name='数据库用户', max_length=128)
    db_password = models.CharField(verbose_name='数据库密码', max_length=128)
    sql_query = models.CharField(verbose_name='sql语句', max_length=2000)
    describe = models.CharField(verbose_name='描述', max_length=128, null=True, blank=True)

    class Meta:
        db_table = 'variable_query_database'
        ordering = ['-id']

    def __str__(self):
        return self.id