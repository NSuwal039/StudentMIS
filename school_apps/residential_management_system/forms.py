from .models import RoomType, Room, RoomPicture, Expense, Booking, Review
from django import forms
from student_management_app.models import CustomUser

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = '__all__'

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

class RoomPictureForm(forms.ModelForm):
    class Meta:
        model = RoomPicture
        fields = '__all__'

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'               

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        widgets = {
            'booking_start' : forms.DateTimeInput(format=('%m/%d/%Y %H:%M'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'datetime-local'}),
            'booking_end' : forms.DateTimeInput(format=('%m/%d/%Y %H:%M'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'datetime-local'})
        }
        fields = '__all__'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'        