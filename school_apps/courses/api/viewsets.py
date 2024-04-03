from school_apps.courses.api.serializers import *
from school_apps.courses.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.decorators import action
from student_management_app.api.viewsets import input_to_json
#~~~~~~~~~~~~~~~~~~~~~~~~~~~filters/pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from student_management_app.pagination import CustomLimitOffsetPagination

class TermViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Term.objects.all()

    serializer_class = TermSerializer
    # permission_classes = []
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['term_id', 'term_name',]
    filterset_fields = ['term_id', 'term_name',]
    pagination_class = CustomLimitOffsetPagination

    @action(detail=True, methods=['GET'], url_path='create-application-forms')
    def mass_exam_application(self, request, *args, **kwargs):
        self_obj = self.get_object()

        students = Student.objects.filter(status='Running')
        applications = []
        
        for item in students:
            application_id_str = self_obj.term_id + "." + item.student_user.username
            obj, created = application_form.objects.get_or_create(student=item, term=self_obj, application_id= application_id_str
                            ,semester=item.semester)
            selected_subjects = selectedcourses.objects.filter(student_id=item)
            selected_exams = []
            for sub_item in selected_subjects:
                try:
                    selected_exams.append(Exams.objects.get(term=self_obj, subject_id=sub_item.subject_id))
                except:
                    print(str(sub_item.subject_id) + " exam not found~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            
            for exam in selected_exams:
                obj.exam.add(exam, through_defaults={'exam_type':True, 'passed':False})
            
            obj.save()
            applications.append(obj)
        
        return Response(
            application_formSerializer(applications, many=True).data,
            status=status.HTTP_200_OK)
    
    # @action(detail=True, methods=['GET'], url_path='get-exams')
    # def term_exams(self, request, *args, **kwargs):
    #     exams_list = Exams.objects.filter(term=kwargs['pk'])
    #     serializer = ExamsSerializer(exams_list,many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'],  url_path='publish-results')
    def publish_results(self, request, *args, **kwargs):
        selected_term = self.get_object()

        if(selected_term.is_published):
            selected_term.is_published = False
            selected_term.save()
        else:
            selected_term.is_published = True
            selected_term.save()
        
        serializer=TermSerializer(selected_term)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path='print-results')
    def exam_printresults(self, request, *args, **kwargs):
        self_obj = self.get_object()
        results = []
        for item in request.data['student_id']:
            applications = application_form.objects.get(
                student = Student.objects.get(pk=item),
                term=self_obj.term,           
            )
            results.append(applications)
        return Response(
            application_formSerializer(applications, many=True).data,
            status = status.HTTP_200_OK
        )
    
        
class ExamsViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Exams.objects.all()

    serializer_class = ExamsSerializer
    # permission_classes = []
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['exam_id', 'exam_title',]
    filterset_fields = ['term', 'semester','subject_id','date']
    pagination_class = CustomLimitOffsetPagination

    def create(self, request):
        for item in request.data.items():
            if item[0] == 'term':
                term_obj=Term.objects.get(pk=str(item[1]))
        serializer = ExamsSerializer(data=request.data)

        if serializer.is_valid():
            print("in valid", '\n')
            to_return = serializer.save(term=term_obj)
        
            return Response(
                ExamsSerializer(to_return).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request):
        self_obj = self.get_object()
        term_obj=self_obj.term
        for item in request.data.items():
            if item[0] == 'term':
                term_obj=Term.objects.get(pk=str(item[1]))
        

        serializer = ExamsSerializer(self_obj,data=request.data)
        if serializer.is_valid():
            serializer.save(
                term=term_obj
            )
            return Response(
                ExamsSerializer(self_obj).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )


    @action(detail=True, methods=['GET'], url_path='get-grades')
    def exam_grades(self, request, *args, **kwargs):
        selectedexam = self.get_object()
        grades = studentgrades.objects.filter(exam_id = selectedexam)
        serializer = studentgradesSerializer(grades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], url_path='submit-scores')
    def exam_submitscore(self, request, *args, **kwargs):
        self_obj = self.get_object()

        for item in request.data:
            stu_obj = Student.objects.get(id=item['id'])
            app_obj, created = application_form.objects.get_or_create(
                student = stu_obj,
                term = self_obj.term
            )
            try:
                check=studentgrades.objects.get(
                    exam_id=self_obj,
                    # application_id__student__id=item['id']
                    application_id=app_obj
                )
                check.marks=item['marks']
                check.is_absent =True if item['is_absent']=='True' else False
                check.save()
            except:
                studentgrades.objects.create(
                    exam_id=self_obj,
                    # application_id__student__id=item['id'],
                    application_id=app_obj,
                    marks = item['marks'],
                    is_absent =True if item['is_absent']=='True' else False
                )
        
        for item in studentgrades.objects.filter(exam_id=self_obj):
            item.rank = studentgrades.objects.filter(marks__gt=item.marks, exam_id=self_obj).count()+1
            item.save()
        
        response = studentgradesSerializer(studentgrades.objects.filter(exam_id=self_obj), many=True)
        return Response(response.data)
                
    

class application_formViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return application_form.objects.all()

    serializer_class = application_formSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['application_id', 'student',]
    filterset_fields = ['status', 'term',]
    pagination_class = CustomLimitOffsetPagination

    pagination_class = CustomLimitOffsetPagination
    # permission_classes = []

class studentgradesViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return studentgrades.objects.all()

    serializer_class = studentgradesSerializer
    pagination_class = CustomLimitOffsetPagination

    # permission_classes = []

class term_rankingViewSet(viewsets.ModelViewSet):
    queryset = term_ranking.objects.all()
    serializer_class = term_rankingSerializer
    pagination_class = CustomLimitOffsetPagination

    # permission_classes = []

class selectedcoursesViewSet(viewsets.ModelViewSet):
    queryset = selectedcourses.objects.all()
    serializer_class = selectedcoursesSerializer
    pagination_class = CustomLimitOffsetPagination

    filterset_fields = ['student_id','subject_id','semester']

    # permission_classes = []

