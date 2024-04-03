from django import forms
from student_management_app.models import Student,Section,Semester,CourseCategory
from django.shortcuts import get_object_or_404

class StudentForm(forms.ModelForm):
    # guardian = forms.ModelChoiceField(required=True, label='Parent Name',
    #                                   empty_label="-----Please Select Your Parent Name----- ", queryset=Parent.objects.all())
    # section = forms.ModelChoiceField(
    #     empty_label="Select Section ", queryset=Section.objects.all())
    dob = forms.DateField(label='Date of Birth', widget=forms.DateInput(
        attrs={'type': 'date', "class": "form-control"}))
    stu_id = forms.CharField(label='Student Id', widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": " Enter Student Id", }))
   
    temporary_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": " Enter Temporary Address", }))
    
    permanent_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": " Enter permanent Address", }))
    contact = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": " Enter Student Mobile Number", }))
    # roll_no = forms.CharField(required=False, widget=forms.TextInput(
    #     attrs={"placeholder": " Enter Roll No", }))

    # semester = forms.ModelChoiceField(
    #     label='Class', empty_label="Select Class ", queryset=Semester.objects.all())
# ----------
 
    class Meta:
        model = Student
        fields = (
            'join_year','stu_id','gender','contact',
            'permanent_address','temporary_address','dob','blood_group','image',
        )
    def __init__(self, *args, user = None, **kwargs):
        super().__init__(*args, **kwargs)
        # a_level_course_category = get_object_or_404(CourseCategory,course_name = 'A-Level')
        bachelor_course_category = get_object_or_404(CourseCategory,course_name = 'Bachelor')
        master_course_category = get_object_or_404(CourseCategory,course_name = 'Master')
        
        # if user.adminuser.course_category == a_level_course_category:
        #     semester = self.fields['semester']
        #     semester.queryset = semester.queryset.filter(course_category = a_level_course_category)
        #     section = self.fields['section']
        #     section.queryset = section.queryset.filter(course_category = a_level_course_category)
            
        # if user.adminuser.course_category == bachelor_course_category:
        #     semester = self.fields['semester']
        #     semester.queryset = semester.queryset.filter(course_category = bachelor_course_category)
            # section = self.fields['section']
            # section.queryset = section.queryset.filter(course_category = bachelor_course_category)
            
        # if user.adminuser.course_category == master_course_category:
        #     semester = self.fields['semester']
        #     semester.queryset = semester.queryset.filter(course_category = master_course_category)
            # section = self.fields['section']
            # section.queryset = section.queryset.filter(course_category = master_course_category)