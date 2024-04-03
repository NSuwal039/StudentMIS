from django.db.models import fields
from rest_framework import serializers

from ..models import *

class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ingredients
        fields = '__all__'

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=FoodItem
        fields = '__all__'

class StallSerializer(serializers.ModelSerializer):
    class Meta:
        model=Stall
        fields = '__all__'

class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Sales
        fields = '__all__'

class sales_itemSerializer(serializers.ModelSerializer):
    class Meta:
        model=sales_item
        fields = '__all__'

# class IngredientAssignmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=IngredientAssignment
#         fields = '__all__'

class stall_ingredients_itemSerializer(serializers.ModelSerializer):
    class Meta:
        model=stall_ingredients_item
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model=Menu
        fields = '__all__'

class menu_itemsSerializer(serializers.ModelSerializer):
    menu = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=menu_items
        fields = '__all__'

class CafeteriaStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model=CafeteriaStaff
        fields = '__all__'

