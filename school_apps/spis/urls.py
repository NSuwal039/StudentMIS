from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# moved to student_management_app/router.py
# router.register('vacancyapi', views.VacancyViewSet, basename='vacancy')
# router.register('vacancyviewapi', views.VacancyReadOnlyModelViewSet, basename='vacancyview')

urlpatterns = [
    # path('', include(router.urls)),
    path('send-mail/', views.Mail_part, name = 'send-mail'),
]