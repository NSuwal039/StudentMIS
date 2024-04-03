from datetime import date
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import related
from student_management_app.models import *
from school_apps.inventory.models import Category

# Create your models here.

class Ingredients(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    amount = models.FloatField()
    restock_at = models.FloatField()

class FoodItem(models.Model):
    name = models.CharField(max_length=255)

class Menu(models.Model):
    # stall = models.ForeignKey(Stall, on_delete=models.CASCADE, related_name="menu_stall")
    menu_items = models.ManyToManyField(FoodItem, through='menu_items')

class Stall(models.Model):
    stall_id = models.CharField(max_length=255, unique=True)
    ingredients = models.ManyToManyField(Ingredients, through='stall_ingredients_item')
    # menu = models.ManyToManyField(FoodItem)
    menu =models.OneToOneField(Menu, on_delete=models.CASCADE, null=True)
    sales = models.ManyToManyField(CustomUser, through='sales')

# class Menu(models.Model):
#     stall = models.ForeignKey(Stall, on_delete=models.CASCADE, related_name="menu_stall")
#     menu_items = models.ManyToManyField(FoodItem, through='menu_items')

class menu_items(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_menu', null=True)
    item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='menu_fooditem')
    price = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def clean(self):
        super(menu_items, self).clean()
        price = self.price

        if price <0:
            raise ValidationError('Price cannot be negative.')
        return super().clean()

class Sales(models.Model): #needs changing
    stall = models.ForeignKey(Stall, on_delete=models.CASCADE, related_name="sales_stall")
    item = models.ManyToManyField(menu_items, through='sales_item')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    total = models.FloatField()

class sales_item(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE)
    item = models.ForeignKey(menu_items, on_delete=models.CASCADE, related_name='sales_item')
    amount = models.IntegerField()
    total = models.FloatField()

# class IngredientAssignment(models.Model): #needs changing
#     stall = models.ForeignKey(Stall, on_delete=models.CASCADE, related_name="ingredients_stall")
#     ingredient = models.ManyToManyField(Ingredients)
#     date = models.DateField(auto_now_add=True)

class stall_ingredients_item(models.Model):
    stall = models.ForeignKey(Stall, on_delete=models.CASCADE)
    ingredient =models.ForeignKey(Ingredients, on_delete=models.CASCADE, related_name='assignment_ingredient')
    amount = models.FloatField()



class CafeteriaStaff(models.Model):      #do not use
    extra_user = models.ForeignKey(ExtraUser, on_delete=models.CASCADE)
    stall = models.ForeignKey(Stall, on_delete=models.CASCADE, null=True)