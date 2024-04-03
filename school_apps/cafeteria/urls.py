from django.urls import path
from .views import *

app_name = 'cafeteria'

urlpatterns = [
    path('manage_ingredients/', ingredients_list, name='ingredients_list'),
    path('manage_fooditems/', fooditem_list, name='fooditems_list'),
    path('manage_stalls/', stall_list, name='stalls_list'),

    path('manage_menu/<str:pk>', stall_menu ,name= 'manage_menu'),
    path('stall_members/<str:pk>', stall_members ,name= 'stall_members'),
    path('staff_assignment/', staff_assignment ,name= 'staff_assignment'),
    path('stall_ingredients_assignment/', stall_ingredients_assignment ,name= 'stall_ingredients_assignment'),

    path('sales/', sales ,name= 'sales'),

    path('ajax/staff_to_stall_ajax/', staff_to_stall_ajax ,name= 'staff_to_stall_ajax'),

    

]