from ..models import *
from .serializers import *
from school_apps.inventory.models import Category

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token, TokenProxy
from rest_framework import viewsets
import json
from rest_framework.decorators import action
#~~~~~~~~~~~~~~~~~~~~~~~~~~~filters/pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from student_management_app.pagination import CustomLimitOffsetPagination


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_fields = ['category', ]
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Ingredients.objects.all()

    def create(self, request):
        serializer = IngredientsSerializer(data=request.data)

        if serializer.is_valid():
            category = Category.objects.get(name='Ingredients')
            serializer.save(category=category)


class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_fields = ['name', ]
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return FoodItem.objects.all()

class StallViewSet(viewsets.ModelViewSet):
    serializer_class = StallSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['stall_id',]
    filterset_fields = ['stall_id', ]
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Stall.objects.all()

    @action(detail=True, methods=['GET',])
    def get_menu(self, request, *args, **kwargs):
        self_obj = self.get_object()
        self_menu=self_obj.menu
        menuitems = menu_items.objects.filter(menu=self_menu)
        print(menuitems)
              
        menu_serializer = MenuSerializer(self_menu)
        menuitems_serializer = menu_itemsSerializer(menuitems, many=True)
        
        return Response(menuitems_serializer.data)

    @action(detail=True, methods=['PATCH',], url_path='edit-menu-items')
    def edit_menu_items(self, request, *args, **kwargs):
        response=[]
        for item in request.data:
            object = menu_items.objects.get(pk=item['id'])
            print(object)
            serializer=menu_itemsSerializer(instance=object,data=item, partial=True)
            if serializer.is_valid():
                serializer.save()
                response.append(serializer.data)
            else:
                return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(response)
    
    @action(detail=True, methods=['DELETE',], url_path='delete-menu-items')
    def delete_menu_items(self, request, *args, **kwargs):
        response={}
        count=0
        for item in request.data:
            try:
                object = menu_items.objects.get(pk=item['id'])
                object.delete()
                count+=1
            except:
                count+=0
            
        response['deleted']=count
        return Response(response)
        
        # return Response({'msg':'ok'})
    
    @action(detail=True, methods=['POST',], url_path='create-menu-items')
    def create_menu_items(self, request, *args, **kwargs):
        menu_list = []
        self_obj = self.get_object()
        self_menu, created = Menu.objects.get_or_create(stall=self_obj)
        self_obj.menu=self_menu
        self_obj.save()
        print(self_menu)
        for item in request.data:
            try:
                check=menu_items.objects.get(menu=self_menu, item=FoodItem.objects.get(pk=item['item']))
                print(check)
            except:
                serializer=menu_itemsSerializer(data=item)
                if serializer.is_valid():
                    serializer.save(menu=self_menu)
                else:
                    return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        
        for item in menu_items.objects.filter(menu=self_menu):
            menu_list.append(menu_itemsSerializer(item).data)
        response = {}
        response['menu']=MenuSerializer(self_menu).data
        response['menu_items']=menu_list
        return Response(response)


class SalesViewSet(viewsets.ModelViewSet):
    serializer_class = SalesSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return Sales.objects.all()

class sales_itemViewSet(viewsets.ModelViewSet):
    serializer_class = sales_itemSerializer

    def get_queryset(self):
        return sales_item.objects.all()

# class IngredientAssignmentViewSet(viewsets.ModelViewSet):
#   
#     serializer_class = IngredientAssignmentSerializer

#     def get_queryset(self):
#         return IngredientAssignment.objects.all()

class stall_ingredients_itemViewSet(viewsets.ModelViewSet):
    serializer_class = stall_ingredients_itemSerializer

    def get_queryset(self):
        return stall_ingredients_item.objects.all()

class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer

    def get_queryset(self):
        return Menu.objects.all()


    # @action(detail=False, methods=['POST'])
    # def edit_menu(self, request, *args, **kwargs):
    #     menu = self.get_object()
    #     data = request.data['menu_items']

    #     print(data)

    #     return Response({'msg':'ok'})

class menu_itemsViewSet(viewsets.ModelViewSet):
    serializer_class = menu_itemsSerializer

    def get_queryset(self):
        return menu_items.objects.all()

class CafeteriaStaffViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaStaffSerializer

    def get_queryset(self):
        return CafeteriaStaff.objects.all()


