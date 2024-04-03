from student_management_app.models import *
from student_management_app.api.serializers import *
from ..api.serializers import *
import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
import pandas as pd
from rest_framework.authtoken.models import Token

#~~~~~~~~~~~~~~~~~~~~~~~~~~~filters/pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from student_management_app.pagination import CustomLimitOffsetPagination

class StudentAttendanceViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = StudentAttendanceSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['attendance_date','student__semester']
    # search_fields = ['first_name', 'last_name', 'mu_id']
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return StudentAttendance.objects.all()
    
    # @action(detail=False, methods=['POST'], url_path='student-attendance')
    # def student_attendance(self, request, *args, **kwargs):
    def create(self,request):
        subject_obj = Subject.objects.get(subject_code=request.data['subject_code'])
        token = request.META.get('HTTP_AUTHORIZATION')
        token_key = token.split(" ")[1]
        user = Token.objects.get(key=token_key).user
        att_list = []
        for item in request.data['attendance']:
            student_obj=Student.objects.get(pk=item['student_id'])
            attendance, created = StudentAttendance.objects.get_or_create(
                student=student_obj,
                attendance_date=request.data['date'],
                status = item['status'],
                reason = item['reason'],
                subject=subject_obj,
                attendance_by=user
            )
            att_list.append(attendance)
        
        return Response(
            StudentAttendanceSerializer(att_list, many=True).data,
            status = status.HTTP_201_CREATED
        )

class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = TeacherAttendanceSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['attendance_date']
        
    def get_queryset(self):
        return TeacherAttendance.objects.all()

class StaffAttendanceViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = StaffAttendanceSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['attendance_date']
        
    def get_queryset(self):
        return StaffAttendance.objects.all()
    
    def create(self,request):
        att_list = []
        for item in request.data['attendance']:
            staff_obj=Staff.objects.get(pk=item['staff_id'])
            attendance, created = StaffAttendance.objects.get_or_create(
                staff=staff_obj,
                attendance_date=request.data['date'],
                status = item['status'],
                reason = item['reason'],
            )
            att_list.append(attendance)
        
        return Response(
            StaffAttendanceSerializer(att_list, many=True).data,
            status = status.HTTP_201_CREATED
        )
