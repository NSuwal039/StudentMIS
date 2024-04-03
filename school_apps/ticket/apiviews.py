from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import DepartmentSerializer, TicketSerializer, FormSerializer
from .models import Department, Ticket, Form
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.db.models import Q
import time
from datetime import datetime

# Default no of items to be displayed in a listview
page_count = 2

def page_serializer(paginator, page_obj, page, data):
    serialized_data = {
        'count' : paginator.count,
        'current_page' : int(page),
        'total_pages' : paginator.num_pages,
        'has_prevous_page' : page_obj.has_previous(),
        'has_next_page' : page_obj.has_next(),
        'data' : data
    }
    
    return serialized_data

"""
View to list departments
Includes pagination. Each page lists 10 items
Checks for two query params page and name
Page is used to get items for the page number while name is used to filter department on the basis of their name
For filtering using name, __icontains used as lookup
GET and POST methods allowed
"""
class DepartmentList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):  
        try:    
            department = Department.objects.all()
        except:
            raise Http404


        serializer = DepartmentSerializer(department, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)      

"""
View for department detail view
Allowed methods GET, PUT and DELETE
Need to provide id in the url, integer expected. <int:id>
"""
class DepartmentDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Department.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404    

    def get(self, request, id):
        department = self.get_object(id)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)  

    def put(self, request, id):
        department = self.get_object(id)
        serializer = DepartmentSerializer(department, data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        department = self.get_object(id)     
        department.delete()
        return Response(status = status.HTTP_201_CREATED)         


"""
View to list tickets
Includes pagination. Each page lists 10 items
Checks for two query params page and department
Page is used to get items for the page number while name is used to filter ticket on the basis of department
For department filtering, id of the department needs to be provided
GET and POST methods allowed
"""
class TicketList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = request.query_params.get('page')
        department = request.query_params.get('department')
        
        if not page:
            page = 1

        if request.user.is_staff:
            query = Q()
            if department:
                query &= Q(department = department)

            try:    
                ticket = Ticket.objects.all().filter(query)
            except:
                raise Http404

            paginator = Paginator(ticket, page_count)
            ticket = paginator.get_page(page)
        else:
            ticket = Ticket.objects.filter(user = request.user)

        serializer = TicketSerializer(ticket, many = True)
        data = page_serializer(paginator, ticket, page, serializer.data)
        return Response(data, status = status.HTTP_201_CREATED)

    def post(self, request):
        serializer = TicketSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)        

"""
View for ticket detail view
Allowed methods GET, PUT and DELETE
Need to provide id in the url, integer expected. <int:id>
"""
class TicketDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, id):
        try:
            if request.user.is_staff:
                ticket = Ticket.objects.get(id = id)
            else:
                ticket = Ticket.objects.get(id = id, user = request.user)    
        except ObjectDoesNotExist:
            raise Http404
        else:
            return ticket

    def get(self, request, id):
        ticket = self.get_object(request, id)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        ticket = self.get_object(request, id)
        serializer = TicketSerializer(ticket, data = request.data)
        if serializer.is_valid():
            if request.data['timestamp'] and request.data['closed_timestamp']:
                closed_timestamp = datetime.strptime(request.data['closed_timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ') 
                timestamp = datetime.strptime(request.data['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
                time_diff = closed_timestamp - timestamp
            
                serializer.validated_data['response_time'] = time_diff

            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)    
        
    def delete(self, request, id):
        ticket = self.get_object(request, id)
        ticket.delete()
        return Response(status = status.HTTP_201_CREATED)   

"""
View to list forms
Includes pagination. Each page lists 10 items
Checks for two query params page and department
Page is used to get items for the page number while name is used to filter forms on the basis of department
For department filtering, id of the department needs to be provided
GET and POST methods allowed
"""
class FormList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = request.query_params.get('page')
        department = request.query_params.get('department')
        if not page:
            page = 1

        if request.user.is_staff:
            query = Q()
            if department:
                try:
                    query &= Q(department = Department.objects.get(id = department))
                except:
                    raise Http404

            try:    
                form = Form.objects.all().filter(query)
            except Exception as e:
                raise Http404
            

            paginator = Paginator(form, page_count)
            page_obj = paginator.get_page(page)
            serializer = FormSerializer(page_obj, many = True)
            data = page_serializer(paginator, page_obj, page, serializer.data)

            return Response(data, status = status.HTTP_201_CREATED)

    def post(self, request):
        if request.user.is_staff:
            serializer = FormSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(request.data, status = status.HTTP_201_CREATED)
            else:
                return Response(request.data, status = status.HTTP_400_BAD_REQUEST)    

"""
View for form detail view
Allowed methods GET, PUT and DELETE
Need to provide id in the url, integer expected. <int:id>
"""
class FormDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            form = Form.objects.get(id = id)
            return form
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, id):
        form = self.get_object(id)
        serializer = FormSerializer(form)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        form = self.get_object(id)
        serializer = FormSerializer(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        form = self.get_object(id)
        form.delete()
        return Response(status = status.HTTP_201_CREATED)                               

