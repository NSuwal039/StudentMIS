from django.db import models
from student_management_app.models import *
# Create your models here.
event_priority_choices = (
        ('REG', 'Regular'),
        ('URG', 'Urgent')
    )

class EventCategory(models.Model):
    name=models.CharField(max_length=100)

class Event(models.Model):
    event_name = models.CharField(max_length=255)
    event_type = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(null=True, blank=True)
    agenda = models.TextField(null=True, blank=True)
    event_priority = models.CharField(max_length=3, default='REG', choices=event_priority_choices)
    participants = models.ManyToManyField(CustomUser, through='event_participants')
    awards = models.ManyToManyField(Awards)

class event_participants(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    # student = models.ForeignKey(Student, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE )
    rank = models.PositiveIntegerField(blank=True, null=True)
    award_rewarded = models.ForeignKey(awards_recipient, on_delete=models.CASCADE, null=True)
    remarks = models.CharField(max_length=255, blank=True)