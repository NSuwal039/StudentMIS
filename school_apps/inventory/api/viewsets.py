from urllib import response
from django.http import HttpResponse
import pandas as pd
from .serializers import *
from ..models import *
from rest_framework import viewsets
from rest_framework import status

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from student_management_app.pagination import CustomLimitOffsetPagination

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    search_fields = ['name']
    filterset_fields = ['name']

    def get_queryset(self):
        return Category.objects.all()

class AssetsViewSet(viewsets.ModelViewSet):
    serializer_class = AssetsSerializer
    search_fields = ['name']
    filterset_fields = ['category']

    def get_queryset(self):
        return Assets.objects.all()

class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    search_fields = ['name', 'pan_number']
    filterset_fields = ['name', 'pan_number']

    def get_queryset(self):
        return Vendor.objects.all()

class StatusOptionsViewSet(viewsets.ModelViewSet):
    serializer_class = StatusOptionsSerializer
    def get_queryset(self):
        return StatusOptions.objects.all()
    
    @action(detail=False, methods=['POST'], url_path='csv-upload')   
    def csv_upload(self, request, *args, **kwargs):
        df = pd.read_csv(request.FILES['file'], index_col=0)

        print(df)
        for index, row in df.iterrows():
            print(row['goto_branch'])
        return HttpResponse("ok")

class ProcurementRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ProcurementRequestSerializer
    search_fields = []
    filterset_fields = ['requester','requester_dept','requester_branch','category','item','is_complete','status',
                        'procurement_personnel','finance_personnel','procurement_date','finance_date']

    def get_queryset(self):
        return ProcurementRequest.objects.all()

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filterset_fields = ['vendor','category','item','request_date','is_complete']
    search_fields = ['procurement_order']

    def get_queryset(self):
        return Transaction.objects.all()

    @action(detail=False, methods=['POST'], url_path='register-transaction-items')
    def register_transaction_items(self, request, *args, **kwargs):
        item_list=[]
        for item in request.data:
            trans_item = transaction_items.objects.get(pk=item['id'])
            try:
                to_create = Item.objects.create(
                    id_no=item['item_id'],
                    item_type=trans_item.item_type,
                    category=trans_item.item_type.category,
                    current_department=Department.objects.get(pk=item['dept_id']),
                    source_transaction=trans_item.transaction
                )
                item_list.append(to_create)
            except:
                try:
                    to_create = Item.objects.create(
                    id_no=item['item_id'],
                    item_type=trans_item.item_type,
                    category=trans_item.item_type.category,
                    current_branch=Branch.objects.get(pk=item['branch_id']),
                    source_transaction=trans_item.transaction
                )
                    item_list.append(to_create)
                except:
                    to_create = Item.objects.create(
                    id_no=item['item_id'],
                    item_type=trans_item.item_type,
                    category=trans_item.item_type.category,
                    source_transaction=trans_item.transaction
                )
                    item_list.append(to_create)


        return response(
            ItemSerializer(to_create,many=True).data,
            status=status.status.HTTP_201_CREATED
        )

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer

    search_fields = ['id_no']
    filterset_fields = ['category','item_type','source_transaction','current_department','current_branch']

    def get_queryset(self):
        return Item.objects.all()

class assets_transferViewSet(viewsets.ModelViewSet):
    serializer_class = assets_transferSerializer
    search_fields = []
    filterset_fields = ['from_dept','to_dept','from_branch','to_branch','overseer','transfer_date','item']

    def get_queryset(self):
        return assets_transfer.objects.all()

class transaction_itemsViewSet(viewsets.ModelViewSet):
    serializer_class = transaction_itemsSerializer
    search_fields = ['item']
    filterset_fields = ['transaction','item_type','is_registered']

    def get_queryset(self):
        return transaction_items.objects.all()


