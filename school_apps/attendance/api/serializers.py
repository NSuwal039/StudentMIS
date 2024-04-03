from django.db.models import fields
from rest_framework import serializers
from student_management_app.api.serializers import StudentSerializer, StaffSerializer, ExtraUserSerializer, SubjectTeacherSerializer
from ..models import *
from django.contrib.auth.models import Permission
from student_management_app.models import (Student, Staff, ExtraUser)

class StudentAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    class Meta:
        model=StudentAttendance
        fields = '__all__'
    
    def get_student(self, obj):
        student=obj.student
        return (StudentSerializer(student).data)

class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    subjectteacher = serializers.SerializerMethodField()
    class Meta:
        model=TeacherAttendance
        fields = '__all__'
    
    def get_teacher(self, obj):
        teacher=obj.teacher
        return (StaffSerializer(teacher).data)
    
    def get_subjectteacher(self,obj):
        return SubjectTeacherSerializer(obj.subjectteacher).data
    
class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff = serializers.SerializerMethodField()

    class Meta:
        model=StaffAttendance
        fields = '__all__'
    
    def get_staff(self, obj):
        staff=obj.staff
        return (StaffSerializer(staff).data)
    