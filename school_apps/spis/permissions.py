from rest_framework import permissions

class VacancyPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'DELETE']:
            return request.user.is_superuser
        return True