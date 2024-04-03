from tkinter.messagebox import NO
from django.db import models
from student_management_app.models import (Subject, SessionYear, Staff, Student, Semester,
                                           Section, CustomUser, ExtraUser, SubjectTeacher, Teacher)

attendance_choices = (
        ('Present','Present'),('Absent(Informed)','Absent(Informed)'),('Absent(Not Informed)','Absent(Not Informed)'),
        ('Late','Late'),
        ('Excused','Excused'),
    )
class Attendance(models.Model):
    # subject=models.ForeignKey(Subject,on_delete=models.DO_NOTHING, null=True)
    attendance_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length = 50,choices = attendance_choices , blank=True)
    reason = models.CharField(max_length=500, blank=True)
    updated_at=models.DateTimeField(auto_now=True)
    attendance_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        abstract = True
    
class StudentAttendance(Attendance):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE, null=True)

class TeacherAttendance(Attendance):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subjectteacher = models.ForeignKey(SubjectTeacher, on_delete=models.CASCADE, null=True)

class StaffAttendance(Attendance):
    staff=models.ForeignKey(Staff, on_delete=models.CASCADE)
    
class AttendanceReport(models.Model):
    attendance_choices = (
        ('Present','Present'),('Absent(Informed)','Absent(Informed)'),('Absent(Not Informed)','Absent(Not Informed)'),
        ('Late','Late'),
        ('Excused','Excused'),
    )
    
    student=models.ForeignKey(Student,on_delete=models.DO_NOTHING, null=True)
    staff=models.ForeignKey(Staff,on_delete=models.DO_NOTHING, null=True)
    extra_user=models.ForeignKey(Teacher,on_delete=models.DO_NOTHING, null=True)
    # attendance=models.ForeignKey(Attendance,on_delete=models.CASCADE)
    # status=models.BooleanField(default=False)
    # normal_status = models.CharField(max_length=50,null=True,blank=True)
    status = models.CharField(max_length = 50,choices = attendance_choices , blank=True)
    remarks = models.CharField(max_length=250, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        try:
            return f'{self.student}'
        except:
            try:
                return f'{self.teacher}'
            except:
                return f'{self.extra_user}'




