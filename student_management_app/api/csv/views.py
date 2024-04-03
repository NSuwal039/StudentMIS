from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view
from rest_framework import serializers
from django.http import FileResponse
import pandas as pd
from django.db.models.fields import Field
import csv,io
from ..reports.views import get_model, camel_case, lower_case
from django.http.response import HttpResponse
import pprint
from ..reports.serializers_list import serializers_list, ranges_list, additional_fields, csv_fields
from rest_framework.response import Response
from rest_framework import status


excludeFields = [
        'BigAutoField',
        'OneToOneField',
        'JSONField',
        'FileField'
    ]

excludeName=[
    'created_at',
    'updated_at'
]

def get_csv_fields(model: models.Model):
    model_name = model.__name__
    fields_list = list(model._meta.fields)
    fields_name = []

    for item in fields_list:
        if item.name not in excludeName and item.get_internal_type() not in excludeFields:
            fields_name.append(item)

    return fields_name

def get_foreign_keys(model:models.Model):
    model_name = model.__name__
    fields_list = list(model._meta.fields)
    fields_name = []

    for item in fields_list:
        if item.get_internal_type()=='ForeignKey':
            fields_name.append(item)
    return fields_name

@api_view(['GET'])
def download_csv(request):
    content_type = get_model(request.query_params['model'])
    model_class = content_type.model_class()
    return_json = {}
    fields_name = get_csv_fields(model_class)
    sample_model=model_class.objects.all()[0]
    headers = []
    values=[]

    for item in fields_name:
        values.append(getattr(sample_model,item.name).pk if item.get_internal_type()=="ForeignKey" else getattr(sample_model,item.name))
        headers.append(camel_case(item.name))

    print (headers ,'\n',values,'\n')
    df=pd.DataFrame([values],columns=headers)
    print(df)
    csv_file = df.to_csv(index=False)

    filename = model_class.__name__ + " format"
    response = FileResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= "%s.csv"' %filename
    return response
    return HttpResponse("ok") 

@api_view(['POST'])
def upload_csv(request):
    df = pd.read_csv(request.FILES['file'])
    df = df.rename(columns = lambda x:lower_case(x))
    df = df.iloc[1: , :]
    df_dict = df.to_dict('index')
    df_list = []
    content_type = get_model(request.data['model'])
    model_class = content_type.model_class()
    serializer = serializers_list[model_class.__name__]

    print(df)

    foreign_keys = []
    for item in model_class._meta.fields:
        if item.get_internal_type()=='ForeignKey':
            foreign_keys.append(item)

    for item in df_dict:
        df_list.append(df_dict[item])

    # process_json(df_list, foreign_keys)


    create_obj = serializer(data = df_list, many=True)
    create_obj.is_valid(raise_exception=True)
    create_obj.save()

    return Response(
        create_obj.data,
        status=status.HTTP_200_OK
    )
    return HttpResponse('ok')

def row_to_json(row):
    for item in row:
        print(item)

def process_json(csv_list, foreignkey_list):
    to_return = []
    foreignkey_name = [item.name for item in foreignkey_list]

    for item in csv_list:
        temp_json = {}
        for key,value in item.items():
            # print(key, value, key in foreignkey_name)
            if key not in foreignkey_name:
                temp_json[key]=value
            # else:
            #     try:
            #         value=

        to_return.append(temp_json)    

    print(to_return)

    pass