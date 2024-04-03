from ..models import *
from .serializers import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token, TokenProxy
from rest_framework import viewsets
import json
from rest_framework.decorators import action

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import  permission_required
import datetime


class EnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = EnquirySerializer

    def get_queryset(self):
        return Enquiry.objects.all()
    
    @action(detail=True, methods=['GET'])
    def send_entrance_info(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        date = datetime.date.today()
        html_content = render_to_string('enquiry/entrance_info_email_template.html', {'enquiry':enquiry_obj,'date':date})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.application_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def send_application_email(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        html_content = render_to_string('enquiry/application_form_email_template.html', {'enquiry':enquiry_obj,})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.application_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def send_entrance_results(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        date = datetime.date.today()
        html_content = render_to_string('enquiry/entrance_result_email_template.html', {'enquiry':enquiry_obj, 'date':date})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.entrance_result_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def send_interview_results(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        html_content = render_to_string('enquiry/interview_result_email_template.html', {'enquiry':enquiry_obj})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.interview_result_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def send_confirmation_email(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        html_content = render_to_string('enquiry/confirmation_email_template.html', {'enquiry':enquiry_obj})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.interview_result_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.all()

    @action(detail=True, methods=['GET'])
    def send_entrance_info(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        date = datetime.date.today()
        html_content = render_to_string('enquiry/entrance_info_email_template.html', {'enquiry':enquiry_obj,'date':date})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.application_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def send_entrance_results(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        date = datetime.date.today()
        html_content = render_to_string('enquiry/entrance_result_email_template.html', {'enquiry':enquiry_obj, 'date':date})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.entrance_result_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def send_interview_results(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        html_content = render_to_string('enquiry/interview_result_email_template.html', {'enquiry':enquiry_obj})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.interview_result_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def send_confirmation_email(self, request, *args, **kwargs):
        enquiry_obj = self.get_object()
        html_content = render_to_string('enquiry/confirmation_email_template.html', {'enquiry':enquiry_obj})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            "testemail",
            text_content,
            settings.EMAIL_HOST_USER,
            [enquiry_obj.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        enquiry_obj.interview_result_sent = True
        enquiry_obj.save()

        serializer = EnquirySerializer(enquiry_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def enroll(self, request, *args, **kwargs):
        pass