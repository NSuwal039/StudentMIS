
"""it receives signal from ready function use in apps.py"""

from student_management_app.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
import student_management_app.api.serializers as foo
from rest_framework import serializers as drf_serializers
from django.core import serializers

import inspect
try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey

def populate_models(sender, **kwargs):
    a_level_admin, created = Group.objects.get_or_create(name='Admin')
    bachelor_admin_group, created = Group.objects.get_or_create(name='Bachelor-Admin')
    master_admin_group, created = Group.objects.get_or_create(name='Master-Admin')
    teacher_group, created = Group.objects.get_or_create(name='Teacher')
    student_group, created = Group.objects.get_or_create(name='Student')
    parent_group, created = Group.objects.get_or_create(name='Parent')
    cafe_group, created = Group.objects.get_or_create(name='Cafeteria')
    procurement_group, created = Group.objects.get_or_create(name='Procurement')
    finance_group, created = Group.objects.get_or_create(name='Finance')
    
    bachelor, created = CourseCategory.objects.get_or_create(course_name="Bachelor", course_category_code='1')
    master, created = CourseCategory.objects.get_or_create(course_name="Master", course_category_code='2')
    
    finance_branch, created = Branch.objects.get_or_create(name='Finance')
    administration_branch, created = Branch.objects.get_or_create(name='Administration')
    
    
    return [a_level_admin, bachelor_admin_group, master_admin_group,teacher_group,student_group,parent_group,procurement_group,finance_group]

 
# @receiver(post_save)
# def create_logs(sender, instance, created, **kwargs):
#         modellogs_name = 'modellogs'
#         model_label ='logs'
#         modellogs_type = ContentType.objects.get(
#             model=modellogs_name,
#             app_label=model_label
#         )

#         obj_content_type = ContentType.objects.get_for_model(instance)
#         if obj_content_type != modellogs_type:

#             test=ModelLogs.objects.create(
#                 content_type=obj_content_type,
#                 object_id=instance.pk,
#                 action = 'CREATE' if created else 'UPDATE',
#                 object_repr = serializers.serialize("json", [instance])
#             )


