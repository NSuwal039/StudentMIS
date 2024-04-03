from school_apps.courses.api.serializers import ExamsSerializer, TermSerializer, studentgradesSerializer
from school_apps.courses.models import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets

# def term_exams(request, pk):
#     exams_list = Exams.objects.filter(term__term_id=pk)
#     serializer = ExamsSerializer(exams_list,many=True)
#     return Response(serializer.data)

def exam_studentlist(request, pk):
    selectedexam = Exams.objects.get(exam_id=pk)
    grades = studentgrades.objects.filter(exam_id = selectedexam).order_by('-marks')
    serializer = studentgradesSerializer(grades, many=True)
    return Response(serializer.data)

# def publish_results(request, pk):
#     selected_term = Term.objects.get(pk=pk)

#     if(selected_term.is_published):
#         selected_term.is_published = False
#         selected_term.save()
#     else:
#         selected_term.is_published = True
#         selected_term.save()
    
#     serializer=TermSerializer(selected_term)
#     return Response(serializer.data)

def exam_submitscore(request):
    pass