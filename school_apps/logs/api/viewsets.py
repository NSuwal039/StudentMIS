from .serializers import UserLogSerializer, ReportLogSerializer
from rest_framework.decorators import action
from rest_framework import viewsets
from django.db.models import Q
from ..models import ReportLog, UserLog

#~~~~~~~~~~~~~~~~~~~~~~~~~~~filters/pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from student_management_app.pagination import CustomLimitOffsetPagination

class UserLogViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    def get_queryset(self):
        filters={}
        get_params = list(self.request.query_params.items())

        for item in get_params:
            if item[0]=='model_name':
                if item[1] =='teacher':
                    filters[item[0]]='staff'
                elif item[1]=='staff':
                    filters[item[0]]='extrauser'
                else:
                    filters[item[0]]=item[1]
            
            print(item[0])
            if item[0]!='limit' and item[0]!='offset':
                print('test')
                filters[item[0]]=item[1]

        print(filters)
        filter_q = Q(**filters)
        queryset = UserLog.objects.filter(filter_q)
        

        return queryset
    
    # permission_classes = []
    serializer_class = UserLogSerializer
    # filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    # filterset_fields = ['app_name', 'model_name','action','user','object_id']
    pagination_class = CustomLimitOffsetPagination


class ReportLogViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = ReportLogSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    # search_fields = []
    filterset_fields = ['model_name', 'app_name', 'user']
    pagination_class = CustomLimitOffsetPagination
    http_method_names = ['get']

    def get_queryset(self):
        return ReportLog.objects.all()