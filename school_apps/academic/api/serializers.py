from django.db.models import fields
from rest_framework import serializers
from ..models import *

class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Syllabus
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Assignment
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Grade
        fields = '__all__'

class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model=Routine
        fields = '__all__'