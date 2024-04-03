from rest_framework import serializers
from ..models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields = '__all__'

class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Assets
        fields = '__all__'

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Vendor
        fields = '__all__'

class StatusOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=StatusOptions
        fields = '__all__'

class ProcurementRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProcurementRequest
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transaction
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=Item
        fields = '__all__'

class assets_transferSerializer(serializers.ModelSerializer):
    class Meta:
        model=assets_transfer
        fields = '__all__'

class transaction_itemsSerializer(serializers.ModelSerializer):
    class Meta:
        model=transaction_items
        fields = '__all__'
