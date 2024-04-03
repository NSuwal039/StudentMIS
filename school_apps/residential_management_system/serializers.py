from rest_framework import serializers
from .models import RoomType, Room, RoomPicture, Booking
from student_management_app.models import CustomUser

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    room_type = serializers.PrimaryKeyRelatedField(queryset = RoomType.objects.all())
    class Meta:
        model = Room
        fields = '__all__'  

class RoomPictureSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset = Room.objects.all())
    class Meta:
        model = RoomPicture
        fields = '__all__'    

class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset = CustomUser.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset = Room.objects.all())


class BookingSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset = Room.objects.all())
    class Meta:
        model = Booking     
        fields = '__all__'