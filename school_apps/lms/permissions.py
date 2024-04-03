from rest_framework.permissions import DjangoModelPermissions 
from .compound_selector import query_engine


class CustomDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
    
    def has_object_permission(self, request, view, obj):
        user=request.user
        query=query_engine(user,view.basename).get()
        if query:
            return obj in query
        return True