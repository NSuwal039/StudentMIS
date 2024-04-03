from django.urls import path
from . import views
from .api.views import *

app_name = 'courses'

urlpatterns=[
    path('', views.index, name='index'),
  
    path('addexam/', views.addexam, name='addexam'),
    path('addterm/', views.addterm, name='addterm'),
    path('ajax/addexam_marks_ajax/', views.addexam_marks_ajax, name='addexam_marks_ajax'),
    path('viewterm/', views.viewterm, name='viewterm'),
    path('checkterm_exams/<str:pk>', views.checkterm_exams, name='checkterm_exams'),
    path('examresults/', views.examresults, name='examresults'),
    path('publishresults/', views.publishresults, name='publishresults'),
    path('toggle_results/<str:pk>', views.toggle_results, name="toggle_results"),
    path('examreport/', views.examreport, name='examreport'),
    path('viewresults/', views.viewresults, name='viewresults'),
    path('examtoppers/', views.examtoppers, name='examtoppers'),
    path('addstudentmarks/', views.addstudentmarks, name='addstudentmarks'),
    path('submitscores/', views.submitscores, name='submitscores'),
    path('studentdetails/', views.student_details, name='student_details'),
    

    #bulk print admit cards
    path('bulkprintadmitcard/', views.bulkprintadmitcard, name='bulkprintadmitcard'),
    path('printadmitcards/', views.printadmitcards, name='printadmitcards'),
    path('ajax/returnexamdropdown/', views.returnexamdropdown, name='returnexamdropdown'),
    path('ajax/return_exams_admit/', views.return_exams_admit, name='return_exams_admit'),
    path('ajax/returnstudentlist_admit/', views.returnstudentlist_admit, name='returnstudentlist_admit'),

    #bulk print results
    path('bulkprintresults/', views.bulkprintresults, name='bulkprintresults'),
    path('ajax/return_exams_results/', views.return_exams_results, name='return_exams_results'),
    path('ajax/returnstudentlist_results/', views.returnstudentlist_results, name='returnstudentlist_results'),
    path('printresults/', views.printresults, name='printresults'),

    path('confirmexamapplication/', views.confirmexamapplication, name='confirmexamapplication'),
    path('studentmarksentry/<str:id>', views.studentsmarksentry, name='studentmarksentry'),
    path('confirmapplication/', views.confirmapplication, name='confirmapplication'),
    path('ajax/studentlist/', views.studentsAjax, name='studentlist'),
    path('ajax/confirmAjax/', views.confirmAjax, name='confirmAjax'),

    #subject to teacher
    path('assign_subject_to_teacher/', views.assign_subject_to_teacher, name='assign_subject_to_teacher'),
    path('manage_subject_teacher/', views.showsubjectteacherlist, name='showsubjectteacherlist'),
    path('edit_subject_teacher/', views.editsubjectteacher, name='editsubjectteacher'),      #<str:exam_id>
    path('delete_subjectteacher/<str:pk>/', views.deletesubjectteacher, name='deletesubjectteacher'),
    path('ajax/subject_to_teacher/', views.subject_to_teacher_Ajax, name='subject_to_teacher_ajax'),
    path('ajax/fill_section_select/', views.fill_section_select, name='fill_section_select'),

    #subject to class
    path('subject_to_class/', views.subject_to_class, name='subject_to_class'),
    path('ajax/subject_to_class/', views.subject_to_class_Ajax, name='subject_to_class_ajax'),
    path('ajax/returnexamlist/', views.returnexamlist_Ajax, name='returnexamlist_ajax'),
    path('printexamreport/<str:pk>', views.printexamreport, name='printexamreport'),

    #subject to student
    path('assign_subject_to_student/', views.assign_subject_to_student, name='assign_subject_to_student'),
    path('drop_subject/', views.drop_subject, name='drop_subject'),
    path('ajax/subject_to_student/', views.subject_to_student_Ajax, name='subject_to_student_ajax'),
    path('ajax/return_student_subject/', views.return_student_subject, name='return_student_subject'),
    path('delete_subjectstudent/<str:pk>/', views.deletesubjectstudent, name='deletesubjectstudent'),

    #add exam marks
    path('addexammarks/', views.addexammarks, name='addexammarks'),
    path('ajax/fill_exam_select/', views.fill_exam_select, name='fill_exam_select'),
    path('ajax/examsAjax/', views.examsAjax, name='examsAjax'),

    #mass exam application
    path('massexamapplication', views.massexamapplication, name="massexamapplication"),
    path('toggle_application/<str:pk>', views.toggle_application, name="toggle_application"),
    path('gci_printresults/', views.gci_printresults, name="gci_printresults"),
    
    #api
    # path('')
    
    
]