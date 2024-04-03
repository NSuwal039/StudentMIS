from rest_framework import status
from rest_framework.response import Response
from ..models import *
from .serializers import *
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


class EventViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Event.objects.all()
    
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['event_name', ]
    filterset_fields = ['event_type', ]
    # pagination_class = CustomLimitOffsetPagination
    
    @action(detail=True, methods=['POST'], url_path='set-participants')
    def set_participants(self, request, *args, **kwargs):
        self_obj = self.get_object()

        # for item in request.data['user_id']:
        #     i_student = CustomUser.objects.get(pk=item)
        #     participant, created = event_participants.objects.get_or_create(
        #         event=self_obj,
        #         user=i_student,
        #     )
        
        if request.data['students']['all']!="T":
            student_by_semester = Student.objects.filter(
                semester__in=request.data['students']['semester']
            )
            student_by_course = Student.objects.filter(
                course_id__in=request.data['students']['course']
            )
            student_by_batch = Student.objects.filter(
                batch_id__in=request.data['students']['batch']
            )
            students = student_by_semester & student_by_course & student_by_batch
        else:
            students = Student.objects.all()
        
        for item in students:
                participant, created = event_participants.objects.get_or_create(
                event=self_obj,
                user=item.student_user,
            )
        
        if request.data['teachers']['all']!="T":
            teachers = Staff.objects.filter(
                department_id__in=request.data['teachers']['department']
            )
        else:
            teachers=Staff.objects.all()
        
        for item in teachers:
                participant, created = event_participants.objects.get_or_create(
                event=self_obj,
                user=item.staff_user,
            )

        if request.data['staffs']['all']!="T":
            staffs = ExtraUser.objects.filter(
                branch_id__in=request.data['staffs']['branch']
            )
        else:
            staffs=ExtraUser.objects.all()
        
        for item in staffs:
                participant, created = event_participants.objects.get_or_create(
                event=self_obj,
                user=item.extra_user,
        )

        return Response(EventSerializer(self_obj).data, status=status.HTTP_200_OK)
    
    def create(self, request):
        event_data=request.data['event']
        event_serializer = EventSerializer(data=event_data)
        if event_serializer.is_valid():
            created_event = event_serializer.save()
        
            for item in request.data['participants']:
                i_student = CustomUser.objects.get(pk=item)
                participant, created = event_participants.objects.get_or_create(
                    event=created_event,
                    user=i_student,
                )

            return Response(
                EventSerializer(created_event).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                event_serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, pk):
        event_data=request.data['event']
        self_obj = self.get_object()
        event_serializer = EventSerializer(self_obj, data=event_data)

        if event_serializer.is_valid():
            event_serializer.save()

            for item in request.data['participants']:
                i_student = CustomUser.objects.get(pk=item)
                participant, created = event_participants.objects.get_or_create(
                    event=self_obj,
                    user=i_student,
                )


            return Response(
                EventSerializer(self_obj).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                event_serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request, pk):
        event_data=request.data['event']
        self_obj = self.get_object()
        event_serializer = EventSerializer(self_obj, data=event_data, partial=True)

        if event_serializer.is_valid():
            event_serializer.save()

            for item in request.data['participants']:
                i_student = CustomUser.objects.get(pk=item)
                participant, created = event_participants.objects.get_or_create(
                    event=self_obj,
                    user=i_student,
                )

            return Response(
                EventSerializer(self_obj).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                event_serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )


        
    @action(detail=True, methods=['POST'], url_path='set-awards')
    def set_awards(self, request, *args, **kwargs):
        self_obj = self.get_object()

        for item in request.data['awards']:
            award_obj=Awards.objects.get(id=item)

            self_obj.awards.add(award_obj)
        
        return Response(
            EventSerializer(self_obj).data,
            status=status.HTTP_200_OK
        )
        
    
    # @action(detail=True, methods=['POST'], url_path='set-awards')
    # def set_awards(self, request, *args, **kwargs):~
    #     self_obj = self.get_object()

    #     for item in request.data:


class EventCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = EventCategorySerializer

    def get_queryset(self):
        return EventCategory.objects.all()
    
    pagination_class = CustomLimitOffsetPagination

