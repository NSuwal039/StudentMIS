from rest_framework import serializers
from .models import Department, Ticket, Form
from django.contrib.auth.models import User
from student_management_app.models import CustomUser

"""
Serializer for department model
Uses model serializer
All fields included
"""
class DepartmentSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many = True, queryset = CustomUser.objects.all())
    class Meta:
        model = Department
        fields = '__all__'


"""
Serializer for Form model
Uses model serializer
All fields included
"""
class FormSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset = Department.objects.all())
    class Meta:
        model = Form
        fields = '__all__'           


"""
Serializer for Ticket model
Uses model serializer
All fields included
"""
class TicketSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset = CustomUser.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset = Department.objects.all())
    form = serializers.PrimaryKeyRelatedField(queryset = Form.objects.all())
    class Meta:
        model = Ticket 
        fields = '__all__'

            