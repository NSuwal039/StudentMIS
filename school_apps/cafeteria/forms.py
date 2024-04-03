from .models import *
from django.forms import ModelForm
from django import forms

class IngredientsCreateForm(ModelForm):
    class Meta:
        model=Ingredients
        fields = '__all__'
        exclude = ['category']

class FoodItemCreateForm(ModelForm):
    class Meta:
        model=FoodItem
        fields = '__all__'

class StallCreateForm(ModelForm):
    class Meta:
        model=Stall
        fields = '__all__'
        exclude = ['menu', 'sales']