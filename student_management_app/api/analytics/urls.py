from .views import *
from django.urls import path

app_name='analytics'

urlpatterns=[
    path('students/', student_analytics, name='student_analytics'),
    path('teachers/', teacher_analytics, name='teacher_analytics'),
    path('staffs/', staff_analytics, name='staff_analytics'),
    path('subjects/', subject_analytics, name='subject_analytics'),
    path('departments/', department_analytics, name='department_analytics'),
    path('branches/', branch_analytics, name='branch_analytics'),
    path('courses/', course_analytics, name='course_analytics'),
    path('awards/', awards_analytics, name='awards_analytics'),
    path('events/', event_analytics, name='events_analytics'),
    path('library/', library_analytics, name='library_analytics'),


]