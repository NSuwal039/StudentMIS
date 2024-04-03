from django.db.models import fields
from rest_framework import serializers
from ..models import *
from django_countries.fields import CountryField
from django.contrib.auth.models import Permission, Group
# from school_apps.lms.models import BookIssue
# from school_apps.lms.serializers import BookIssueSerializer
from school_apps.events.models import *

from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from student_management_system.config import *
import threading
from django.db import transaction
# from school_apps.events.api.serializers import EventSerializer

# class EducationHistoryListSerializer(serializers.ListSerializer):
#     def update(self, instance, validated_data):
#         try:
#             for x in validated_data:
#                 try:
#                     id=x["id"]
#                 except:
#                     id=0
#                 if EducationHistory.objects.filter(id=id).exists():
#                     t=EducationHistory.objects.get(id=id)
#                     t.degree=x.get('degree',t.degree)
#                     t.board=x.get('board',t.board)
#                     t.grade=x.get('grade',t.grade)
#                     t.cgpa=x.get('cgpa',t.cgpa)
#                     t.year_enrollment=x.get('year_enrollment',t.year_enrollment)
#                     t.year_completion=x.get('year_completion',t.year_completion)
#                     t.certificate_completion=x.get('certificate_completion',t.certificate_completion)
#                     t.transcript=x.get('transcript',t.transcript)
#                     t.save()
#                 else:
#                     obj=EducationHistory.objects.create(**x)
#                     obj_queryset=EducationHistory.objects.filter(id=obj.id)
#                     instance=instance.union(obj_queryset)
#             return instance
#         except:
#             raise NotImplementedError(
#                 "Serializers with many=True do not support multiple update by "
#                 "default, only multiple create. For updates it is unclear how to "
#                 "deal with insertions and deletions. If you need to support "
#                 "multiple update, use a `ListSerializer` class and override "
#                 "`.update()` so you can specify the behavior exactly."
#             )

class NoneSerializer(serializers.Serializer):
    class Meta:
        fields=None
class CommonListSerializer(serializers.ListSerializer):

    def update_logic(self,instance,validated_data):
        for x in validated_data: #Loop for multiple objects
            try:
                id=x["id"]
            except:
                id=0
            if instance.model.objects.filter(id=id).exists(): # if object id is present then update
                t=instance.model.objects.get(id=id)
                for y in instance.model._meta.fields: #loop to get all the fields in the given model
                    if y.name in x: # check field if present/not_present in validated_data
                        t.__dict__[y.name]=x.get(y.name,y)
                    # else:
                    #     t.__dict__[y.name]=''
                t.save()
            else:# if not present then create a new instance
                obj=instance.model.objects.create(**x)
                obj_queryset=instance.model.objects.filter(id=obj.id)
                instance=instance.union(obj_queryset)#instance is done union to its queryset later which is added on m2m field list in viewset
        return instance

    @transaction.atomic #For Atomicity
    def update(self, instance, validated_data):
        # A Custom List Serialzier made to handle m2m update for Staff/Student/Faculty of our system
        try:
            ins=self.update_logic(instance,validated_data)
            return ins
        except:
            raise NotImplementedError(
                "Serializers with many=True do not support multiple update by "
                "default, only multiple create. For updates it is unclear how to "
                "deal with insertions and deletions. If you need to support "
                "multiple update, use a `ListSerializer` class and override "
                "`.update()` so you can specify the behavior exactly."
            )

class TrainingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    certificate_url=serializers.SerializerMethodField()
    class Meta:
        model=Training
        fields = '__all__'
        list_serializer_class=CommonListSerializer
    
    def get_certificate_url(self, obj):
        # import pdb;pdb.set_trace()
        try:
            certificate_url = obj.certificate.url
            return f'{PROTOCOL}{SITE}{certificate_url}'
        except:
            return None

class EducationHistorySerializer(serializers.ModelSerializer):
    transcript_url=serializers.SerializerMethodField(read_only=True)
    certificate_completion_url=serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(required=False)
    class Meta:
        model=EducationHistory
        fields = '__all__'
        list_serializer_class=CommonListSerializer
    
    def get_transcript_url(self, obj):
        # request = self.context.get('request')
        try:
            transcript_url = obj.transcript.url
            return f'{PROTOCOL}{SITE}{transcript_url}'
            # return request.build_absolute_uri(transcript_url)
        except:
            return None 

    def get_certificate_completion_url(self, obj):
        # import pdb;pdb.set_trace()
        try:
            certificate_completion_url = obj.certificate_completion.url
            return f'{PROTOCOL}{SITE}{certificate_completion_url}'
        except:
            return None   

class EmploymentHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=EmploymentHistory
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class ResearchAndConsultancySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=ResearchAndConsultancy
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class GraduateResearchSupervisionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=GraduateResearchSupervision
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class GraduateProjectSupervisionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=GraduateProjectSupervision
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class WorkshopSeminarConferenceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=WorkshopSeminarConference
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class FellowshipAwardsStudyvisitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=FellowshipAwardsStudyvisit
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class PublicationAndCopyrightsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model=PublicationAndCopyrights
        fields = '__all__'
        list_serializer_class=CommonListSerializer

class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Campus
        fields = '__all__'
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model=School
        fields = '__all__'
class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=CourseCategory
        fields = '__all__'
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Course
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Department
        fields = '__all__'

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Batch
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Branch
        fields = '__all__'
   
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','username', 'email',
              'is_active', 'is_staff', 'is_superuser', 'password', 'full_name')   #needs to fix bookissue error
        
        # fields = ('username', 'email',
        #       'is_active', 'is_staff', 'is_superuser', 'password', 'full_name')

        # These fields are displayed but not editable and have to be a part of 'fields' tuple
        read_only_fields = ('is_active', 'is_staff', 'is_superuser',)

        # These fields are only editable (not displayed) and have to be a part of 'fields' tuple
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}

    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    guardian=serializers.SerializerMethodField()
    education_history = serializers.SerializerMethodField()
    batch=serializers.SerializerMethodField()
    campus=serializers.SerializerMethodField()
    school=serializers.SerializerMethodField()
    course_category=serializers.SerializerMethodField()
    class Meta:
        model=Student
        fields = '__all__'
    
    def get_campus(self, obj):
        campus = obj.campus
        return CampusSerializer(campus).data
    
    def get_school(self,obj):
        school=obj.school
        return SchoolSerializer(school).data
    
    def get_course_category(self,obj):
        course_category=obj.course_category
        return CourseCategorySerializer(course_category).data
    
    def get_batch(self, obj):
        batch = obj.batch
        return BatchSerializer(batch).data
    
    def get_guardian(self, obj):
        parent = obj.guardian
        return ParentSerializer(parent).data

    def get_user(self, obj):
        user = obj.student_user
        return CustomUserSerializer(user).data
    
    def get_course(self, obj):
        user = obj.course
        return CourseSerializer(user).data
    
    def get_education_history(self,obj):
        education = obj.education_history
        return EducationHistorySerializer(education,many=True).data


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=AdminUser
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    # full_name = serializers.ReadOnlyField(source = 'staff_user.full_name')
    user = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    training=serializers.SerializerMethodField()
    guardian=serializers.SerializerMethodField()
    education_history=serializers.SerializerMethodField()
    employment_history=serializers.SerializerMethodField()
    branch=serializers.SerializerMethodField()
    school=serializers.SerializerMethodField()

    class Meta:
        model=Staff
        fields = '__all__'

    def get_training(self, obj):
        training = obj.training
        return TrainingSerializer(training,many=True).data
    
    def get_education_history(self, obj):
        education = obj.education_history
        return EducationHistorySerializer(education,many=True).data
    
    def get_employment_history(self, obj):
        employment = obj.employment_history
        return EmploymentHistorySerializer(employment,many=True).data
    
    def get_user(self, obj):
        user = obj.staff_user
        return CustomUserSerializer(user).data
    
    def get_department(self, obj):
        department=obj.department
        return DepartmentSerializer(department).data
    
    def get_guardian(self, obj):
        guardian=obj.guardian
        return ParentSerializer(guardian).data
    
    def get_branch(self, obj):
        branch=obj.branch
        return BranchSerializer(branch).data
    
    def get_school(self, obj):
        school=obj.school
        return SchoolSerializer(school).data

