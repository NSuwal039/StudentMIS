from rest_framework import serializers
from student_management_app.api.serializers import AwardsSerializer, CustomUserSerializer, StudentSerializer

from ..models import *

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=EventCategory
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    eventcategory = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    awards = serializers.SerializerMethodField()
    
    class Meta:
        model=Event
        fields = '__all__'
    
    def get_eventcategory(self, obj):
        return EventCategorySerializer(obj.event_type).data
    
    def get_participants(self, obj):
        participants = obj.participants.all()
        return CustomUserSerializer(participants, many=True).data
    
    def get_awards(self, obj):
        awards = obj.awards.all()
        return AwardsSerializer(awards, many=True).data

class event_participantsSerializer(serializers.ModelSerializer):
    class Meta:
        model=event_participants
        fields='__all__'