from django.db.models import fields
from django.db.models.fields import Field
from school_apps.courses.models import *
from student_management_app.models import Subject
from student_management_app.api.serializers import StudentSerializer, SubjectSerializer
from rest_framework import serializers

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model=Term
        fields = '__all__'
    
    

class ExamsSerializer(serializers.ModelSerializer):
    term = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    class Meta:
        model=Exams
        fields = '__all__'
    
    def get_term(self,obj):
        return TermSerializer(obj.term).data
    
    def get_subject(self,obj):
        return SubjectSerializer(obj.subject_id).data

class application_formSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    term = serializers.SerializerMethodField()
    grades = serializers.SerializerMethodField()

    class Meta:
        model=application_form
        fields = '__all__'
    
    def get_student(self, obj):
        return StudentSerializer(obj.student).data
    
    def term(self, obj):
        return TermSerializer(obj.term).data
    
    def grades(self, obj):
        grades = studentgrades.objects.filter(application_id=obj)
        return studentgradesSerializer(grades, many=True).data

class studentgradesSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    exam = serializers.SerializerMethodField()
    class Meta:
        model=studentgrades
        fields = '__all__'

    def get_student(self, obj):
        student=obj.application_id.student
        return StudentSerializer(student).data
    
    def get_exam(self,obj):
        return ExamsSerializer(obj.exam_id).data
class term_rankingSerializer(serializers.ModelSerializer):
    class Meta:
        model=term_ranking
        fields = '__all__'

class selectedcoursesSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    class Meta:
        model=selectedcourses
        fields = '__all__'
    
    def get_student(self, obj):
        return StudentSerializer(obj.student_id).data
    
    def get_subject(self, obj):
        return SubjectSerializer(obj.subject_id).data



