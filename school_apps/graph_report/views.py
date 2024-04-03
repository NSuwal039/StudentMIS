from django.shortcuts import render
from django.db.models import Model
from django.db.models.query import QuerySet

# Create your views here.

def graph_report(model: Model, queryset: QuerySet, list: list):
    fields_list = model._meta.get_fields()
    valid_list =[]
    print('\n')
    for item in fields_list:
        if item.name in list:
            valid_list.append(item)
    
    values_list =[]
    field_count = valid_list.count()

    for obj in queryset:
        for item in valid_list:
            temp_json={}
            temp_json[item.name]=item.value_from_obj(obj)
            temp={str(obj):temp_json}
        
        values_list.append(temp)
            
            

    
    print('func:',valid_list,type(valid_list[0]),'\n')