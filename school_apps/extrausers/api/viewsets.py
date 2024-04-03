from school_apps.attendance.api.serializers import StaffAttendanceSerializer
from school_apps.attendance.models import StaffAttendance
from school_apps.cafeteria.models import CafeteriaStaff
from student_management_app.api.serializers import *
from student_management_app.models import *
from student_management_app.pagination import CustomLimitOffsetPagination
from rest_framework.decorators import action
from student_management_app.api.viewsets import input_to_json, upload_user_file
import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
import json
from rest_framework.authtoken.models import Token


class ExtraUserViewset(viewsets.ModelViewSet):
    queryset = ExtraUser.objects.all()
    serializer_class = ExtraUserSerializer
    pagination_class = CustomLimitOffsetPagination
    search_fields = ['first_name', 'last_name', 'mu_id','middle_name']
    filterset_fields = ['branch']


    def create(self, request):
        for item in request.data.items():
            if item[0] == 'staff.branch':
                branch_obj=Branch.objects.get(pk=str(item[1]))
        json = input_to_json(list(request.data.items()))
        serializer = ExtraUserSerializer(data=json['staff'])
        user_serializer = CustomUserSerializer(data=json['user'])
        emessage=""
        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage=user_serializer.errors
        else:
            print(serializer.validated_data)
            # s_branch = serializer.validated_data['branch']
            user=user_serializer.save()
            extra_staff=serializer.save(
                extra_user=user,
                branch=branch_obj)

            # try:
            #     if s_branch==Branch.objects.get(name="Cafeteria"):
            #         CafeteriaStaff.objects.create(extra_user=user.extrauser)
            # except:
            #     pass

            togo_group = Group.objects.get(name="Staff")
            togo_group.user_set.add(extra_staff.extra_user)

            response = {}
            response['staff']=serializer.data
            response['user']=user_serializer.data
            return Response(response, status = status.HTTP_201_CREATED)
        return Response({
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
        user_obj=staff_obj.extra_user

        serializer = ExtraUserSerializer(staff_obj, data=json['staff'],partial=True)
        user_serializer = CustomUserSerializer(user_obj, data=json['user'], partial=True)


        if not serializer.is_valid():
            emessage=serializer.errors
        elif not user_serializer.is_valid():
            emessage=user_serializer.errors
        else:
            user=user_serializer.save()
            extra_staff=serializer.save(
                branch=branch_obj)

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

        return Response(StaffSerializer(attendances, many=True).data, status = status.HTTP_201_CREATED)
            

    
