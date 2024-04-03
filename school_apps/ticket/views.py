from django.views import View
from .models import Department, Ticket
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .forms import DepartmentForm, TicketForm
from django.contrib import messages

class PrintFormView(View):
    def get(self, request):
        model = request.GET.get('model', None)
        _id = request.GET.get('id', None)
        if model and _id:
            if (model.lower() ==  'department'):
                try:
                    item = Department.objects.get(id = _id)
                except ObjectDoesNotExist:
                    raise Http404
                else:
                    context = {'model' : 'department', 'item' : item} 

            elif (model.lower() ==  'ticket'):
                try:
                    item = Ticket.objects.get(id = _id)
                except ObjectDoesNotExist:
                    raise Http404
                else:
                    context = {'model' : 'ticket', 'item' : item}   
        else:
            context = {}                     
        return render(request, 'ticket/printform.html', context)        
            
    
class DepartmentAddView(View):
    def get(self, request):
        form = DepartmentForm()
        context = {'form' : form}
        return render(request, 'ticket/department-add.html', context)

    def post(self, request):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department Added successfully !')
            return redirect('/ticket/department/')

        else:  
            messages.error(request, 'Please correct the following errors.')

class DepartmentEditView(View):
    def get(self, request, id):
        try:
            department = Department.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:    
            form = DepartmentForm(instance = department)        
            context = {'form' : form, 'department' : department}
            return render(request, 'ticket/department-edit.html', context)

    def post(self, request, id):
        try:
            department = Department.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:  
            form = DepartmentForm(request.POST, instance = department)
            if form.is_valid():
                form.save()
                messages.success(request, 'Department Edited successfully !')
                return redirect('/ticket/department/')

            else:  
                messages.error(request, 'Please correct the following errors.')        

class DepartmentDeleteView(View):
    def get(self, request, id):
        try:
            department = Department.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:                
            department.delete()
            messages.success(request, 'Department Deleted successfully !')
            return redirect('/ticket/department/')

class DepartmentListView(View):
    def get(self, request):
        department = Department.objects.all()
        context = {'department' : department}
        return render(request, 'ticket/department-list.html', context)

class DepartmentDetailView(View):
    def get(self, request, id):
        try:
            department = Department.objects.get(id = id)

        except ObjectDoesNotExist:
            raise Http404    

        else:
            context = {'department' : department}
            return render(request, 'ticket/department-detail.html', context)               

class TicketListView(View):
    def get(self, request):
        tickets = Ticket.objects.all()
        context = {'tickets' : tickets}
        return render(request, 'ticket/ticket-list.html', context)

class TicketDetailView(View):
    def get(self, request, id):
        try:
            ticket = Ticket.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            context = {'ticket' : ticket}
            return render(request, 'ticket/ticket-detail.html', context)        

class TicketAddView(View):
    def get(self, request):
        form = TicketForm()
        context = {'form' : form}
        return render(request, 'ticket/ticket-add.html', context)

    def post(self, request):
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket Added successfully !')

        else:
            messages.success(request, 'Ticket Added successfully !')
        return redirect('/ticket/ticket-list/')    

class TicketEditView(View):
    def get(self, request, id):
        try:
            ticket = Ticket.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:        
            form = TicketForm(instance = ticket)
            context = {'form' : form, 'ticket' : ticket}
            return render(request, 'ticket/ticket-edit.html', context)

    def post(self, request, id):
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/ticket/ticket/')            

class TicketDeleteView(View):
    def get(self, request, id):
        try:
            ticket = Ticket.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:        
            ticket.delete()
            return redirect('/ticket/ticket/')
            messages.success(request, 'Ticket deleted successfully !')

            