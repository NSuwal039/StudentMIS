from django.shortcuts import render
from rest_framework import viewsets
from .serializers import VacancySerializer
from .models import Vacancy 
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

#mail part
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from student_management_app.models import Student


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

class VacancyReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


#mail part
def Mail_part(request):
    user_detail = Student.objects.get(student_user=request.user)
    ctx = {"user": user_detail}

    subject = 'Subject'
    html_message = render_to_string('cv.html', ctx)
    plain_message = strip_tags(html_message)
    from_email = 'From <from@example.com>'
    to = 'sanjivr361@gmail.com'

    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    return HttpResponse('mail has been sent!')



