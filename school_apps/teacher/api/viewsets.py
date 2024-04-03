from school_apps.attendance.api.serializers import TeacherAttendanceSerializer
from school_apps.attendance.models import TeacherAttendance
from school_apps.courses.api.serializers import ExamsSerializer
from student_management_app.models import *
from student_management_app.api.serializers import *
from student_management_app.api.viewsets import upload_user_file, input_to_json
from school_apps.courses.models import *
import pandas as pd
from rest_framework.authtoken.models import Token

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
import json
from rest_framework.decorators import action

#~~~~~~~~~~~~~~~~~~~~~~~~~~~filters/pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from student_management_app.pagination import CustomLimitOffsetPagination

class TeacherViewSet(viewsets.ModelViewSet):
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'mu_id','employment_id', 'middle_name']
    filterset_fields = ['institution', 'department', 'designation', 'employment_type','courses', 'subject']
    def get_queryset(self):
        return Staff.objects.all()

    serializer_class = StaffSerializer
    # def list(self, request):
    #     stu = Staff.objects.all()
    #     serializer = StaffSerializer(stu, many=True)
    #     return Response(serializer.data)
    
        
    def create(self, request):
        for item in request.data.items():
            if item[0] == 'teacher.department':
                department_obj=Department.objects.get(pk=str(item[1]))
        json_obj = input_to_json(list(request.data.items()))

        # created_json=json.dumps(json_obj)
        # json_object = json.loads(created_json)
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)

        serializer = StaffSerializer(data=json_obj['teacher'])
        user_serializer = CustomUserSerializer(data=json_obj['user'])
        emessage = ""
        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage= user_serializer.errors
        else:

            user=user_serializer.save()
            teacher=serializer.save(
                staff_user=user,
                department=department_obj)

            togo_group = Group.objects.get(name="Teacher")
            togo_group.user_set.add(teacher.staff_user)
            response={}
            response['teacher']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        return Response({
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk):
        staff_obj = self.get_object()
        department_obj=staff_obj.department
        for item in request.data.items():
            if item[0] == 'teacher.department':
                department_obj=Department.objects.get(pk=str(item[1]))
        json = input_to_json(list(request.data.items()))
        user_obj = staff_obj.staff_user
        serializer = StaffSerializer(staff_obj, data=json['teacher'])
        user_serializer = CustomUserSerializer(user_obj, data=json['user'])
        
        if serializer.is_valid() and user_serializer.is_valid():
            teacher=serializer.save(
                department=department_obj
            )
            user=user_serializer.save()
            response={}
            response['teacher']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        # staff_obj = Staff.objects.get(pk=id)
        staff_obj = self.get_object()
        json = input_to_json(list(request.data.items()))
        user_obj = staff_obj.staff_user
        serializer = StaffSerializer(staff_obj, data=json['teacher'], partial=True)
        user_serializer = CustomUserSerializer(user_obj, data=json['user'], partial=True)
        
        if serializer.is_valid() and user_serializer.is_valid():
            teacher=serializer.save()
            user=user_serializer.save()
            response={}
            response['teacher']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'], url_path='upload-documents')
    def upload_document(self, request, *args, **kwargs):
        file = request.FILES['file']

        f_title = request.POST.__getitem__('title')
        user_obj = self.get_object()

        user_file = upload_user_file(title= f_title, file=file, user=user_obj)
        serializer = DocumentFileSerializer(user_file)
        return Response(serializer.data)


    @action(detail=True, methods=['GET'], url_path='get-exams')
    def getexams(self, request, *args, **kwargs):
        teacher_obj=self.get_object()
        subjects=SubjectTeacher.objects.filter(teacher=teacher_obj).values('subject')
        # term_obj=Term.objects.get(pk=request.query_params.get('term'))
        terms = Term.objects.all()
        response = []
        for item in terms:
            temp_json={}
            exams = Exams.objects.filter(term=item, subject_id__in=subjects)
            temp_json['term_id']=item.term_id
            temp_json['term_title']=item.term_name
            temp_json['exams']=serializer = ExamsSerializer(exams, many=True).data
            response.append(temp_json)
        return Response(response)
    
    @action(detail=True, methods=['GET'], url_path='get-subjects')
    def getsubjects(self, request, *args, **kwargs):
        teacher_obj = self.get_object()
        subjects=SubjectTeacher.objects.filter(teacher=teacher_obj)

        serializer = SubjectTeacherSerializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'], url_path='get-students')
    def getstudents(self, request, *args, **kwargs):
        # selected_subject=SubjectTeacher.objects.get(pk=request.query_params.get['subject_id'])
        subjects= SubjectTeacher.objects.filter(teacher= self.get_object())
        response = []
        for item in subjects:
            temp_json={}
            temp_json['subject_code']=item.subject.subject_code
            temp_json['subject_name']=item.subject.subject_name
            try:
                temp_json['class']=item.section.semester.master_semester
            except:
                temp_json['class']=item.section.semester.bachelor_semester
            students = selectedcourses.objects.filter(subject_id = item.subject, student_id__section = item.section).values('student_id')
            temp_list=[]
            for item in students:
                temp_list.append(Student.objects.get(pk=item['student_id']))
            temp_json['students']= StudentSerializer(temp_list, many=True).data
            response.append(temp_json)
        return Response(response)

    
    @action(detail=True, methods=['GET'], url_path='get-documents')   
    def get_documents(self, request, *args, **kwargs):
        self_obj =self.get_object()
        self_user=self_obj.staff_user

        files = DocumentFile.objects.filter(custom_user = self_user)
        serializer = DocumentFileSerializer(files, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], url_path='select-subjects')
    def assign_self_subjects(self, request, *args, **kwargs):
        self_obj = self.get_object()
        subject_code_list = request.data['subject_code']
        resp=[]

        for item in subject_code_list:
            subject_teacher, created=SubjectTeacher.objects.get_or_create(
                teacher=self_obj,
                subject = Subject.objects.get(subject_code=item)
            )
            resp.append(subject_teacher)
        
        return Response(
            SubjectTeacherSerializer(resp, many=True).data,
            status = status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['GET'], url_path='get-attendance')
    def get_attendance(self, request, *args, **kwargs):
        self_obj=self.get_object()
        from_date = request.query_params['from']
        to_date = request.query_params['to']
        subject_code = request.query_params['subject_code']
        subject = SubjectTeacher.objects.get(subject_id = subject_code)

        daterange = pd.date_range(from_date, to_date)
        attendance = []
        for dates in daterange: 
            python_date = dates.date()
            try:
                attendance.append(TeacherAttendance.objects.get(
                teacher=self_obj,
                attendance_date=python_date,
                subjectteacher = subject
            ))
            except:
                continue
        
        return Response(TeacherAttendanceSerializer(attendance, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path = 'set-attendance')
    def set_attendance(self, request, *args, **kwargs):
        self_obj=self.get_object()
        attendances = []
        token = request.META.get('HTTP_AUTHORIZATION')
        token_key = token.split(" ")[1]
        user = Token.objects.get(key=token_key).user
        for item in request.data:
            date = item['date']
            subject_code = item['subject_code']
            try:
                subject = SubjectTeacher.objects.get(subject_id = subject_code)
                att_status = item['status']

                attendance, created = TeacherAttendance.objects.get_or_create(
                    teacher=self_obj,
                    attendance_date = date,
                    subjectteacher=subject,
                )
                attendance.attendance_by=user
                attendance.status = att_status
                attendance.save()
                attendances.append(attendance)
            except:
                pass

        return Response(TeacherAttendanceSerializer(attendances, many=True).data, status = status.HTTP_201_CREATED)
            