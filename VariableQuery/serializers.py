# VariableQuery/serializers.py
from rest_framework import serializers
from .models import *


class VariableQueryDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableQueryDatabase
        fields = '__all__'
