from multiprocessing import Event
from ...models import Student, Staff, ExtraUser,  Subject, Course, CourseCategory, Department, Branch, Awards, SubjectTeacher, Teacher
from school_apps.attendance.models import StudentAttendance, StaffAttendance, TeacherAttendance
from school_apps.events.models import Event, EventCategory
from school_apps.courses.models import *
from school_apps.lms.models import *
from school_apps.spis.models import Vacancy
import pandas as pd
import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models.query import QuerySet
from django.db.models import Sum, Count
from dateutil.relativedelta import relativedelta

@api_view(['GET'])
def student_analytics(request):
    total_students = Student.objects.all().count()

    today = datetime.datetime.today().date()
    weekday = today.weekday()
    start_delta = datetime.timedelta(days=weekday, weeks=1)
    start_of_week = today - start_delta + datetime.timedelta(days=1)
    week = pd.date_range( start_of_week, today)
    today_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }
    week_attendance = []
    week_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }

    delta_month = datetime.timedelta(days=weekday, weeks=4)
    start_of_month = today - delta_month + datetime.timedelta(days=1)
    month = pd.date_range( start_of_month, today)
    month_attendance = []
    month_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }

    course_query = Student.objects.values('course__course_name').annotate(student_count=Count('course')).order_by()
    coursecat_query = Student.objects.values('course_category__course_name').annotate(student_count=Count('course_category')).order_by()
    student_by_subject = selectedcourses.objects.values('subject_id__subject_name').annotate(student_count=Count('subject_id')).order_by()
    
    attendance_today=StudentAttendance.objects.filter(attendance_date=today).values('status').annotate(student_count=Count('status')).order_by()
    for item in attendance_today:
        today_attendance_json[item['status']]+=item['student_count']

    for item in week:
        week_attendance.append(
            StudentAttendance.objects.filter(attendance_date=item).values('status').annotate(student_count=Count('status')).order_by()
        )
    for item in week_attendance:
        for att_item in item:
            week_attendance_json[att_item['status']]+=att_item['student_count']
    
    for item in month:
        month_attendance.append(
            StudentAttendance.objects.filter(attendance_date=item).values('status').annotate(student_count=Count('status')).order_by()
        )
    
    for item in month_attendance:
        for att_item in item:
            month_attendance_json[att_item['status']]+=att_item['student_count']
    return Response(
        {
            'total':total_students,
            'student_by_course':course_query,
            'student_by_coursecategory':coursecat_query,
            'student_by_subject':student_by_subject,
            'attendance_today':today_attendance_json,
            'attendance_week':week_attendance_json,
            'attendance_month':month_attendance_json

        },
        status=status.HTTP_200_OK
        
    )

