from ..models import UserLog, ReportLog
from rest_framework import serializers
from student_management_app.api.serializers import CustomUserSerializer


class UserLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model=UserLog
        fields = '__all__'
    
    def get_user(self,obj):
        return CustomUserSerializer(obj.user).data

class ReportLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model=ReportLog
        fields = '__all__'
    
    def get_user(self,obj):
        return CustomUserSerializer(obj.user).data