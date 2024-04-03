import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import Group
from school_apps.transports.models import Transport
from django.core.validators import MinValueValidator, MaxValueValidator

# from PIL import Image
# for qrcode
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
# from simple_history.models import HistoricalRecords
# barcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File


gender_choice = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Third Gender', 'Third Gender')
)
bachelor_semester_choices = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
    )
master_semester_choices = (
        ('First','First'),
        ('Second','Second'),
        ('Third','Third'),
        ('Fourth','Fourth'),
    )
YEAR_CHOICES = []
for r in range(2010, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))


def default_address_dict():
    return {
        'house_no': '',
        'street_name':'',
        'ward_no':'',
        'municipality':'',
        'district':'',
        'province':''
    }

class CourseCategory(models.Model):  # i also want to see subject for particular course
    course_name = models.CharField(max_length=255)
    course_category_code=models.CharField(max_length=1, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.course_name
    
    class Meta:
        ordering = ('-created_at',)

class Department(models.Model):
    name = models.CharField(_("Department Name"), max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
    class Meta:
        ordering = ('-created_at',)
class Course(models.Model):  # i also want to see subject for particular course
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    course_name = models.CharField(max_length=255,null = True)
    course_code = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,null = True, blank=True)
    course_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_Course'
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    # def __str__(self):
    #     return self.course_name

    class Meta:
        ordering = ('-created_at',)
class Batch(models.Model):
    year=models.PositiveIntegerField(
            validators=[
                MinValueValidator(1900), 
                MaxValueValidator(datetime.datetime.now().year)],
            primary_key=True)
    
    class Meta:
        ordering=['-year']   

class Branch(models.Model):
    name = models.CharField(verbose_name="Branch name:", max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_at',)

class Campus(models.Model):
    name=models.CharField(max_length=255)
    campus_code=models.CharField(max_length=4)
    description=models.TextField(blank=True,null=True)
    motto=models.CharField(max_length=255,null=True,blank=True)
    address=models.TextField(max_length=255,null=True,blank=True)
    available_course=models.ManyToManyField(Course,blank=True ,related_name="course_college")
    logo=models.ImageField(upload_to='logo/%Y/%m/%d/', null=True, blank=True)
    website=models.CharField(max_length=500,null=True,blank=True)
    # staff=models.ManyToManyField(Staff,blank=True,related_name="staff_college")
    # admin=models.OneToOneField(AdminUser,blank=True,null=True,related_name="admin_college",on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ("add_college_admin", "Can Add Admin"),
            ("add_college_staff", "Can Add Staff"),
        )

    def __str__(self):
        return self.name


class School(models.Model):
    name=models.CharField(max_length=255)
    faculty_code=models.CharField(max_length=4)



class CustomUser(AbstractUser):  # use this for extending deafult django auth system
    full_name = models.CharField(max_length=255)
    user_type = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    # password = models.CharField(_('password'), max_length=128, null = True)

    class Meta:
        db_table = 'tbl_Customuser'
        verbose_name = _("customuser")
        verbose_name_plural = _("customusers")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Parent(models.Model):
    # --gci field
    home_phone = models.CharField(max_length=30,null = True, blank=True)
    father_name = models.CharField(max_length=100, null = True, blank=True)#full_namei.e customuser retrieve from this is placed in father name
    father_phone = models.CharField(max_length=30,null = True, blank=True)
    mother_name = models.CharField(max_length=100,null = True, blank=True)
    mother_phone = models.CharField(max_length=30,null = True, blank=True)
    local_guardian_name = models.CharField(max_length=100,null = True, blank=True)
    local_guardian_phone = models.CharField(max_length=30,null = True, blank=True)
    local_guardian_relation=models.CharField(max_length=30,null = True, blank=True)
    local_guardian_email=models.CharField(max_length=100,null = True, blank=True)
    
    # ------other extra field 
    father_profession = models.CharField(max_length=255,null = True, blank=True)
    father_email = models.EmailField(null=True, blank=True)
    father_profession = models.CharField(max_length=255,null = True, blank=True)
    father_office = models.CharField(max_length = 100, null=True, blank=True)
    mother_profession = models.CharField(max_length=255,null = True, blank=True)
    mother_email = models.EmailField(null=True, blank=True)
    mother_office = models.CharField(max_length = 100, null=True, blank=True)
    address = models.CharField(max_length=255,null = True, blank=True)
    image = models.ImageField(upload_to='parent_images', null=True, blank=True)
    status = models.BooleanField(default=True)
    parent_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_Parent'
        verbose_name = _("parent")
        verbose_name_plural = _("parents")
        
        permissions = (
            ("view_parent_profile", "Can View  Profile"),
            ("add_parent_document", "Can Add Document"),
            ("edit_parent_document", "Can Edit Document"), 
            ("delete_parent_document", "Can Delete Document"),
         
        )

    # def __str__(self):
    #     return self.parent_user.full_name
class SessionYear(models.Model):
    session_start_year = models.DateField()
    session_end_year = models.DateField()

    class Meta:
        db_table = 'tbl_Sessionyear'

    def __str__(self):

        return f'{str(self.session_start_year)} To {str(self.session_end_year)}'

class Training(models.Model):
    title=models.CharField(max_length=255)
    institution=models.CharField(max_length=255)
    duration_from=models.DateField()
    duration_to=models.DateField(blank=True,null=True)
    certificate=models.FileField(upload_to='training_certificates', null=True, blank=True)

class EducationHistory(models.Model):
    degree=models.CharField(max_length=255)
    board=models.CharField(max_length=255)
    grade=models.CharField(max_length=5)
    cgpa=models.CharField(max_length=5)
    year_enrollment=models.DateField()
    year_completion=models.DateField(blank=True,null=True)
    certificate_completion=models.FileField(upload_to='certificate_of_completion', null=True, blank=True)
    transcript=models.FileField(upload_to='transcript', null=True, blank=True)

class EmploymentHistory(models.Model):
    institution=models.CharField(max_length=255)
    position=models.CharField(max_length=255)
    responsibilities=models.CharField(max_length=255)
    duration_from=models.DateField()
    duration_to=models.DateField(blank=True,null=True)

class ResearchAndConsultancy(models.Model):
    ROLE = (
        ('Team Leader','Team Leader'),
        ('Thematic Expert','Thematic Expert'),
        ('Research Analyst', 'Research Analyst'),
        ('Field Supervisor', 'Field Supervisor'),
        ('Researcher','Researcher')
    ) 
    project_title=models.CharField(max_length=255)
    institution=models.CharField(max_length=255)
    role=models.CharField(default='Researcher', choices=ROLE, max_length=50)
    duration_from=models.DateField()
    duration_to=models.DateField(blank=True,null=True)

class GraduateResearchSupervision(models.Model):
    POSITION = (
        ('Supervisor','Supervisor'),
        ('Co-Supervisor','Co-Supervisor'),
        ('Internal Examiner', 'Internal Examiner'),
        ('External Examiner', 'External Examiner')
    ) 
    name=models.CharField(max_length=255)
    title=models.CharField(max_length=255)
    degree=models.CharField(max_length=255)
    position=models.CharField(choices=POSITION, max_length=50,null=True,blank=True)
    university=models.CharField(max_length=255)
    date_start=models.DateField()
    date_end=models.DateField(blank=True,null=True)
    doi=models.URLField(max_length=255,null=True,blank=True)

class GraduateProjectSupervision(models.Model): 
    POSITION = (
        ('Supervisor','Supervisor'),
        ('Co-Supervisor','Co-Supervisor'),
        ('Internal Examiner', 'Internal Examiner'),
        ('External Examiner', 'External Examiner')
    ) 
    name=models.CharField(max_length=255)
    title=models.CharField(max_length=255)
    degree=models.CharField(max_length=255)
    position=models.CharField(choices=POSITION, max_length=50,null=True,blank=True)
    date_start=models.DateField()
    date_end=models.DateField(blank=True,null=True)
    doi=models.URLField(max_length=255,null=True,blank=True)

class WorkshopSeminarConference(models.Model):
    TYPE=(
        ("Workshop","Workshop"),
        ("Seminar","seminar"),
        ("Conference","Conference")
    )
    ROLE = (
        ('Keynote Speaker','Keynote Speaker'),
        ('Speaker','Speaker'),
        ('Panelist', 'Panelist'),
        ('Presenter', 'Presenter'),
        ('Organizer', 'Organizer'),
        ('Participant','Participant')
    )
    title=models.CharField(max_length=255)
    type=models.CharField(choices=TYPE, max_length=50,default="Workshop")
    host=models.CharField(max_length=255)
    role=models.CharField(choices=ROLE, max_length=50,null=True,blank=True)

class FellowshipAwardsStudyvisit(models.Model):
    LEVEL=(
        ("National","National"),
        ("International","International")
    )
    title=models.CharField(max_length=255)
    level=models.CharField(choices=LEVEL, max_length=50,default="National")
    date=models.DateField()
    doi=models.URLField(max_length=255,null=True,blank=True)

class PublicationAndCopyrights(models.Model):
    TYPE=(
        ("Textbook","Textbook"),
        ("Reference Book","Reference Book"),
        ("Journal Article","Journal Article"),
        ("Other Periodicals","Other Periodicals")
    )
    AUTHORSHIP=(
        ("Single","Single"),
        ("Co-Author","Co-Author"),
        ("Editor","Editor")
    )
    LEVEL=(
        ("National","National"),
        ("International","International")
    )
    NATURE=(
        ("Factor Rated","Factor Rated"),
        ("Quality Rated","Quality Rated"),
        ("Blind Reviewed","Blind Reviewed")
    )

    title=models.CharField(max_length=255)
    type_of_work=models.CharField(choices=TYPE, max_length=50,default="Textbook")
    publisher=models.CharField(max_length=255)
    authorship=models.CharField(choices=AUTHORSHIP, max_length=50,default="Single")
    type_of_publication=models.CharField(choices=LEVEL, max_length=50,default="National")
    nature_of_publication=models.CharField(choices=NATURE, max_length=50,default="Factor Rated")
    date=models.DateField(null=True,blank=True)
    doi=models.URLField(max_length=255,null=True,blank=True)


class AdminUser(models.Model):
    # linking main auth model to admin which assists to relate to admin table with its id.Do same for staffs and students
    admin_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, choices=gender_choice, default='Male', blank=True)
    religion = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    join_date = models.DateField(null=True,blank = True)
    image = models.ImageField(upload_to='admin_images', null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_Adminuser'
        verbose_name = _("adminuser")
        verbose_name_plural = _("adminusers")
        permissions = (
            ("view_admin_profile", "Can View Profile"),
            ("add_admin_document", "Can Add Document"),
            ("edit_admin_document", "Can Edit Document"), 
            ("delete_admin_document", "Can Delete Document"),
         
        )
        

    def __str__(self):
        return self.admin_user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at',)


class Student(models.Model):
    blood_group_choices = (
        ('', 'Select Blood Group'), ('A+', 'A+'), ('A-',
                                                   'A-'), ('B+', 'B+'),  ('B-', 'B-'),
        ('O+', 'O+'),  ('O-', 'O-'), ('AB+', 'AB+'),  ('AB-', 'AB-'),
    )
    shift = (
        ('Morning','Morning'),
          ('Day','Day')
    )
    status_choices = (
        ('Running','Running'),('In Active','In Active')
    )

    sn=models.IntegerField(default=1)
    join_year = models.CharField(_('Join Year'),max_length = 50, default=datetime.datetime.now().year, null = True,blank = True)#this is same as batch
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True)
    campus=models.ForeignKey(Campus,on_delete=models.CASCADE) 
    nationality=models.CharField(max_length=100,default='Nepali')            #mu regd number
    institution = models.CharField(max_length=255, blank=True)                                                  #
    first_name = models.CharField("First Name",max_length=50, blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    student_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null = True, blank = True)
    gender = models.CharField(max_length=20, choices=gender_choice,null = True, default='Male')

    school = models.ForeignKey(School,on_delete=models.CASCADE)              
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True )
    semester = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50,choices = status_choices, null=True, blank=True)

    contact = models.CharField(max_length=30, blank=True)
    guardian = models.ForeignKey(Parent, on_delete=models.DO_NOTHING,null=True, blank=True)

    permanent_province = models.CharField(max_length=100,null=True, blank=True)                                        
    permanent_district = models.CharField(max_length=100,null=True, blank=True)
    permanent_municipality = models.CharField(max_length=100,null=True, blank=True)
    permanent_ward_no = models.CharField(max_length=100,null=True, blank=True)
    permanent_street_name = models.CharField(max_length=100,null=True, blank=True)
    permanent_house_no = models.CharField(max_length=100,null=True, blank=True)

    temporary_province = models.CharField(max_length=100,null=True, blank=True)                                        
    temporary_district = models.CharField(max_length=100,null=True, blank=True)
    temporary_municipality = models.CharField(max_length=100,null=True, blank=True)
    temporary_ward_no = models.CharField(max_length=100,null=True, blank=True)
    temporary_street_name = models.CharField(max_length=100,null=True, blank=True)
    temporary_house_no = models.CharField(max_length=100,null=True, blank=True)


    ethnicity = models.CharField(max_length=255, null=True, blank=True)
    citizenship_number=models.CharField(max_length=255, null=True, blank=True)
    passport_number=models.CharField(max_length=255, null=True, blank=True)
    passport_expiry=models.DateField(null=True,blank=True)
    scholarship_status = models.CharField(max_length=50, null=True, blank=True)
    sponshorship_status = models.CharField(max_length=50, null=True, blank=True)
    martyr_lineage = models.BooleanField(default=False, null=True, blank=True)
    disability_status = models.CharField(max_length=25, null=True, blank=True)
    
    education_history = models.ManyToManyField(EducationHistory, blank=True)

    dob = models.DateField(null=True, blank=True)
    dob_ad=models.DateField(null=True,blank=True)
    blood_group = models.CharField(max_length=25, choices=blood_group_choices, blank=True)
    image = models.ImageField( upload_to='student_images', null=True, blank=True)
    qr_code = models.ImageField( upload_to='student_Qrcodes/', blank=True, null=True)
    country = models.CharField(max_length=60, blank=True, null=True)
    
    # ---------------------------------------------extra field--------------------------------------------------------

    register_no = models.CharField(max_length=250, unique=True, null=True,blank=True)               #need to confirm
    religion = models.CharField(max_length=100,null=True, blank=True)
    remarks = models.CharField(max_length=255,null=True, blank=True)
    state = models.CharField(max_length=255,null=True, blank=True)                                  #need to confirm
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
       
    class Meta:
        # ordering = ('student_user__full_name',)
        db_table = 'tbl_Student'
        verbose_name = _("student")
        verbose_name_plural = _("students")
        
        permissions = (
            ("view_student_profile", "Can View Profile"),
            ("add_student_document", "Can Add Document"),
            ("edit_student_document", "Can Edit Document"), 
            ("delete_student_document", "Can Delete Document"),
             ("print_student_id_card", "Can Print Id Card"),
            ("student_bulk_upload", "Can Upload Bulk Student Data"),
         
        )

        ordering = ('-created_at',)

    def __str__(self):
        return (self.first_name +' ' + self.middle_name + ' '+self.last_name)
    

    
    # def student_barcode(self,first_place,  *args, **kwargs):
    #     COD128 = barcode.get_barcode_class('code128')
    #     rv = BytesIO()
    #     code = COD128(f'{first_place}{self.stu_id}', writer=ImageWriter()).write(rv)
    #     barcode.base.Barcode.default_writer_options['write_text'] = False# this line remove footer text or number
    #     self.barcode.save(f'{self.stu_id}.png',File(rv), save=False)
    #     return super().save(*args, **kwargs)
    
    
    # def save(self, *args, **kwargs):          # overriding save() 
    #     # -- for placing digits number in barcode-----------
    #     student_id = f'{self.stu_id}'
        
    #     if(len(student_id) == 1):
    #         first_place = '000000'
    #         self.student_barcode(first_place)
            
    #     elif len(student_id) == 2:
    #         first_place = '00000'
    #         self.student_barcode(first_place)
            
    #     elif len(student_id) == 3:
    #         first_place = '0000'
    #         self.student_barcode(first_place)
            
    #     elif len(student_id) == 4:
    #         first_place = '000'
    #         self.student_barcode(first_place)
            
    #     elif len(student_id) == 5:
    #         first_place = '00'
    #         self.student_barcode(first_place)
            
    #     elif len(student_id) == 6:
    #         first_place = '0'
    #         self.student_barcode(first_place)
            
    #     elif len(student_id) == 7:
    #         first_place = ''
    #         self.student_barcode(first_place)
            
    #     # --

    