@api_view(['GET'])
def teacher_analytics(request):
    total_teachers = Teacher.objects.count()
    today = datetime.datetime.today().date()
    weekday = today.weekday()
    start_delta = datetime.timedelta(days=weekday, weeks=1)
    start_of_week = today - start_delta + datetime.timedelta(days=1)
    week = pd.date_range( start_of_week, today)
    today_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }
    week_attendance = []
    week_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }

    delta_month = datetime.timedelta(days=weekday, weeks=4)
    start_of_month = today - delta_month + datetime.timedelta(days=1)
    month = pd.date_range( start_of_month, today)
    month_attendance = []
    month_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }

    coursecategory_count = {}
    for item in CourseCategory.objects.all():
        coursecategory_count[item.course_name]=0

    for item in CourseCategory.objects.all():
        # coursecategory_count[item]=Staff.objects.filter()
        for staff in Teacher.objects.all():
            if item in staff.courses.all():
                coursecategory_count[item]+=1
    
    staff_teacher_count={}
    for item in Subject.objects.all():
        staff_teacher_count[item.subject_name]=0
    
    for item in Subject.objects.all():
        staff_teacher_count[item.subject_name] = SubjectTeacher.objects.filter(subject=item).count()

    attendance_today=TeacherAttendance.objects.filter(attendance_date=today).values('status').annotate(student_count=Count('status')).order_by()
    for item in attendance_today:
            today_attendance_json[item['status']]+=item['student_count']

    for item in week:
        week_attendance.append(
            TeacherAttendance.objects.filter(attendance_date=item).values('status').annotate(student_count=Count('status')).order_by()
        )
    
    for item in week_attendance:
        for att_item in item:
            week_attendance_json[att_item['status']]+=att_item['student_count']

    for item in month:
        month_attendance.append(
            TeacherAttendance.objects.filter(attendance_date=item).values('status').annotate(student_count=Count('status')).order_by()
        )
    
    for item in month_attendance:
        for att_item in item:
            month_attendance_json[att_item['status']]+=att_item['student_count']

    return Response(
        {
        'total':total_teachers,
        'course_category_count':coursecategory_count,
        'subject_count':staff_teacher_count,
        'attendance_today':today_attendance_json,
        'attendance_week':week_attendance_json,
        'attendance_month':month_attendance_json
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def staff_analytics(request):
    total_staff = Staff.objects.count()
    today = datetime.datetime.today().date()
    weekday = today.weekday()
    start_delta = datetime.timedelta(days=weekday, weeks=1)
    start_of_week = today - start_delta + datetime.timedelta(days=1)
    week = pd.date_range( start_of_week, today)
    today_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }
    week_attendance = []
    week_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }

    delta_month = datetime.timedelta(days=weekday, weeks=4)
    start_of_month = today - delta_month + datetime.timedelta(days=1)
    month = pd.date_range( start_of_month, today)
    month_attendance = []
    month_attendance_json = {
        "Present":0,
        "Absent(Informed)":0,
        'Absent(Not Informed)':0,
        'Late':0
    }

    branch_query = Staff.objects.values('branch__name').annotate(staff_count=Count('branch')).order_by()

    attendance_today=StaffAttendance.objects.filter(attendance_date=today).values('status').annotate(student_count=Count('status')).order_by()
    for item in attendance_today:
            today_attendance_json[item['status']]+=item['student_count']

    for item in week:
        week_attendance.append(
            StaffAttendance.objects.filter(attendance_date=item).values('status').annotate(student_count=Count('status')).order_by()
        )
    
    for item in week_attendance:
        for att_item in item:
            week_attendance_json[att_item['status']]+=att_item['student_count']

    for item in month:
        month_attendance.append(
            StaffAttendance.objects.filter(attendance_date=item).values('status').annotate(student_count=Count('status')).order_by()
        )
    
    for item in month_attendance:
        for att_item in item:
            month_attendance_json[att_item['status']]+=att_item['student_count']
    
        return Response(
        {
        'total':total_staff,
        'staff_by_branch':branch_query,
        'attendance_today':today_attendance_json,
        'attendance_week':week_attendance_json,
        'attendance_month':month_attendance_json
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def subject_analytics(request):
    total_count = Subject.objects.count()
    coursecat_query = Subject.objects.values('course_category__course_name').annotate(subject_count=Count('course_category')).order_by()
    course_query = Subject.objects.values('course__course_name').annotate(subject_count=Count('course')).order_by()

    subject_student={}
    
    for item in Subject.objects.all():
        subject_student[item.subject_name]=selectedcourses.objects.filter(subject_id=item).count()
    
    return Response(
        {
            'total':total_count,
            'course_category_count':coursecat_query,
            'course_query':course_query,
            'students_per_subject':subject_student
        }
    )

@api_view(['GET'])
def department_analytics(request):

    total=Department.objects.count()

    teachers_by_department={}
    for item in Department.objects.all():
        teachers_by_department[item.name]= item.staff_set.count()
    
    return Response(
        {
            'total':total,
            'teachers_by_department':teachers_by_department
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def branch_analytics(request):
    staff_by_branch={}
    for item in Branch.objects.all():
        staff_by_branch[item.name]= item.extrauser_set.count()
    
    return Response(
        {
            'total':Branch.objects.count(),
            'staff_by_branch':staff_by_branch
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def course_analytics(request):
    return Response(
        {
            'total':Course.objects.count(),
        },
        status=status.HTTP_200_OK
    )

@api_view(["GET"])
def awards_analytics(request):
    return Response(
        {
            'total':Awards.objects.count(),
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def event_analytics(request):
    today = datetime.datetime.today().date()
    weekday = today.weekday()
    start_delta = datetime.timedelta(days=weekday, weeks=1)
    start_of_week = today - start_delta + datetime.timedelta(days=1)
    week = pd.date_range( start_of_week, today)
    category_query = Event.objects.values('event_type__name').annotate(event_count=Count('event_type')).order_by()

    events_this_week = Event.objects.filter(start_date__in=week).count()
    total_participants = 0
    for item in Event.objects.all():
        total_participants+=item.participants.all().count()
    
    
    
    return Response(
        {
            'total':Event.objects.count(),
            'event_by_type':category_query,
            'events_this_week':events_this_week,
            'total_participants':total_participants
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def library_analytics(request):
    total_books = Books.objects.count()
    total_book_category = BookCategory.objects.count()
    total_books_quantity=Books.objects.aggregate(Sum('totalquantity'))
    total_books_receive_quantity=Books.objects.aggregate(Sum('receive_quantity'))
    total_book_issues = borrowed_books.objects.filter(status='borrowed').count()
    total_book_returns = borrowed_books.objects.filter(status='returned').count()


    return Response(
        {
            'total_books':total_books,
            'total_book_category':total_book_category,
            'total_books_quantity':total_books_quantity["totalquantity__sum"],
            'total_books_receive_quantity':total_books_receive_quantity["receive_quantity__sum"],
            'total_book_issues':total_book_issues,
            'total_book_returns':total_book_returns,
        },
        status =status.HTTP_200_OK
    )

@api_view(['GET'])
def vacancy_analytics(request):
    #Siddartha fill here

    return Response(
        {
            'total-vacancy':Vacancy.objects.count()
        }
    )
    pass