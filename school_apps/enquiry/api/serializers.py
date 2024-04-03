from rest_framework import serializers

from ..models import *

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model=Enquiry
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields = '__all__'