class Staff(models.Model): 
    EMPLOYMENT_TYPE = (
        ('Permanent','Permanent'),
        ('Contract','Contract'),
        ('Monthly Wages', 'Monthly Wages'),
        ('Daily Wages', 'Daily Wages')
    ) 
    mu_id = models.CharField(max_length=100,unique=True)  
    employment_type = models.CharField(default='Permanent', choices=EMPLOYMENT_TYPE, max_length=20)
    # employment_id = models.CharField(max_length=50, blank=True)
    staff_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    nationality=models.CharField(max_length=100,default='Nepali')
    contact = models.CharField(max_length=30)
    dob = models.DateField(null=True, blank=True)
    dob_ad=models.DateField(null=True, blank=True)
    citizenship_number=models.CharField(max_length=255, null=True, blank=True)
    passport_number=models.CharField(max_length=255, null=True, blank=True)
    passport_expiry=models.DateField(null=True,blank=True)
    gender = models.CharField( max_length=20, choices=gender_choice, default='Male')
    join_date = models.DateField(null=True,blank = True)
    position_joining_section=models.CharField(max_length=100,null=True, blank=True)
    position_joining_classification=models.CharField(max_length=100,null=True, blank=True)
    position_current_section=models.CharField(max_length=100,null=True, blank=True)
    position_current_classification=models.CharField(max_length=100,null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)


    permanent_province = models.CharField(max_length=100,null=True, blank=True)                                        
    permanent_district = models.CharField(max_length=100,null=True, blank=True)
    permanent_municipality = models.CharField(max_length=100,null=True, blank=True)
    permanent_ward_no = models.CharField(max_length=100,null=True, blank=True)
    permanent_street_name = models.CharField(max_length=100,null=True, blank=True)
    permanent_house_no = models.CharField(max_length=100,null=True, blank=True)

    temporary_province = models.CharField(max_length=100,null=True, blank=True)                                        
    temporary_district = models.CharField(max_length=100,null=True, blank=True)
    temporary_municipality = models.CharField(max_length=100,null=True, blank=True)
    temporary_ward_no = models.CharField(max_length=100,null=True, blank=True)
    temporary_street_name = models.CharField(max_length=100,null=True, blank=True)
    temporary_house_no = models.CharField(max_length=100,null=True, blank=True)

    guardian = models.ForeignKey(Parent, on_delete=models.DO_NOTHING,null=True, blank=True)

    present_status=models.CharField(max_length=100,null=True, blank=True)

    education_history = models.ManyToManyField(EducationHistory, blank=True)
    employment_history = models.ManyToManyField(EmploymentHistory, blank=True)
    training = models.ManyToManyField(Training, blank=True)
    

    school=models.ForeignKey(School,blank=True,null=True,on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    
    language = models.CharField(max_length=255, null=True, blank=True)
    social_media = models.JSONField(null=True, blank=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'tbl_Staff'
        verbose_name = _("staff")
        verbose_name_plural = _("staffs")
        
        permissions = (
            ("view_staff_profile", "Can View Profile"),
            ("add_staff_document", "Can Add Document"),
            ("edit_staffr_document", "Can Edit Document"), 
            ("delete_staff_document", "Can Delete Document"),
         
        )
        verbose_name = 'Staff'

    def __str__(self):
        return (self.first_name +' ' + self.middle_name + ' '+self.last_name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    # def get_subjects(self):
    #     customuser_teacher = CustomUser.objects.filter(user_type = Group.objects.get(name = 'Teacher')).get(id = teacher_id)
    #     subjects = customuser_teacher.subject_set.all()
    #     return subjects

    class Meta:
        ordering = ('-created_at',)


class Teacher(models.Model):
    EMPLOYMENT_TYPE = (
        ('Permanent','Permanent'),
        ('Contract','Contract'),
        ('Part Time', 'Part Time'),
    ) 
    PROFESSIONAL_STATUS=(
        ("Professor","Professor"),
        ("Associate Professor","Associate Professor"),
        ("Teaching Assistant/Instructor","Teaching Assistant/Instructor")
    )
    mu_id = models.CharField(max_length=100,unique=True)  
    employment_type = models.CharField(default='Permanent', choices=EMPLOYMENT_TYPE, max_length=20)
    image = models.ImageField(null=True, blank=True)
    # employment_id = models.CharField(max_length=50, blank=True)
    faculty_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    nationality=models.CharField(max_length=100,default='Nepali')
    contact = models.CharField(max_length=30)
    dob = models.DateField(null=True, blank=True)
    dob_ad=models.DateField(null=True, blank=True)
    citizenship_number=models.CharField(max_length=255, null=True, blank=True)
    passport_number=models.CharField(max_length=255, null=True, blank=True)
    passport_expiry=models.DateField(null=True,blank=True)
    gender = models.CharField( max_length=20, choices=gender_choice, default='Male')
    join_date = models.DateField(null=True,blank = True)
    position_joining_section=models.CharField(max_length=100,null=True, blank=True)
    position_joining_classification=models.CharField(max_length=100,null=True, blank=True)
    position_current_section=models.CharField(max_length=100,null=True, blank=True)
    position_current_classification=models.CharField(max_length=100,null=True, blank=True)
    
    permanent_province = models.CharField(max_length=100,null=True, blank=True)                                        
    permanent_district = models.CharField(max_length=100,null=True, blank=True)
    permanent_municipality = models.CharField(max_length=100,null=True, blank=True)
    permanent_ward_no = models.CharField(max_length=100,null=True, blank=True)
    permanent_street_name = models.CharField(max_length=100,null=True, blank=True)
    permanent_house_no = models.CharField(max_length=100,null=True, blank=True)

    temporary_province = models.CharField(max_length=100,null=True, blank=True)                                        
    temporary_district = models.CharField(max_length=100,null=True, blank=True)
    temporary_municipality = models.CharField(max_length=100,null=True, blank=True)
    temporary_ward_no = models.CharField(max_length=100,null=True, blank=True)
    temporary_street_name = models.CharField(max_length=100,null=True, blank=True)
    temporary_house_no = models.CharField(max_length=100,null=True, blank=True)

    guardian = models.ForeignKey(Parent, on_delete=models.DO_NOTHING,null=True, blank=True)

    present_status=models.CharField(max_length=100,null=True, blank=True)

    education_history = models.ManyToManyField(EducationHistory, blank=True)
    employment_history = models.ManyToManyField(EmploymentHistory, blank=True)

    research_and_consultancy=models.ManyToManyField(ResearchAndConsultancy, blank=True)
    graduate_research_supervision=models.ManyToManyField(GraduateResearchSupervision, blank=True)
    graduate_project_supervision=models.ManyToManyField(GraduateProjectSupervision, blank=True)
    workshop_seminar_conference=models.ManyToManyField(WorkshopSeminarConference, blank=True)
    fellowship_awards_studyvisit=models.ManyToManyField(FellowshipAwardsStudyvisit, blank=True)
    publication_and_copyrights=models.ManyToManyField(PublicationAndCopyrights, blank=True)


    institution = models.CharField(max_length=255, blank=True)
    school=models.ForeignKey(School,on_delete=models.CASCADE,null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    professional_status=models.CharField(max_length=255,choices=PROFESSIONAL_STATUS, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    courses = models.ManyToManyField(CourseCategory, max_length=100,blank=True)
    
    language = models.CharField(max_length=255, null=True, blank=True)
    social_media = models.JSONField(null=True, blank=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'tbl_Teacher'
        verbose_name = _("teacher")
        verbose_name_plural = _("teacher")
        
        permissions = (
            ("view_teacher_profile", "Can View Profile"),
            ("add_teacher_document", "Can Add Document"),
            ("edit_teacher_document", "Can Edit Document"), 
            ("delete_teacher_document", "Can Delete Document"),
         
        )
        verbose_name = 'Teacher'

    def __str__(self):
        return (self.first_name +' ' + self.middle_name + ' '+self.last_name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    class Meta:
        ordering = ('-created_at',)
      
class ExtraUser(models.Model):
    mu_id = models.CharField(max_length=100,unique=True)            #mu regd number# this all other user like driver accountant and so on
    extra_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null = True)
    first_name = models.CharField(max_length=50, blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    role = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    dob = models.DateField(null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=gender_choice, default='Male')
    religion = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=30, blank=True)

    permanent_province = models.CharField(max_length=100,null=True, blank=True)                                        
    permanent_district = models.CharField(max_length=100,null=True, blank=True)
    permanent_municipality = models.CharField(max_length=100,null=True, blank=True)
    permanent_ward_no = models.CharField(max_length=100,null=True, blank=True)
    permanent_street_name = models.CharField(max_length=100,null=True, blank=True)
    permanent_house_no = models.CharField(max_length=100,null=True, blank=True)

    temporary_province = models.CharField(max_length=100,null=True, blank=True)                                        
    temporary_district = models.CharField(max_length=100,null=True, blank=True)
    temporary_municipality = models.CharField(max_length=100,null=True, blank=True)
    temporary_ward_no = models.CharField(max_length=100,null=True, blank=True)
    temporary_street_name = models.CharField(max_length=100,null=True, blank=True)
    temporary_house_no = models.CharField(max_length=100,null=True, blank=True)
    
    employment_history = models.TextField(null=True, blank=True)                                          #
    education_history = models.TextField(null=True, blank=True)   
    project_history = models.TextField(null=True, blank=True)                                       #
                                            #
    join_date = models.DateField(null=True)
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_Extrauser'
        verbose_name = _("extrauser")
        verbose_name_plural = _("extrausers")
        permissions = (
            ("view_extrauser_profile", "Can View Profile"),
            ("add_extrauser_document", "Can Add Document"),
            ("edit_extrauser_document", "Can Edit Document"), 
            ("delete_extrauser_document", "Can Delete Document"),   
         
        )

    def __str__(self):
        return (self.first_name +' ' + self.middle_name + ' '+self.last_name)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'ExtraUser'

class Semester(models.Model):

    ALEVEL_CHOICES = [
        ('AS', 'Advanced Subsidiary (AS)'),
        ('AL', 'Advanced Level (AL)'),
        ('PA', 'Passed out')
        ]
    
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    bachelor_semester = models.CharField(_("Semester"),max_length=100,null = True, blank = True)
    master_semester = models.CharField(_("Semester"),max_length=100,null = True, blank = True)
    name = models.CharField(max_length=100, verbose_name="Year")
    semester_value = models.IntegerField(null=True, blank=True)
    level = models.CharField(max_length=20, choices=ALEVEL_CHOICES, default='AS',null = True,blank = True)
    # staff_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null = True, blank = True)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_Semester'
        verbose_name = _("semester")
        verbose_name_plural = _("semesters")


    class Meta:
        ordering = ('-created_at',)

class Subject(models.Model):

    subject_code = models.CharField(max_length=50, primary_key = True)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    # semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    semester = models.IntegerField()
    school = models.ForeignKey(School,on_delete=models.CASCADE)
    
    subject_name = models.CharField(max_length=255)
    course = models.ManyToManyField(Course)
    staff_user = models.ManyToManyField(Staff, through='SubjectTeacher', blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_Subject'
        verbose_name = _("subject")
        verbose_name_plural = _("subjects")
        ordering = ('semester')
        

    def save(self, *args, **kwargs):

        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject_name
    # def __str__(self):
    #     return f'{self.semester} : {self.subject_name} : ' + ' , '.join([str(teacher) for teacher in self.staff_user.all()])
    
    @property
    def get_teachers(self):
        return ', '.join(str(teacher) for teacher in self.staff_user.all())

    class Meta:
        ordering = ('-created_at',)

class Section(models.Model):
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE,null = True, blank=True)
    section_name = models.CharField(max_length=100)
    capacity = models.IntegerField(null = True, blank = True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null = True)
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null = True, blank = True)
    category = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject = models.ManyToManyField(Subject)
    
    class Meta:
        db_table = 'tbl_Section'
        verbose_name = _("section")
        verbose_name_plural = _("sections")
    
    def __str__(self):
        return f'{self.semester} : {self.section_name}'

    class Meta:
        ordering = ('-created_at',)

class SubjectTeacher(models.Model):
    subject = models.ForeignKey(Subject, verbose_name=_("Subject"), on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete = models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # section = models.ForeignKey(Section, on_delete=models.CASCADE,null = True, blank=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields = ['subject', 'section'], name = 'unique_subject_teacher_section')
    #     ]
    
    def __str__(self):
        return f'{self.subject.subject_name}:{self.teacher}'
    
    
class OptionalSubject(models.Model):
    semester = models.IntegerField()
    subject_name = models.CharField(max_length=255)
    subject_code = models.CharField(max_length=50, default='XXX', blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    staff_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_Optionalsubject'
        verbose_name = _("optionalsubject")
        verbose_name_plural = _("optionalsubjects")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject_name



#THis is for student union college union group
class StudentGroup(models.Model):
    name = models.CharField(max_length=250, blank=True,verbose_name = 'Student Union Name', help_text='This is Student  Union GrouP')
    class Meta:
        db_table = 'tbl_Studentgroup'
        verbose_name = _("studentgroup")
        verbose_name_plural = _("studentgroups")

    def __str__(self):
        return self.name
      
    
# def upload_location(instance, filename):
#     filebase, extension = filename.split(".")
#     return f'employee documents / {instance.employee_id} . {instance.employee.first_name} {instance.employee.last_name} / {filename}'
         

class DocumentFile(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='document_files')
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'tbl_Documentfile'
        verbose_name = _("documentfile")
        verbose_name_plural = _("documentfiles")

    def __str__(self):
        return self.title

class Complain(models.Model):
    title = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    description = RichTextField()
    attachment = models.FileField(upload_to='Complain_attachment', blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'tbl_Complain'
        verbose_name = _("complain")
        verbose_name_plural = _("complains")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('-created_at',)


class CertificateTemplate(models.Model):
    theme_choices = (('', 'Choose Template Theme'),
                     ('Theme 1', 'Theme 1'), ('Theme 2', 'Theme 2'))
    title_choices = (
        ('Mr','Mr'),('Mrs','Mrs'),('Miss','Miss'),('Dr','Dr'),('Prof','Prof')
    )
    certificate_number = models.CharField(max_length=50)
    date_of_issue = models.DateField()
    salutations = models.CharField(_("Salutation"), choices = title_choices, max_length=50, null = True, blank = True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    passed_year = models.IntegerField(_('Passed Year'),choices = YEAR_CHOICES,default=datetime.datetime.now().year)
    photo = models.ImageField( upload_to='student_character_certificates_photos', blank=True, null = True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    # -------------------------------extra field --------------------------
    certificate_name = models.CharField(max_length=250)
    theme = models.CharField(max_length=50, choices=theme_choices)
    main_middle_text = RichTextField()
    top_heading_title = RichTextField(blank=True)
    top_heading_left = RichTextField(blank=True)
    top_heading_middle = RichTextField(blank=True)
    top_heading_right = RichTextField(blank=True)
    footer_left_text = RichTextField(blank=True)
    footer_middle_text = RichTextField(blank=True)
    footer_right_text = RichTextField(blank=True)
    background_image = models.ImageField( upload_to='certificate_template_background', blank=True)

    class Meta:
        db_table = 'tbl_Certificatetemplate'
        verbose_name = _("certificatetemplate")
        verbose_name_plural = _("certificatetemplates")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class SocialLink(models.Model):
    role = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    facebook = models.URLField(max_length=200, blank=True)
    twitter = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=200, blank=True)
    google_plus = models.URLField(max_length=200, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    # image = models.ImageField(upload_to = 'user_sociallink_images')

    class Meta:
        db_table = 'tbl_Sociallink'
        verbose_name = _("sociallink")
        verbose_name_plural = _("sociallinks")

 
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class UserRole(models.Model):
    role = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    
    class Meta:
        db_table = 'tbl_Userrole'
        verbose_name = _("userrole")
        verbose_name_plural = _("userroles")

    def __str__(self):
        return self.role
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Awards(models.Model):
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

class awards_recipient(models.Model):
    award = models.ForeignKey(Awards, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    
