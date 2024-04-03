# from crypt import methods
from django.http.response import HttpResponse
from school_apps.academic.api.serializers import RoutineSerializer, SyllabusSerializer
from school_apps.academic.models import Routine, Syllabus
from school_apps.attendance.api.serializers import StudentAttendanceSerializer ,StaffAttendanceSerializer,TeacherAttendanceSerializer
from school_apps.attendance.models import Attendance, StudentAttendance,StaffAttendance,TeacherAttendance
from school_apps.courses.models import selectedcourses
from student_management_app.authentication import ExpiringTokenAuthentication
from student_management_app.models import *
from student_management_app.api.serializers import *
from school_apps.courses.api.serializers import *
from school_apps.events.api.serializers import *
from datetime import datetime as date1
import datetime
import pandas as pd
import csv,io
from rest_framework.authtoken.models import Token
from .reports.views import get_model

from dateutil.parser import parse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
import datetime
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from rest_framework.decorators import authentication_classes

#~~~~~~~~~~~~~~~~~~~~~~~~~~~filters/pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from student_management_app.pagination import CustomLimitOffsetPagination

from rest_framework.generics import UpdateAPIView
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework import serializers

from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly


def generate_redg(campus_obj,batch_obj,school_obj,course_category_obj):
    if Student.objects.filter(campus=campus_obj).exists():
        sn=Student.objects.filter(campus=campus_obj).first().sn +1
    else:
        sn=1
    # import pdb;pdb.set_trace()
    jy=batch_obj.year
    fc=school_obj.faculty_code
    cc=course_category_obj.course_category_code
    cac=campus_obj.campus_code
    register_no = f'{jy}-{fc}-{cc}-{cac}-{sn:04}'
    return register_no ,sn

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
        
    def get_queryset(self):
        # import pdb;pdb.set_trace()
        filters={}
        get_params = list(self.request.query_params.items())

        for item in get_params:
            if item[0]!='subject_code' and item[0]!='search' and item[0]!='limit' and item[0]!='offset':
                filters[item[0]]=item[1]
            if item[0]=='subject_code':
                subject_set = selectedcourses.objects.filter(subject_id__subject_code=item[1]).values('student_id')

        filter_q = Q(**filters)
        final_queryset = Student.objects.filter(filter_q)
        try:
            subject_student_set = Student.objects.filter(pk__in=subject_set)
            intersection = final_queryset&subject_student_set
            return intersection
        except:
            return final_queryset

        # queryset=Student.objects.all()

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'mu_id']
    filterset_fields = ['semester', 'join_year', 'gender', 'course']
    pagination_class = CustomLimitOffsetPagination

        
    def create(self, request):
        course_obj=None
        school_obj=None
        campus_obj=None
        course_category_obj=None
        for item in request.data.items():
            if item[0] == 'student.course':
                course_obj=Course.objects.get(pk=str(item[1]))
            if item[0] == 'student.join_year':
                batch_obj=Batch.objects.get(pk=int(item[1]))
            else:
                batch_obj,created=Batch.objects.get_or_create(year=datetime.datetime.now().year)
            if item[0] == 'student.school':
                school_obj=School.objects.get(pk=int(item[1]))
            if item[0] == 'student.campus':
                campus_obj=Campus.objects.get(pk=int(item[1]))
            if item[0] == 'student.course_category':
                course_category_obj=CourseCategory.objects.get(pk=int(item[1]))
        json = input_to_json(list(request.data.items()))
        serializer = StudentSerializer(data=json['student'])
        redg,sn=generate_redg(campus_obj,batch_obj,school_obj,course_category_obj)
        json['user'].update(username=redg)
        user_serializer = CustomUserSerializer(data=json['user'])
        parent_serializer = ParentSerializer(data=json['guardian'])
        try:
            education_serializer=EducationHistorySerializer(data=json['education_history'],many=True)
        except:
            return Response({
            'message':"Please fill up the Education History",
            }, status=status.HTTP_400_BAD_REQUEST)
        # import pdb;pdb.set_trace()
        emessage = ""
        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage= user_serializer.errors
        elif not parent_serializer.is_valid():
            emessage=parent_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        else:
            user=user_serializer.save(username=redg)
            guardian=parent_serializer.save()
            education=education_serializer.save()
            # import pdb;pdb.set_trace()
            student=serializer.save(
                register_no=redg,
                sn=sn,
                student_user=user,
                course=course_obj,
                guardian=guardian,
                batch=batch_obj,school=school_obj,campus=campus_obj,course_category=course_category_obj
                )
            # import pdb;pdb.set_trace()
            # import pdb;pdb.set_trace()
            for x in education:
                student.education_history.add(x.id)
            
            togo_group,created = Group.objects.get_or_create(name="Student")
            togo_group.user_set.add(student.student_user.id)
            # import pdb;pdb.set_trace()
            # print("course=",student.course,"\n")
            response = {}
            response['student']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        return Response({
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request):
        # student_obj = Student.objects.get(pk=id)
        json = input_to_json(list(request.data.items()))
        student_obj = self.get_object()
        user_obj=student_obj.student_user
        parent_obj=student_obj.guardian
        education_obj=student_obj.education_history.all()
        serializer = StudentSerializer(student_obj,data=json['student'])
        user_serializer = CustomUserSerializer(user_obj,data=json['user'])
        parent_serializer = ParentSerializer(parent_obj,data=json['parent'])
        try:
            education_serializer=EducationHistorySerializer(education_obj,data=json['education_histopry'],many=True)
        except:
            return Response({
            'message':"Please fill up the Education History",
            }, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid() and user_serializer.is_valid() and parent_serializer.is_valid() and education_serializer.is_valid():
            student=serializer.save()
            user=user_serializer.save()
            parent=parent_serializer.save()
            education=education_serializer.save()
            response = {}
            response['student']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        else:
            emessage=serializer.errors
            return Response({
                'status': 'Bad request',
                'message': emessage,
            }, status=status.HTTP_400_BAD_REQUEST)

    
    def partial_update(self, request, pk):
        student_obj = self.get_object()
        course_obj=student_obj.course
        for item in request.data.items():
            if item[0] == 'student.course':
                course_obj=Course.objects.get(pk=str(item[1]))
        json = input_to_json(list(request.data.items()))
        user_obj=student_obj.student_user
        parent_obj=student_obj.guardian
        education_obj=student_obj.education_history.all()
        serializer = StudentSerializer(student_obj,data=json['student'], partial=True)
        user_serializer = CustomUserSerializer(user_obj,data=json['user'], partial=True)
        parent_serializer = ParentSerializer(parent_obj,data=json['guardian'], partial=True)
        try:            
            education_serializer=EducationHistorySerializer(education_obj,data=json['education_history'],partial=True,many=True)
        except:
            return Response({
            'message':"Please fill up the Education History",
            }, status=status.HTTP_400_BAD_REQUEST)
        # import pdb;pdb.set_trace()
        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage= user_serializer.errors
        elif not parent_serializer.is_valid():
            emessage=parent_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        else:
            student=serializer.save(course=course_obj)
            user=user_serializer.save()
            parent=parent_serializer.save()
            education=education_serializer.save()
            for x in education:
                student.education_history.add(x.id)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response({
            'status': 'Bad request',
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], url_path='upload-documents')
    def upload_document(self, request, *args, **kwargs):
        file = request.FILES['file']
        title = request.POST['title']
        user_obj = self.get_object()

        user_file = upload_user_file(title=title, file=file, user=user_obj)
        serializer = DocumentFileSerializer(context = {'request':request},data=user_file)
        serializer.is_valid()
        # import pdb;pdb.set_trace()
        return Response({"message":"Documents Uploaded"})

    @action(detail=True, methods=['GET'], url_path='get-attendance')
    def get_attendance(self, request,pk=None):
        from_date = request.query_params['from']
        to_date = request.query_params['to']
        subject_code_obj = request.query_params['subject_code']
        subject = Subject.objects.get(subject_code = subject_code_obj)
    
        daterange = pd.date_range(from_date, to_date)
        attendance = []
        for dates in daterange: 
            python_date = dates.date()
            try:
                attendance.append(StudentAttendance.objects.get(
                student=int(pk),
                attendance_date=python_date,
                subject = subject
                ))
            except:
                continue
        
        return Response(StudentAttendanceSerializer(attendance, many=True).data, status=status.HTTP_200_OK)
    
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
            subject = Subject.objects.get(subject_code = subject_code)
            att_status = item['status']

            attendance, created = StudentAttendance.objects.get_or_create(
                student=self_obj,
                attendance_date = date,
                subject=subject,
                
            )
            attendance.attendance_by=user
            attendance.status = att_status
            attendance.save()
            attendances.append(attendance)

        return Response(StudentAttendanceSerializer(attendances, many=True).data, status = status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['GET'], url_path='get-documents')   
    def get_documents(self, request, *args, **kwargs):
        self_obj =self.get_object()
        self_user=self_obj.student_user

        files = DocumentFile.objects.filter(custom_user = self_user)
        serializer = DocumentFileSerializer(files, many=True, context={"request": request})


        return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['GET'], url_path='get-csv')
    def get_csv(self, request, *args, **kwargs):
        
        pass
    @action(detail=False, methods=['POST'], url_path='bulk-upload')
    def bulk_upload(self, request, *args, **kwargs):
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return Response({"error":"Not a csv file"}, status=status.HTTP_400_BAD_REQUEST)
        
        data_set = csv_file.read().decode('latin-1')
        io_string = io.StringIO(data_set)
        next(io_string)
        
        file_data = csv.reader(io_string, delimiter=',', quotechar="|")

        for column in file_data:
            batch = column[1]
            student_id = column[2]
            roll_no = column[3]
            full_name =column[4]
            gender =column[5]
            shift = column[6]
            program = column[7]
            dob = parse(column[8]).date()
            email = column[9]
            phone = column[10]

            temporary_address = {
                "province":column[11],
                "district":column[12],
                "municipality":column[13],
                "ward_no":column[14],
                "street_no":column[15],
                "house_no":column[16]
            }

            permanent_address = {
                "province":column[17],
                "district":column[18],
                "municipality":column[19],
                "ward_no":column[20],
                "street_no":column[21],
                "house_no":column[22]
            }

            citizenship_no = column[23]
            ethnicity = column[24]
            scholarship_status=column[25]
            martyr_lineage=column[26]
            disability_status = column[27]

            father_name = column[28]
            father_phone = column[29]
            mother_name = column[30]
            mother_phone = column[31]
            local_guardian_name = column[32]
            local_guardian_phone = column[33]
            blood_group = column[34]

            fname = full_name.split(' ')[0]
            father_username = "p_" + fname.lower() +'_'+ f'{student_id}'
            parent_role = Group.objects.get(name='Parent')

            
            
            student={
                "country": "NP",
                "join_year": batch,
                "mu_id": student_id,
                "roll_no": roll_no,
                "full_name": full_name,
                "gender": gender,
                "shift": shift,
                #create object
                # "bachelor_course": program,     
                "status": "Running",
                "contact": phone,
                "permanent_address": permanent_address,
                "temporary_address": temporary_address,
                "dob": dob,
                "blood_group": blood_group,
                # "course_category": 1,
            }

            parent={
                "father_name":father_name,
                "mother_name":mother_name,
                "father_phone":father_phone,
                "mother_phone":mother_phone,
                "local_guardian_name":local_guardian_name,
                "local_guardian_phone":local_guardian_phone
            }

            fname = full_name.split(" ")[0]
            user={
                "password": "password",
                "is_superuser": False,
                "username": fname+str(student_id),
                "first_name": full_name.split(" ")[0],
                "last_name": full_name.split(" ")[1],
                "is_staff": False,
                "is_active": True,
                "full_name": full_name,
                "email": email,
                "user_type": 5,
                "groups": [
                    5
                ],
            }

            serializer = StudentSerializer(data=student)
            user_serializer = CustomUserSerializer(data=user)
            parent_serializer = ParentSerializer(data=parent)
            emessage = {}
            if not serializer.is_valid():
                emessage['error']=serializer.errors
                emessage['data'] = "student"
            elif not user_serializer.is_valid():
                emessage['error']=user_serializer.errors 
                emessage['data'] = "user"
            elif not parent_serializer.is_valid():
                emessage['error']=parent_serializer.errors
                emessage['data'] = "parent"
            else:  
                fname = user_serializer.validated_data['first_name']
                student_id = serializer.validated_data['stu_id']
                father_username = "p_" + fname.lower() +'_' + f'{student_id}' 
                parent_role = Group.objects.get(name='Parent')
                try:
                    Father_object = CustomUser.objects.create_user(
                        username=father_username, password='password', user_type=parent_role, full_name = father_name
                    )
                except:
                    Father_object = CustomUser.objects.get(
                        username=father_username
                    )

                user=user_serializer.save()
                parent=parent_serializer.save(parent_user=Father_object)
                student=serializer.save(student_user=user, guardian=parent)
                response = {}
                response['student']=serializer.data
                response['parent']=parent_serializer.data
                response['user']=user_serializer.data
                return Response(response, status = status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail =True, methods=['GET'], url_path='get-subjects')
    def get_subjects(self, request, *args, **kwargs):
        student = self.get_object()
        response = []
        courses = selectedcourses.objects.filter(student_id = student)

        return Response(
            selectedcoursesSerializer(courses, many=True).data,
            status = status.HTTP_200_OK
        )

        

    @action(detail='True', methods=['POST'], url_path='select-subjects')
    def select_subjects(self, request, *args, **kwargs):
        courses = request.data['id']
        self_obj = self.get_object()
        error_list = []
        created_list = []

        for item in courses:
            try:
                subject = Subject.objects.get(subject_code=item)
                item=selectedcourses.objects.create(
                    student_id=self_obj,
                    subject_id=subject,
                    semester=self_obj.semester,
                    year= date1.now().year
                )
                created_list.append(item)
            except:
                error_list.append(item)

        return Response(
            selectedcoursesSerializer(created_list, many=True).data,
            status = status.HTTP_200_OK
            )

    @action(detail='True', methods=['GET'], url_path='get-exams')
    def get_exams(self, request, *args, **kwargs):
        self_obj=self.get_object()

        forms = application_form.objects.filter(student=self_obj)
        response = []

        for item in forms:
            temp_json={}
            temp_json['term']=item.term.term_id
            temp_json['exams']=ExamsSerializer(item.exam.all(), many=True).data
            response.append(temp_json)
        
        return Response(response)

    @action(detail='True', methods=['GET'], url_path='get-grades')
    def get_grades(self, request, *args, **kwargs):
        self_obj=self.get_object()
        forms = application_form.objects.filter(student=self_obj)
        response = []

        for item in forms:
            temp_json={}
            grades = studentgrades.objects.filter(application_id=item)
            temp_json['term']=item.term.term_id
            temp_json['grades']=studentgradesSerializer(grades, many=True).data
            response.append(temp_json)
        
        return Response(response)
    
    @action(detail='True', methods=['GET'], url_path='get-routine')
    def get_routine(self, request, *args, **kwargs):
        self_obj=self.get_object()
        try:
            routine = Routine.objects.get(section=self_obj.section, college_year=date1.now().year)
            return Response(RoutineSerializer(routine).data)
        except:
            return Response(
                {'message':'not found'},
                status = status.HTTP_404_NOT_FOUND)
    
    @action(detail='True', methods=['GET'], url_path='get-syllabus')
    def get_syllabus(self, request, *args, **kwargs):
        self_obj=self.get_object()
        try:
            syllabus = Syllabus.objects.filter(semester=self_obj.semester)
            return Response(SyllabusSerializer(data=syllabus, many=True).data)
        except:
            return Response(
                {'message':'not found'},
                status = status.HTTP_404_NOT_FOUND)
    
    @action(detail='True', methods=['GET'], url_path='get-events')
    def get_events(self, request, *args, **kwargs):
        self_obj=self.get_objects()
        
        events = Event.objects.filter(participants__contains = self_obj)
        return Response(EventSerializer(events, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail='True', methods=['GET'], url_path='exam-application')
    def exam_application(self, request, *args, **kwargs):
        self_obj=self.get_object()
        pass

class StaffViewset(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    pagination_class = CustomLimitOffsetPagination
    search_fields = ['first_name', 'last_name', 'mu_id','middle_name']
    filterset_fields = ['branch']


    def create(self, request):
        branch_obj=None
        department_obj=None
        school_obj=None
        obj=list(request.data.items())
        for item in request.data.items():
            if item[0] == 'staff.branch':
                branch_obj=Branch.objects.get(pk=str(item[1]))
                obj.remove(item)
            if item[0] == 'staff.department':
                department_obj=Department.objects.get(pk=str(item[1]))
                obj.remove(item)
            if item[0] == 'staff.school':
                school_obj=School.objects.get(pk=str(item[1]))
                obj.remove(item) 
        json = input_to_json(obj)
        serializer = StaffSerializer(data=json['staff'])
        user_serializer = CustomUserSerializer(data=json['user'])
        parent_serializer=ParentSerializer(data=json['guardian'])
        try:
            training_serializer=TrainingSerializer(data=json['training'],many=True)
        except:
            training_serializer=NoneSerializer(data={})
        try:
            education_serializer=EducationHistorySerializer(data=json['education_history'],many=True)
        except:
            education_serializer=NoneSerializer(data={})
        try:
            employment_serializer=EmploymentHistorySerializer(data=json['employment_history'],many=True)
        except:
            employment_serializer=NoneSerializer(data={})
        # import pdb;pdb.set_trace()
        emessage=""
        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage=user_serializer.errors
        elif not parent_serializer.is_valid():
            emessage=parent_serializer.errors
        elif not training_serializer.is_valid():
            emessage=training_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        elif not employment_serializer.is_valid():
            emessage=employment_serializer.errors
        else:
            print(serializer.validated_data)
            # s_branch = serializer.validated_data['branch']
            user=user_serializer.save()
            guardian=parent_serializer.save()
            staff_staff=serializer.save(
                staff_user=user,
                guardian=guardian,
                branch=branch_obj,
                department=department_obj,
                school=school_obj)

            if not training_serializer.validated_data == {}:
                training=training_serializer.save()
                for x in training:
                    staff_staff.training.add(x.id)
            if not education_serializer.validated_data == {}:
                education=education_serializer.save()
                for y in education:
                    staff_staff.education_history.add(y.id)
            if not employment_serializer.validated_data == {}:       
                employment=employment_serializer.save()
                for z in employment:
                    staff_staff.employment_history.add(z.id)

            togo_group ,created = Group.objects.get_or_create(name="Staff")
            togo_group.user_set.add(staff_staff.staff_user.id)

            response = {}
            response['staff']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        return Response({
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request):
        json = input_to_json(list(request.data.items()))
        staff_obj = self.get_object()
        user_obj=staff_obj.staff_user
        parent_obj=staff_obj.guardian
        training_obj=staff_obj.training.all()
        education_obj=staff_obj.education_history.all()
        employment_obj=staff_obj.employment_history.all()

        serializer = StaffSerializer(staff_obj, data=json['staff'])
        user_serializer = CustomUserSerializer(user_obj, data=json['user'])
        parent_serializer = ParentSerializer(parent_obj, data=json['guardian'])
        training_serializer = TrainingSerializer(training_obj, data=json['training'],many=True)
        education_serializer = EducationHistorySerializer(education_obj, data=json['education_history'],many=True)
        employment_serializer = EmploymentHistorySerializer(employment_obj, data=json['employment_history'],many=True)

        if serializer.is_valid() and user_serializer.is_valid() and parent_serializer.is_valid() and education_serializer.is_valid() and training_serializer.is_valid() and employment_serializer.is_valid():
            student=serializer.save()
            user=user_serializer.save()
            parent=parent_serializer.save()
            training=training_serializer.save()
            education=education_serializer.save()
            employment=employment_serializer.save()
            response = {}
            response['staff']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        else:
            emessage=serializer.errors
            return Response({
                'status': 'Bad request',
                'message': emessage,
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        # student_obj = Student.objects.get(pk=id)
        staff_obj = self.get_object()
        branch_obj=staff_obj.branch
        for item in request.data.items():
            if item[0] == 'staff.branch':
                branch_obj=Branch.objects.get(pk=str(item[1]))
        json = input_to_json(list(request.data.items()))
        user_obj=staff_obj.staff_user
        parent_obj=staff_obj.guardian
        training_obj=staff_obj.training.all()
        education_obj=staff_obj.education_history.all()
        employment_obj=staff_obj.employment_history.all()
    
        serializer = StaffSerializer(staff_obj, data=json['staff'],partial=True)
        user_serializer = CustomUserSerializer(user_obj, data=json['user'], partial=True)
        parent_serializer = ParentSerializer(parent_obj, data=json['guardian'], partial=True)

        try:
            training_serializer = TrainingSerializer(training_obj, data=json['training'], partial=True,many=True)
        except:
            training_serializer=NoneSerializer(data={})
        try:
            education_serializer = EducationHistorySerializer(education_obj, data=json['education_history'], partial=True,many=True)
        except:
            education_serializer=NoneSerializer(data={})
        try:
            employment_serializer = EmploymentHistorySerializer(employment_obj, data=json['employment_history'], partial=True,many=True)
        except:
            employment_serializer=NoneSerializer(data={})

        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage=user_serializer.errors
        elif not parent_serializer.is_valid():
            emessage=parent_serializer.errors
        elif not training_serializer.is_valid():
            emessage=training_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        elif not employment_serializer.is_valid():
            emessage=employment_serializer.errors
        else:
            user=user_serializer.save()
            staff_staff=serializer.save(
                branch=branch_obj)
            parent=parent_serializer.save()

            if not training_serializer.validated_data == {}:
                training=training_serializer.save()
                for x in training:
                    staff_staff.training.add(x.id)
            if not education_serializer.validated_data == {}:
                education=education_serializer.save()
                for y in education:
                    staff_staff.education_history.add(y.id)
            if not employment_serializer.validated_data == {}:       
                employment=employment_serializer.save()
                for z in employment:
                    staff_staff.employment_history.add(z.id)

            response = {}
            response['staff']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)

        return Response({
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'], url_path='get-documents')   
    def get_documents(self, request, *args, **kwargs):
        self_obj =self.get_object()
        self_user=self_obj.extra_user

        files = DocumentFile.objects.filter(custom_user = self_user)
        serializer = DocumentFileSerializer(files, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], url_path='upload-documents')
    def upload_document(self, request, *args, **kwargs):
        file = request.FILES['file']
        title = request.POST['title']
        user_obj = self.get_object()

        user_file = upload_user_file(title=title, file=file, user=user_obj)
        serializer = DocumentFileSerializer(user_file)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'], url_path='get-attendance')
    def get_attendance(self, request, *args, **kwargs):
        self_obj=self.get_object()
        from_date = request.query_params['from']
        to_date = request.query_params['to']

        daterange = pd.date_range(from_date, to_date)
        attendance = []
        for dates in daterange: 
            python_date = dates.date()
            try:
                attendance.append(StaffAttendance.objects.get(
                staff=self_obj,
                attendance_date=python_date,
            ))
            except:
                continue
        
        return Response(StaffAttendanceSerializer(attendance, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path = 'set-attendance')
    def set_attendance(self, request, *args, **kwargs):
        self_obj=self.get_object()
        attendances = []
        token = request.META.get('HTTP_AUTHORIZATION')
        token_key = token.split(" ")[1]
        user = Token.objects.get(key=token_key).user
        for item in request.data:
            date = item['date']
            att_status = item['status']

            attendance, created = StaffAttendance.objects.get_or_create(
                student=self_obj,
                attendance_date = date,
            )
            attendance.attendance_by=user
            attendance.status = att_status
            attendance.save()
            attendances.append(attendance)

        return Response(StaffAttendanceSerializer(attendances, many=True).data, status = status.HTTP_201_CREATED)

class TeacherViewset(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    pagination_class = CustomLimitOffsetPagination
    search_fields = ['first_name', 'last_name', 'mu_id','middle_name']
    filterset_fields = ['branch']


    def create(self, request):
        branch_obj=None
        school_obj=None
        department_obj=None
        obj=list(request.data.items())
        for item in request.data.items():
            if item[0] == 'teacher.branch':
                branch_obj=Branch.objects.get(pk=str(item[1]))
                obj.remove(item)
            if item[0] == 'teacher.school':
                school_obj=School.objects.get(pk=str(item[1]))
                obj.remove(item)
            if item[0] == 'teacher.department':
                department_obj=Department.objects.get(pk=str(item[1]))
                obj.remove(item)
        json = input_to_json(obj)
        serializer = TeacherSerializer(data=json['teacher'])
        user_serializer = CustomUserSerializer(data=json['user'])
        parent_serializer=ParentSerializer(data=json['guardian'])
        try:
            research_and_consultancy_serializer=ResearchAndConsultancySerializer(data=json['research_and_consultancy'],many=True)
        except:
            research_and_consultancy_serializer=NoneSerializer(data={})
        try:
            graduate_research_supervision_serializer=GraduateResearchSupervisionSerializer(data=json['graduate_research_supervision'],many=True)
        except:
            graduate_research_supervision_serializer=NoneSerializer(data={})
        try:
            graduate_project_supervision_serializer=GraduateProjectSupervisionSerializer(data=json['graduate_project_supervision'],many=True)
        except:
            graduate_project_supervision_serializer=NoneSerializer(data={})
        try:
            workshop_seminar_conference_serializer=WorkshopSeminarConferenceSerializer(data=json['workshop_seminar_conference'],many=True)
        except:
            workshop_seminar_conference_serializer=NoneSerializer(data={})
        try:
            fellowship_awards_studyvisit_serializer=FellowshipAwardsStudyvisitSerializer(data=json['fellowship_awards_studyvisit'],many=True)
        except:
            fellowship_awards_studyvisit_serializer=NoneSerializer(data={})
        try:
            publication_and_copyrights_serializer=PublicationAndCopyrightsSerializer(data=json['publication_and_copyrights'],many=True)
        except:
            publication_and_copyrights_serializer=NoneSerializer(data={})
        try:
            education_serializer=EducationHistorySerializer(data=json['education_history'],many=True)
        except:
            education_serializer=NoneSerializer(data={})
        try:
            employment_serializer=EmploymentHistorySerializer(data=json['employment_history'],many=True)
        except:
            employment_serializer=NoneSerializer(data={})
        # import pdb;pdb.set_trace()
        emessage=""
        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage=user_serializer.errors
        elif not parent_serializer.is_valid():
            emessage=parent_serializer.errors
        elif not research_and_consultancy_serializer.is_valid():
            emessage=research_and_consultancy_serializer.errors
        elif not graduate_project_supervision_serializer.is_valid():
            emessage=graduate_project_supervision_serializer.errors
        elif not workshop_seminar_conference_serializer.is_valid():
            emessage=workshop_seminar_conference_serializer.errors
        elif not fellowship_awards_studyvisit_serializer.is_valid():
            emessage=fellowship_awards_studyvisit_serializer.errors
        elif not publication_and_copyrights_serializer.is_valid():
            emessage=publication_and_copyrights_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        elif not graduate_research_supervision_serializer.is_valid():
            emessage=graduate_research_supervision_serializer.errors
        elif not employment_serializer.is_valid():
            emessage=employment_serializer.errors
        else:
            print(serializer.validated_data)
            # s_branch = serializer.validated_data['branch']
            user=user_serializer.save()
            guardian=parent_serializer.save()

            teacher=serializer.save(
                faculty_user=user,
                guardian=guardian,
                branch=branch_obj,
                school=school_obj,
                department=department_obj
                )
            
            if not education_serializer.validated_data == {}:
                education=education_serializer.save()
                for y in education:
                    teacher.education_history.add(y.id)
            if not employment_serializer.validated_data == {}:
                employment=employment_serializer.save()
                for z in employment:
                    teacher.employment_history.add(z.id)
            if not research_and_consultancy_serializer.validated_data == {}:
                rac=research_and_consultancy_serializer.save()
                for x in rac:
                    teacher.research_and_consultancy.add(x.id)
            if not graduate_research_supervision_serializer.validated_data == {}:
                grs=graduate_research_supervision_serializer.save()
                for x in grs:
                    teacher.graduate_research_supervision.add(x.id)
            if not graduate_project_supervision_serializer.validated_data == {}:
                gps=graduate_project_supervision_serializer.save()
                for x in gps:
                    teacher.graduate_project_supervision.add(x.id)
            if not workshop_seminar_conference_serializer.validated_data == {}:
                wsc=workshop_seminar_conference_serializer.save()
                for x in wsc:
                    teacher.workshop_seminar_conference.add(x.id)
            if not fellowship_awards_studyvisit_serializer.validated_data == {}:
                fas=fellowship_awards_studyvisit_serializer.save()
                for x in fas:
                    teacher.fellowship_awards_studyvisit.add(x.id)
            if not publication_and_copyrights_serializer.validated_data == {}:
                pac=publication_and_copyrights_serializer.save()
                for x in pac:
                    teacher.publication_and_copyrights.add(x.id)

            togo_group ,created = Group.objects.get_or_create(name="Teacher")
            togo_group.user_set.add(teacher.faculty_user.id)

            response = {}
            response['teacher']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        return Response({
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request):
        json = input_to_json(list(request.data.items()))
        teacher_obj = self.get_object()
        user_obj=teacher_obj.staff_user
        parent_obj=teacher_obj.guardian
        education_obj=teacher_obj.education_history.all()
        employment_obj=teacher_obj.employment_history.all()
        rac_obj=teacher_obj.research_and_consultancy.all()
        grs_obj=teacher_obj.graduate_research_supervision.all()
        gps_obj=teacher_obj.graduate_project_supervision.all()
        wsc_obj=teacher_obj.workshop_seminar_conference.all()
        fas_obj=teacher_obj.fellowship_awards_studyvisit.all()
        pac_obj=teacher_obj.publication_and_copyrights.all()


        serializer = TeacherSerializer(teacher_obj, data=json['teacher'])
        user_serializer = CustomUserSerializer(user_obj, data=json['user'])
        parent_serializer = ParentSerializer(parent_obj, data=json['guardian'])
        education_serializer = EducationHistorySerializer(education_obj, data=json['education_history'],many=True)
        employment_serializer = EmploymentHistorySerializer(employment_obj, data=json['employment_history'],many=True)
        research_and_consultancy_serializer=ResearchAndConsultancySerializer(rac_obj,data=json['research_and_consultancy'],many=True)
        graduate_research_supervision_serializer=GraduateResearchSupervisionSerializer(grs_obj,data=json['graduate_research_supervision'],many=True)
        graduate_project_supervision_serializer=GraduateProjectSupervisionSerializer(gps_obj,data=json['graduate_project_supervision'],many=True)
        workshop_seminar_conference_serializer=WorkshopSeminarConferenceSerializer(wsc_obj,data=json['workshop_seminar_conference'],many=True)
        fellowship_awards_studyvisit_serializer=FellowshipAwardsStudyvisitSerializer(fas_obj,data=json['fellowship_awards_studyvisit'],many=True)
        publication_and_copyrights_serializer=PublicationAndCopyrightsSerializer(pac_obj,data=json['publication_and_copyrights'],many=True)

        if serializer.is_valid() and user_serializer.is_valid() and parent_serializer.is_valid() and education_serializer.is_valid() and employment_serializer.is_valid() and research_and_consultancy_serializer.is_valid() and graduate_research_supervision_serializer.is_valid() and graduate_project_supervision_serializer.is_valid() and workshop_seminar_conference_serializer.is_valid() and fellowship_awards_studyvisit_serializer.is_valid() and publication_and_copyrights_serializer.is_valid():
            student=serializer.save()
            user=user_serializer.save()
            parent=parent_serializer.save()
            education=education_serializer.save()
            employment=employment_serializer.save()
            rac=research_and_consultancy_serializer.save()
            grs=graduate_research_supervision_serializer.save()
            gps=graduate_project_supervision_serializer.save()
            wsc=workshop_seminar_conference_serializer.save()
            fas=fellowship_awards_studyvisit_serializer.save()
            pac=publication_and_copyrights_serializer.save()
            response = {}
            response['teacher']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        else:
            emessage=serializer.errors
            return Response({
                'status': 'Bad request',
                'message': emessage,
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        # student_obj = Student.objects.get(pk=id)
        teacher_obj = self.get_object()
        branch_obj=teacher_obj.branch
        for item in request.data.items():
            if item[0] == 'teacher.branch':
                branch_obj=Branch.objects.get(pk=str(item[1]))
        json = input_to_json(list(request.data.items()))
        user_obj=teacher_obj.faculty_user
        parent_obj=teacher_obj.guardian
        education_obj=teacher_obj.education_history.all()
        employment_obj=teacher_obj.employment_history.all()
        rac_obj=teacher_obj.research_and_consultancy.all()
        grs_obj=teacher_obj.graduate_research_supervision.all()
        gps_obj=teacher_obj.graduate_project_supervision.all()
        wsc_obj=teacher_obj.workshop_seminar_conference.all()
        fas_obj=teacher_obj.fellowship_awards_studyvisit.all()
        pac_obj=teacher_obj.publication_and_copyrights.all()
        

        serializer = TeacherSerializer(teacher_obj, data=json['teacher'],partial=True)
        user_serializer = CustomUserSerializer(user_obj, data=json['user'], partial=True)
        parent_serializer = ParentSerializer(parent_obj, data=json['guardian'], partial=True)
        try:
            education_serializer = EducationHistorySerializer(education_obj, data=json['education_history'], partial=True,many=True)
        except:
            education_serializer=NoneSerializer(data={})
        try:
            employment_serializer = EmploymentHistorySerializer(employment_obj, data=json['employment_history'], partial=True,many=True)
        except:
            employment_serializer=NoneSerializer(data={})
        try:
            research_and_consultancy_serializer=ResearchAndConsultancySerializer(rac_obj,data=json['research_and_consultancy'],many=True, partial=True)
        except:
            research_and_consultancy_serializer=NoneSerializer(data={})
        try:
            graduate_research_supervision_serializer=GraduateResearchSupervisionSerializer(grs_obj,data=json['graduate_research_supervision'],many=True, partial=True)
        except:
            graduate_research_supervision_serializer=NoneSerializer(data={})
        try:
            graduate_project_supervision_serializer=GraduateProjectSupervisionSerializer(gps_obj,data=json['graduate_project_supervision'],many=True, partial=True)
        except:
            graduate_project_supervision_serializer=NoneSerializer(data={})
        try:
            workshop_seminar_conference_serializer=WorkshopSeminarConferenceSerializer(wsc_obj,data=json['workshop_seminar_conference'],many=True, partial=True)
        except:
            workshop_seminar_conference_serializer=NoneSerializer(data={})
        try:
            fellowship_awards_studyvisit_serializer=FellowshipAwardsStudyvisitSerializer(fas_obj,data=json['fellowship_awards_studyvisit'],many=True, partial=True)
        except:
            fellowship_awards_studyvisit_serializer=NoneSerializer(data={})
        try:
            publication_and_copyrights_serializer=PublicationAndCopyrightsSerializer(pac_obj,data=json['publication_and_copyrights'],many=True, partial=True)
        except:
            publication_and_copyrights_serializer=NoneSerializer(data={})

        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage=user_serializer.errors
        elif not parent_serializer.is_valid():
            emessage=parent_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        elif not employment_serializer.is_valid():
            emessage=employment_serializer.errors
        elif not research_and_consultancy_serializer.is_valid():
            emessage=research_and_consultancy_serializer.errors
        elif not graduate_project_supervision_serializer.is_valid():
            emessage=graduate_project_supervision_serializer.errors
        elif not workshop_seminar_conference_serializer.is_valid():
            emessage=workshop_seminar_conference_serializer.errors
        elif not fellowship_awards_studyvisit_serializer.is_valid():
            emessage=fellowship_awards_studyvisit_serializer.errors
        elif not publication_and_copyrights_serializer.is_valid():
            emessage=publication_and_copyrights_serializer.errors
        elif not education_serializer.is_valid():
            emessage=education_serializer.errors
        elif not graduate_research_supervision_serializer.is_valid():
            emessage=graduate_research_supervision_serializer.errors
        elif not employment_serializer.is_valid():
            emessage=employment_serializer.errors
        else:
            user=user_serializer.save()
            parent=parent_serializer.save()
            teacher=serializer.save(
                branch=branch_obj)
        
            if not education_serializer.validated_data == {}:
                education=education_serializer.save()
                for y in education:
                    teacher.education_history.add(y.id)
            if not employment_serializer.validated_data == {}:
                employment=employment_serializer.save()
                for z in employment:
                    teacher.employment_history.add(z.id)
            if not research_and_consultancy_serializer.validated_data == {}:
                rac=research_and_consultancy_serializer.save()
                for x in rac:
                    teacher.research_and_consultancy.add(x.id)
            if not graduate_research_supervision_serializer.validated_data == {}:
                grs=graduate_research_supervision_serializer.save()
                for x in grs:
                    teacher.graduate_research_supervision.add(x.id)
            if not graduate_project_supervision_serializer.validated_data == {}:
                gps=graduate_project_supervision_serializer.save()
                for x in gps:
                    teacher.graduate_project_supervision.add(x.id)
            if not workshop_seminar_conference_serializer.validated_data == {}:
                wsc=workshop_seminar_conference_serializer.save()
                for x in wsc:
                    teacher.workshop_seminar_conference.add(x.id)
            if not fellowship_awards_studyvisit_serializer.validated_data == {}:
                fas=fellowship_awards_studyvisit_serializer.save()
                for x in fas:
                    teacher.fellowship_awards_studyvisit.add(x.id)
            if not publication_and_copyrights_serializer.validated_data == {}:
                pac=publication_and_copyrights_serializer.save()
                for x in pac:
                    teacher.publication_and_copyrights.add(x.id)
            response = {}
            response['teacher']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)

        return Response({
            'message': emessage,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'], url_path='get-documents')   
    def get_documents(self, request, *args, **kwargs):
        self_obj =self.get_object()
        self_user=self_obj.faculty_user

        files = DocumentFile.objects.filter(custom_user = self_user)
        serializer = DocumentFileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path='upload-documents')
    def upload_document(self, request, *args, **kwargs):
        file = request.FILES['file']
        title = request.POST['title']
        user_obj = self.get_object()

        user_file = upload_user_file(title=title, file=file, user=user_obj)
        serializer = DocumentFileSerializer(user_file)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['GET'], url_path='get-attendance')
    def get_attendance(self, request, *args, **kwargs):
        self_obj=self.get_object()
        from_date = request.query_params['from']
        to_date = request.query_params['to']

        daterange = pd.date_range(from_date, to_date)
        attendance = []
        for dates in daterange: 
            python_date = dates.date()
            try:
                attendance.append(TeacherAttendance.objects.get(
                staff=self_obj,
                attendance_date=python_date,
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
            att_status = item['status']

            attendance, created = TeacherAttendance.objects.get_or_create(
                student=self_obj,
                attendance_date = date,
            )
            attendance.attendance_by=user
            attendance.status = att_status
            attendance.save()
            attendances.append(attendance)

        return Response(TeacherAttendanceSerializer(attendances, many=True).data, status = status.HTTP_201_CREATED)

class CampusViewSet(viewsets.ModelViewSet):  
    serializer_class = CampusSerializer
    queryset=Campus.objects.all()
    pagination_class = CustomLimitOffsetPagination

class SchoolViewSet(viewsets.ModelViewSet):  
    serializer_class = SchoolSerializer
    queryset=School.objects.all()
    pagination_class = CustomLimitOffsetPagination
class SubjectViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Subject.objects.all()
    
    serializer_class = SubjectSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['subject_code','subject_name']
    filterset_fields = ['subject_code', 'course_category', 'subject_name','course','created_at']
    pagination_class = CustomLimitOffsetPagination

class SubjectTeacherViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = SubjectTeacherSerializer
        
    def get_queryset(self):
        return SubjectTeacher.objects.all()
    # permission_classes = []

# class SemesterViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#     serializer_class = SemesterSerializer
        
#     def get_queryset(self):
#         return Semester.objects.all()
#     # permission_classes = []

# class SectionViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#     serializer_class = SectionSerializer
        
#     def get_queryset(self):
#         return Section.objects.all()
#     # permission_classes = []

class DepartmentViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_fields = ['name']
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return Department.objects.all()
    # permission_classes = []

class BranchViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = BranchSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_fields = ['name']
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return Branch.objects.all()
    # permission_classes = []

class CourseCategoryViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = CourseCategorySerializer
    queryset=CourseCategory.objects.all()
        
    def get_queryset(self):
        return CourseCategory.objects.all()
    # permission_classes = []

class CustomUserViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['full_name',]
    filterset_fields = ['full_name']
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return CustomUser.objects.all()
    # permission_classes = []

class CourseViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['course_name','course_code']
    filterset_fields = ['course_category','course_name','course_code','department']
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return Course.objects.all()
    # permission_classes = []

# class DocumentFileViewSet(viewsets.ModelViewSet):
#     serializer_class = DocumentFileSerializer
        
#     def get_queryset(self):
#         return DocumentFile.objects.all()
#     # permission_classes = []

#     # @action(detail=True, method='POST')
#     # def upload_multiple(self, request, *args, **kwargs):


class ComplainViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = ComplainSerializer
        
    def get_queryset(self):
        return Complain.objects.all()
    # permission_classes = []

class CertificateTemplateViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = CertificateTemplateSerializer
    # permission_classes = []
        
    def get_queryset(self):
        return CertificateTemplate.objects.all()

class DocumentFileViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = DocumentFileSerializer
        
    def get_queryset(self):
        return DocumentFile.objects.all()

def upload_user_file(*args, **kwargs):
        title = kwargs['title']
        file = kwargs['file']
        try:
            custom_user = kwargs['user'].staff_user
        except:
            try:
                custom_user = kwargs['user'].student_user
            except:
                custom_user = kwargs['user'].extra_user

        created_file= DocumentFile.objects.create(title=title, file=file, custom_user=custom_user)
        return created_file

@api_view(http_method_names=['POST'])
def Login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    # return Response({'a':'b'})

class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():     
            token, created =  Token.objects.get_or_create(user=serializer.validated_data['user'])

            utc_now = datetime.datetime.utcnow()    
            if not created and token.created < timezone.now() - datetime.timedelta(hours=24):
                token.delete()
                token = Token.objects.create(user=serializer.validated_data['user'])
                token.created = datetime.datetime.utcnow()
                token.save()
            
            profile_obj = get_profile_from_user(serializer.validated_data['user'], request)
            groups = serializer.validated_data['user'].groups.all()
            groups_data = GroupSerializer(groups, many=True).data

            perms=[]
            for item in serializer.validated_data['user'].get_user_permissions():
                app_label, codename = item.split('.')
                perms.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))

            perm_json=[]
            for item in perms:
                perm_json.append({
                    'id':item.id,
                    'name':item.name,
                    'codename':item.codename,
                    'permission':item.content_type.app_label+'.'+item.codename,
                    'content_type':item.content_type.pk}
                )

            return Response({
                'token': token.key,
                'profile':profile_obj,
                'group':groups_data,
                'permissions': perm_json,
                
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()

@api_view(['GET'])
def UserProfile(request):
    token = request.META.get('HTTP_AUTHORIZATION')

    try:
        token_user = Token.objects.get(key=token.split(' ')[1]).user

        perms=[]
        for item in token_user.get_user_permissions():
            app_label, codename = item.split('.')
            perms.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))

        perm_json=[]
        for item in perms:
            perm_json.append({
                'id':item.id,
                'name':item.name,
                'codename':item.codename,
                'permission':item.content_type.app_label+'.'+item.codename,
                'content_type':item.content_type.pk}
            )

        profile_obj = get_profile_from_user(token_user, request)

        groups = token_user.groups.all()
        groups_data = GroupSerializer(groups, many=True).data
        return Response({
                    'user_id':token_user.pk,
                    'email':token_user.email,
                    'userid':token_user.username,      
                    'permissions': perm_json,
                    'profile':profile_obj,
                    'group':groups_data
                })
    except:
        return Response({'error':'Invalid Token'})

class PermissionsViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = PermissionSerializer
    pagination_class = CustomLimitOffsetPagination
    
    
    def get_queryset(self):
        return Permission.objects.all()
        
    
    @action(detail=False, methods=['POST'], authentication_classes=[TokenAuthentication])
    def update_permissions(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk = request.data['id'])
        try:
            add = request.data['add']
        except:
            add = []      
        try:
            remove = request.data['remove']
        except:
            remove=[]

        response={}

        for item in add:
            perm = Permission.objects.get(id = item)
            user.user_permissions.add(perm) 
       

        for item in remove:
            perm = Permission.objects.get(id = item)
            user.user_permissions.remove(perm)

        return Response(CustomUserSerializer(user).data, status = status.HTTP_200_OK)

class GroupViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    pagination_class = CustomLimitOffsetPagination
    
    
    def get_queryset(self):
        return Group.objects.all()
    
    @action(detail=True, methods=['POST'], url_path='set-permissions')
    def set_permissions(self, request, *args, **kwargs):
        self_obj=self.get_object()
        try:
            add = request.data['add']
        except:
            add = []      
        try:
            remove = request.data['remove']
        except:
            remove=[]

        for item in add:
            perm = Permission.objects.get(id = item)
            self_obj.permissions.add(perm) 
       

        for item in remove:
            perm = Permission.objects.get(id = item)
            self_obj.permissions.remove(perm)
        
        return Response(
            GroupSerializer(self_obj).data,
            status=status.HTTP_200_OK
        )
    

def input_to_json(list):
    header_list=[]
    return_json = {}
    list_two=['employment_history','training','education_history','research_and_consultancy','graduate_research_supervision','graduate_project_supervision','workshop_seminar_conference','fellowship_awards_studyvisit','publication_and_copyrights']
    # import pdb;pdb.set_trace()

    # list=[('book.1.sid','1'),('book.1.name','dfs'),('article.1.title','okay'),('student.id','2'),('book.2.name','sdf'),('book.2.id','2')]
    for item in list:
        head = item[0].split('.')[0]
        if head not in header_list:
            header_list.append(head)
    
    for item in header_list:
        if item in list_two:
            return_json[item]=[]
        else:
            return_json[item]={}
    
    for item in list:
        split_item=item[0].split('.')
        item_length=len(split_item)
        if item_length == 3:
            insert_at=int(split_item[1])
            try:
                # import pdb;pdb.set_trace()
                items = return_json[str(item[0].split('.')[0])][insert_at]
                items[str(split_item[2])]=item[1]
            except IndexError:
                dict={}
                dict[str(split_item[2])]=item[1]
                return_json[str(item[0].split('.')[0])].insert(insert_at,dict) 
        elif item_length==2:  
            return_json[str(item[0].split('.')[0])][str(item[0].split('.')[1])]=item[1]
        else:
            return_json[str(item[0].split('.')[0])]=item[1]
    # import pdb;pdb.set_trace()
    return (return_json)
    

class SessionYearViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = SessionYearSerializer
        
    def get_queryset(self):
        return SessionYear.objects.all()

class BatchViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = BatchSerializer
        
    def get_queryset(self):
        return Batch.objects.all()

class AwardsViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = AwardsSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_fields = ['department',]
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return Awards.objects.all()

class awards_recipientViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = awards_recipientSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['award','user']
    pagination_class = CustomLimitOffsetPagination
        
    def get_queryset(self):
        return awards_recipient.objects.all()


@api_view(['GET'])
def get_attendance_status(request):
    status_strings = [
        'Present',
        'Absent(Informed)',
        'Absent(Not Informed)',
        'Late',
        'Excused'
    ]

    return Response(
        status_strings,
        status = status.HTTP_200_OK
    ) 


def get_profile_from_user(CustomUser, request):
    try:
        profile_object = CustomUser.student
        to_return = StudentSerializer(
            profile_object,
            context={"request":request}
            ).data
    except:
        try:
            profile_object = CustomUser.staff
            to_return = StaffSerializer(profile_object,
            context={
                "request":request
            }).data
        except:
            try:
                profile_object = CustomUser.extrauser
                to_return = ExtraUserSerializer(profile_object,
            context={
                "request":request
            }).data
            except:
                profile_object = CustomUser.adminuser
                to_return = AdminUserSerializer(profile_object,
            context={
                "request":request
            }).data
    
    return (to_return)

@api_view(['PATCH'])
def change_password(request):
    try:
        user=CustomUser.objects.get(pk=request.data['user_id'])
    except:
        return Response(
            status=status.HTTP_400_BAD_REQUEST
        )
    
    old_password = request.data['old_password']
    new_password1 = request.data['new_password1']
    new_password2 = request.data['new_password2']
    if not user.check_password(old_password):
            return Response(
                {"details":"Incorrect password"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if new_password1!=new_password2:
        return Response(
                {"details":"New passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    password_validation.validate_password(new_password1, user)
    user.set_password(new_password1)
    user.save()

    return Response(
        CustomUserSerializer(user).data,
        status=status.HTTP_200_OK
    )


