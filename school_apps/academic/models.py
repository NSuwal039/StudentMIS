
from django.db.models.fields.related import ManyToManyField
from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
# from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from student_management_app.models import CustomUser
# from school_apps.courses.models import Semester, Section, Subject
from student_management_app.models import Section, Semester, Subject, Student,CourseCategory
from simple_history.models import HistoricalRecords

class Syllabus(models.Model):
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='syllabus')
    semester = models.IntegerField()
    description = models.TextField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'syllabus'
        verbose_name_plural = 'Syllabus'

    def __str__(self):
        return self.title



class Assignment(models.Model):
    assignment_category = (
    ('Assigned',"Assigned"),('Completed','Completed')
    )
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    # class_id=models.ForeignKey(Class,on_delete=models.CASCADE)
    semester = models.IntegerField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE,null = True, blank=True)
    Subject = models.ForeignKey(Subject, on_delete=models.CASCADE,null = True)
    file = models.FileField(upload_to='Assignment_section', blank=True, null=True)
    student = models.ManyToManyField(CustomUser,through = 'Grade')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null = True,blank=True,related_name='teacher_assignment')
    draft = models.BooleanField(_('Save as Draft'),default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'assignment'
        verbose_name_plural = 'Assignment'

    def __str__(self):
        return self.title


class Grade(models.Model):
    assignment_status = (
    ('Assigned',"Assigned"),('Completed','Completed')
    )
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assignment_status = models.CharField(_("Assignment Category"),choices = assignment_status,  max_length=50, default = 'Assigned',null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.PositiveIntegerField(null = True,blank = True)
    grade_status = models.BooleanField(default=False)#for checking whether assignment is returned to student with points
    feedback = models.CharField(max_length=255, null=True, blank=True, default="No feedback")
    answer_upload = models.FileField(upload_to = 'Assignment_grades', null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Routine(models.Model):
    year_choices = (
		('2021','2021'),('2022','2022'),('2021','2021'),('2021','2021'),
	)
    
    DAYS_OF_WEEK = (
		('SUNDAY','SUNDAY'),
		('MONDAY','MONDAY'),
  		('TUESDAY','TUESDAY'),
  		('WEDNESDAY','WEDNESDAY'),
  		('THURSDAY','THURSDAY'),
  		('FRIDAY','FRIDAY'),
   		('SATURDAY','SATURDAY'),
	)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    routine_file = models.FileField(_("Routine"), upload_to='College Routine')
    semester = models.IntegerField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    # subject = models.ForeignKey(Subject,related_name = 'routine_subject', on_delete=models.CASCADE)
    college_year = models.CharField(max_length=50, choices = year_choices, null=True, blank=True)
    day = models.CharField(max_length=100,choices = DAYS_OF_WEEK, null=True, blank=True)
    # staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    starting_time = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    ending_time = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    room = models.CharField( max_length=100,null=True, blank=True)
    # course = models.ForeignKey(SectionSubject, on_delete=models.CASCADE)
    course = models.ForeignKey(Section, on_delete=models.CASCADE, related_name= 'routine_course', null=True, blank=True)
    history = HistoricalRecords()
    
    
    class Meta:
        db_table = 'routine'
        verbose_name_plural = 'Routines'
    
    class Meta:
        db_table = 'routine'
        verbose_name_plural = 'Routines'

