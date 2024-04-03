from django_filters.rest_framework import DjangoFilterBackend

class LogsBackend(DjangoFilterBackend):
    def get_filterset(self, request, queryset, view):
        print(request)
        print(queryset)
    
        