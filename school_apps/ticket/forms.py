from django import forms
from .models import Department, Form, Ticket
from student_management_app.models import CustomUser

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

    members = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
    )

class FormForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = '__all__'

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'            

