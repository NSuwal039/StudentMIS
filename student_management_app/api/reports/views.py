from django.db import models
from school_apps.logs.models import ReportLog
from student_management_app.models import CustomUser
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
import student_management_app.api.serializers as student_api
import school_apps.courses.api.serializers as courses_api
import inspect
from django.db.models import Model
from rest_framework import serializers
import pandas as pd
from django.http import FileResponse
from django.http.response import HttpResponse
from django.db.models.fields import Field
import csv,io
from rest_framework.authtoken.models import Token
from user_agents import parse
import geoip2.webservice
from django.core import serializers as python_serializer
from re import sub
from .serializers_list import serializers_list, ranges_list, additional_fields

def get_serializer(model:Model):
    
    for name, obj in inspect.getmembers(student_api):
        if inspect.isclass(obj) and issubclass(obj, serializers.ModelSerializer) and model==obj.Meta.model:
            return obj
    

@api_view(['GET'])
def get_report(request):
    get_params = list(request.query_params.items())
    filters={}

    content_type = get_model(request.query_params['model'])
    model = content_type.model_class()
    model_name = model.__name__
    fields_list = list(model._meta.fields)
    fields_name = []

    additional_fields_objects=model.objects.all()
    for item in fields_list:
        fields_name.append(item.name)
    for item in get_params:
        if item[0]!='model':
            if item[0] in fields_name:
                filters[item[0]]=item[1]
            else:
                
                model_data = additional_fields[model_name]
                for fields in model_data:
                    if item[0] in fields['queries']:
                        filter_field=fields
                        additional_filter = {
                            filter_field["fk_field"]:item[1]
                        }
                        additional_filter_q = Q(**additional_filter)
                        add_model = filter_field["model"]
                        additional_queryset = add_model.objects.filter(additional_filter_q).values_list(filter_field["object_field"], flat=True)
                        objects_list = model.objects.filter(pk__in=additional_queryset)
                        additional_fields_objects &= objects_list
                        print(additional_fields_objects)

    filter_q = Q(**filters)
    queryset = model.objects.filter(filter_q)
    queryset &= additional_fields_objects

    response = HttpResponse(content_type='text/csv')
    filename = model.__name__ + " report"
    response['Content-Disposition'] = 'attachment; filename= "%s.csv"' %filename

    headers = []

    required_fields = request.query_params.getlist('fields')
    if required_fields:
        fields_list = [model._meta.get_field(f) for f in required_fields]
    
    print('headers', fields_list)

    for item in fields_list:
        headers.append(item.verbose_name)
    writer = csv.writer(response, delimiter=",")
    writer.writerow(headers)

    for item in queryset:
        line = []
        for head_item in fields_list:
            line.append(str(getattr(item,head_item.name)))
        writer.writerow(line)


    #for report log~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        token_key = token.split(" ")[1]
        user = Token.objects.get(key=token_key).user
    except:
        user=None
    
    ip_address = request.META.get('REMOTE_ADDR', None)
    user_agent = request.META['HTTP_USER_AGENT']
    try:
        client = geoip2.webservice.Client(670479, 'gLAn9GhLLVQ3ph6Q', host='geolite.info')
        location_string = client.city(ip_address)
        location = str(location_string.country.name) + " " + str(location_string.city.name)
    except:
        location=None
            
    ua_string = user_agent
    user_agent=parse(ua_string)
    ua_str=str(user_agent)
    device = ua_str.split("/")[0].replace(" ","")+ " " +ua_str.split("/")[1].replace(" ","")
    user_agent_data = user_agent.browser.family + " " + user_agent.browser.version_string

    if user:
        ReportLog.objects.create(
            app_name=content_type.app_label,
            model_name=content_type.model,
            user=user,
            ip=ip_address,
            location=location,
            user_agent=user_agent_data,
            device=device
        )
    return response    

def get_model(modelname:str):
    content_type = ContentType.objects.get(
        model=modelname,
    )

    return content_type

@api_view(['GET'])
def check_query_params(request):
    print(request.query_params.getlist('years'))
    return HttpResponse('ok')


@api_view(['GET'])
def get_report_fields(request):
    content_type = get_model(request.query_params['model'])
    model = content_type.model_class()
    fields_list = list(model._meta.fields)

    fk_list = []
    response = {}
    response['fields']=[]
    model_name = content_type.model_class().__name__
    
    for item in fields_list:
        temp_json={}
        temp_json['name']=item.name
        temp_json['display_name'] = camel_case(item.name)
        temp_json['relation'] = item.is_relation
        temp_json['field']=item.get_internal_type()

        if item.get_internal_type()=='ForeignKey':
            fk_list.append(item.related_model)
            temp_json['related_to']=item.related_model.__name__
        response['fields'].append(temp_json)
    
    try:
        print("in try")
        for item in additional_fields[model_name]:
            temp_json={}
            temp_json['name']=item["name"]
            temp_json['display_name'] = camel_case(item["name"])
            temp_json['relation'] = item["is_relation"]
            temp_json['field']=item["field"]
            if item["field"]=='ForeignKey':
                fk_list.append(item["fk_dropdown"])
            temp_json['related_to']=item["fk_dropdown"].__name__
            response['fields'].append(temp_json)
            pass

    except:
        pass

    try:
        response['range_fields']=ranges_list[model_name]
    except:
        pass

    # print(content_type.model_class().__name__)
    # import pdb;pdb.set_trace()
    for item in fk_list:
        serializer_obj=serializers_list[item.__name__]
        response[item.__name__]=serializer_obj(item.objects.all(), many=True).data
    return Response(response)



def camel_case(s):
    s = sub(r"(_|-)+", " ", s).title()
    return s

def lower_case(s):
    s = sub(r" ", "_", s).lower()
    return s