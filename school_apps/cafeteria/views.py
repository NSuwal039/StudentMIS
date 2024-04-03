from abc import ABCMeta
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .forms import *
from .models import *
from school_apps.inventory.models import Category
from django.contrib import messages 
from django.urls import reverse

from student_management_app.router import router

# Create your views here.

def ingredients_list(request):
    form = IngredientsCreateForm
    ingredients = Ingredients.objects.all()



    if request.method =='POST':
        form = IngredientsCreateForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.category = Category.objects.get(name="Ingredients")
            instance.save()
            messages.success(request,"Ingredient added.")
        else:
            messages.error(request, "Error.")
    
    context = {'form':form,
                'ingredients':ingredients}

    return render(request, 'cafeteria/manage_ingredients.html', context=context)

def fooditem_list(request):
    form = FoodItemCreateForm
    foods = FoodItem.objects.all()

    if request.method =='POST':
        form = FoodItemCreateForm(request.POST)

        if form.is_valid():
            form.save()
            
            messages.success(request,"Food Item added.")
        else:
            messages.error(request, "Error.")
    
    context = {'form':form,
                'foods':foods}

    return render(request, 'cafeteria/manage_fooditems.html', context=context)


def stall_list(request):
    form = StallCreateForm
    stalls = Stall.objects.all()

    if request.method =='POST':
        form = StallCreateForm(request.POST)

        if form.is_valid():
            form.save()
            
            messages.success(request,"Stall added.")
        else:
            messages.error(request, "Error.")
    
    context = {'form':form,
                'stalls':stalls}

    return render(request, 'cafeteria/manage_stalls.html', context=context)

def stall_menu(request, pk):
    stall = Stall.objects.get(pk=pk)

    context = {
        'stall':stall,
        'foods': FoodItem.objects.all(),
        'existing_item': menu_items.objects.filter(menu__stall=stall)
    }

    if request.method=="POST":
        count = int(request.POST.get("count"))
        i = 1
        menu, created = Menu.objects.get_or_create(stall=stall)

        while (i<=count):
            obj, created = menu_items.objects.get_or_create(menu=menu, item = FoodItem.objects.get(pk=request.POST.get(str(i))))
            price_str=str(i)+"_price"
            obj.price = float(request.POST.get(price_str))
            obj.save()
            i+=1

    return render(request, 'cafeteria/manage_menu.html', context=context)

def sell_food(request):
    pass

def staff_assignment(request):
    staff= CafeteriaStaff.objects.all()

    context ={
        'staff':staff,
        'stall':Stall.objects.all()
    }

    return render(request, 'cafeteria/staff_assignment.html', context=context)

def staff_to_stall_ajax(request):
    
    staff = CafeteriaStaff.objects.get(pk = request.GET['teacher'])
    stall = Stall.objects.get(stall_id = request.GET['subject'])
    

    try:
        staff.stall = stall
        staff.save()

        return JsonResponse({'message':'Staff assigned successfully.'}, status = 201)
    except:
        
        return JsonResponse({'error_message':'Assignment failed.'}, status = 500)
    
def stall_members(request, pk):
    stall = Stall.objects.get(pk=pk)
    staff = CafeteriaStaff.objects.filter(stall=stall)

    context = {
        'stall':stall,
        'staff':staff
    }

    return render (request, 'cafeteria/stall_members.html', context)

def stall_ingredients_assignment(request):
    context={
        'ingredients':Ingredients.objects.all(),
        'stall' : Stall.objects.all()
    }
    return render(request, 'cafeteria/stall_ingredients_assignment.html', context)

def sales(request):
    c_user = CafeteriaStaff.objects.get(extra_user__extra_user = request.user)
    c_stall = c_user.stall
    stall_menu = Menu.objects.get(stall=c_stall)
    c_menu_items = menu_items.objects.filter(menu=stall_menu)
    students = list(Student.objects.all())

    if request.method == 'POST':
        count = int(request.POST.get("count"))
        student = Student.objects.get(student_user__username = request.POST['student'])
        stall = Stall.objects.get(pk = request.POST['stall'])
        i = 1

        sales_obj, created = Sales.objects.get_or_create(
            customer = student.student_user,
            stall=stall,
            total=0
        )

        while (i<=count):
            post_item = menu_items.objects.get(pk=request.POST[str(i)])
            post_amount = int(request.POST[str(i)+"_amount"])
            sales_item.objects.create(
                sale=sales_obj,
                item=post_item,
                amount=post_amount,
                total = post_item.price * post_amount
            )
            i+=1
        
        for item in sales_item.objects.filter(sale=sales_obj):
            sales_obj.total+=item.total
            sales_obj.save()

        messages.success(request, "Sales recorded.")
        return redirect('cafeteria:sales')
            

    context = {
        'user':c_user,
        'stall':c_stall,
        'menu':stall_menu,
        'menu_items':c_menu_items,
        'students':students
    }

    return render (request, 'cafeteria/sales.html', context)
    pass