class TeacherSerializer(serializers.ModelSerializer):
    # full_name = serializers.ReadOnlyField(source = 'staff_user.full_name')
    user = serializers.SerializerMethodField()
    guardian = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school=serializers.SerializerMethodField()
    branch=serializers.SerializerMethodField()

    education_history=serializers.SerializerMethodField()
    employment_history=serializers.SerializerMethodField()

    research_and_consultancy=serializers.SerializerMethodField()
    graduate_research_supervision=serializers.SerializerMethodField()
    graduate_project_supervision=serializers.SerializerMethodField()
    workshop_seminar_conference=serializers.SerializerMethodField()
    fellowship_awards_studyvisit=serializers.SerializerMethodField()
    publication_and_copyrights=serializers.SerializerMethodField()

    class Meta:
        model=Teacher
        fields = '__all__'
  
    def get_education_history(self, obj):
        education = obj.education_history
        return EducationHistorySerializer(education,many=True).data
    
    def get_employment_history(self, obj):
        employment = obj.employment_history
        return EmploymentHistorySerializer(employment,many=True).data
    
    def get_user(self, obj):
        user = obj.faculty_user
        return CustomUserSerializer(user).data
    
    def get_guardian(self, obj):
        parent = obj.guardian
        return ParentSerializer(parent).data
    
    def get_department(self, obj):
        department=obj.department
        return DepartmentSerializer(department).data
    
    def get_school(self, obj):
        school=obj.school
        return SchoolSerializer(school).data
    
    def get_branch(self, obj):
        branch=obj.branch
        return BranchSerializer(branch).data
    
    def get_research_and_consultancy(self, obj):
        research_and_consultancy = obj.research_and_consultancy
        return ResearchAndConsultancySerializer(research_and_consultancy,many=True).data
    
    def get_graduate_research_supervision(self, obj):
        graduate_research_supervision = obj.graduate_research_supervision
        return GraduateResearchSupervisionSerializer(graduate_research_supervision,many=True).data
    
    def get_graduate_project_supervision(self, obj):
        graduate_project_supervision = obj.graduate_project_supervision
        return GraduateProjectSupervisionSerializer(graduate_project_supervision,many=True).data
    
    def get_workshop_seminar_conference(self, obj):
        workshop_seminar_conference = obj.workshop_seminar_conference
        return WorkshopSeminarConferenceSerializer(workshop_seminar_conference,many=True).data
    
    def get_fellowship_awards_studyvisit(self, obj):
        fellowship_awards_studyvisit = obj.fellowship_awards_studyvisit
        return FellowshipAwardsStudyvisitSerializer(fellowship_awards_studyvisit,many=True).data
    
    def get_publication_and_copyrights(self, obj):
        publication_and_copyrights = obj.publication_and_copyrights
        return PublicationAndCopyrightsSerializer(publication_and_copyrights,many=True).data
    
    
class ExtraUserSerializer(serializers.ModelSerializer):
    # full_name = serializers.ReadOnlyField(source = 'extra_user.full_name')
    user = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    class Meta:
        model=ExtraUser
        fields = '__all__'
    
    def get_user(self, obj):
        user = obj.extra_user
        return CustomUserSerializer(user).data

    def get_branch(self, obj):
        branch=obj.branch
        return BranchSerializer(branch).data

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Semester
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    class Meta:
        model=Subject
        fields = '__all__'
    
    def get_course(self, obj):
        return (CourseSerializer(obj.course.all(), many=True).data)

class SectionSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()
    class Meta:
        model=Section
        fields = '__all__'
    
    def get_semester(self, obj):
        semester = obj.semester
        return(SemesterSerializer(semester).data)

class SubjectTeacherSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()

    class Meta:
        model=SubjectTeacher
        fields = '__all__'
    
    def get_subject(self, obj):
        return SubjectSerializer(obj.subject).data

    def get_teacher(self, obj):
        return StaffSerializer(obj.teacher).data

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Parent
        fields = '__all__'

class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudentGroup
        fields = '__all__'

class DocumentFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    class Meta:
        model=DocumentFile
        fields = '__all__'
    
    def get_file(self, obj):
        request = self.context.get('request')
        photo_url = obj.file.url
        return request.build_absolute_uri(photo_url)


class ComplainSerializer(serializers.ModelSerializer):
    class Meta:
        model=Complain
        fields = '__all__'

class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CertificateTemplate
        fields = '__all__'

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model=SocialLink
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserRole
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    permission = serializers.SerializerMethodField()
    class Meta:
        model = Permission
        fields = '__all__'

    def get_permission(self, obj):
        return obj.content_type.app_label+'.'+obj.codename

class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = '__all__'
    
    def get_permissions(self,obj):
        permissions_list=obj.permissions.all()
        return PermissionSerializer(permissions_list,many=True).data

class AwardsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Awards
        fields = '__all__'

class awards_recipientSerializer(serializers.ModelSerializer):
    class Meta:
        model=awards_recipient
        fields = '__all__'
    
class SessionYearSerializer(serializers.ModelSerializer):
    class Meta:
        model=SessionYear
        fields = '__all__'


