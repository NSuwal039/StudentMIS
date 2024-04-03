"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
# from django.conf.urls import url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
import debug_toolbar
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog
from student_management_system.views import index,get_user_by_role_ajax
from student_management_system.views import home as main_home
from django.contrib.auth import views as auth_views
from student_management_app.api.viewsets import Login
from rest_framework import routers
from student_management_app.router import router
from rest_framework.authtoken import views
from student_management_app.api import viewsets as api_views
from student_management_app.api.viewsets import get_attendance_status, change_password
from student_management_app.api.reports.views import get_report as report
from student_management_app.api.reports.views import get_report_fields as report_fields
from student_management_app.api.reports.views import check_query_params as check_query_params
from student_management_app.api.csv.views import download_csv as download_csv
from student_management_app.api.csv.views import upload_csv as upload_csv


from school_apps.lms.views import get_book_category_csv, get_books_csv


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login/', api_views.obtain_expiring_auth_token),
    path('api/profile/', api_views.UserProfile),
    # path('api/', include('student_management_system.api', namespace='api')) ,
    path('api/', include('school_apps.formapi.urls')),
    path('admin/', admin.site.urls),
    path('api-token-auth/', views.obtain_auth_token),
    path('', index),
    # path('logs/', HistoryLogs.as_view(), name ="history_log"),
    path('home/', main_home.as_view(), name ="home"),
    path('get_user_by_role/', get_user_by_role_ajax, name ="get_user_by_role"),
    path('',include('student_management_app.urls',namespace='admin_app')),
    path('',include('school_apps.teacher.urls',namespace='teacher')),
    path('',include('school_apps.student.urls',namespace='student')),
    path('parent/',include('school_apps.parents.urls',namespace='parent')),
    path('viewer/',include('viewer.urls',namespace='viewer')),
    path('exam/',include('school_apps.exam.urls',namespace='exam')),
    path('enquiry/',include('school_apps.enquiry.urls',namespace='enquiry')),
    path('',include('school_apps.inventory.urls',namespace='inventory')),
    path('visitor/',include('school_apps.visitor.urls',namespace='visitor')),
    path('cafeteria/',include('school_apps.cafeteria.urls',namespace='cafeteria')),
    path('',include('school_apps.courses.urls',namespace='courses')),
    path('extrauser/',include('school_apps.extrausers.urls',namespace='extrauser')),
    path('',include('school_apps.customusers.urls',namespace='customuser')),
    path('announcement/',include('school_apps.announcement.urls',namespace='announcement')),
    path('administrator/',include('school_apps.administrator.urls',namespace='administrator')),
    path('',include('school_apps.attendance.urls',namespace='attendance_app')),
    path('',include('school_apps.school_settings.urls',namespace='setting_app')),
    path('',include('school_apps.user_profile.urls')),
    path('',include('school_apps.role_permission.urls',namespace='role_app')),
    path('notifications/', include('school_apps.notifications.urls',namespace='notifications')),
    path('academic/', include('school_apps.academic.urls',namespace='academic')),
    path('schedule/',include('schedule.urls')),
    # path('api/residential/', include('school_apps.residential_management_system.urls')),
    
      
    #For resetting password via email follow below four link 
    path('password/reset/',auth_views.PasswordResetView.as_view(template_name = 'passwordreset/password_reset_email.html'), 
		 name = "password_reset"),
	
	path('password/reset/done/',auth_views.PasswordResetDoneView.as_view(template_name = 'passwordreset/password_reset_sent.html'), 
		 name = "password_reset_done"),
	
	path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='passwordreset/password_reset_form.html'),
		 name="password_reset_confirm"),  
	   
	 #<token> check  for valid user or not--><uidb64> user id encoded in base 64--this email is sent to the user
	 #<uidb64> helps to know user who request for password
	path('reset/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='passwordreset/password_reset_complete.html'),
		 name="password_reset_complete"),
    
    
    #debug toolbar
    # path('__debug__/', include(debug_toolbar.urls)),
    
    #for admin js
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),

    # api
    path('api/',include('school_apps.residential_management_system.api_urls',namespace='residential')),
    path('api/reports/', report),
    path('api/reports/get-fields', report_fields),
    path('api/get-attendance-status/', get_attendance_status, name='attendance_status'),
    path('api/change-password/', change_password, name="change_password"),
    path('api/analytics/', include('student_management_app.api.analytics.urls', namespace='analytics')),
    path('api/book-category-csv/', get_book_category_csv, name='book_category_csv'),
    path('api/books-csv/', get_books_csv, name='books_csv'),
    path('api/reports/check_query_params', check_query_params),
    path('api/csv/get-format', download_csv, name='download_csv' ),
    path('api/csv/upload', upload_csv, name='upload_csv')
    
]#+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
    

    
    
