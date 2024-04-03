from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from student_management_app.models import CustomUser

"""
Choices for status for a ticket
Default status is Pending
"""
status_choices = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Ongoing', 'Ongoing'),
    ('Closed', 'Closed'),
)

"""
Choices for priority for a ticket
Default priority is High 
Admin can change the priority
"""
priority_choices = (
    ('High Priority', 'High Priority'),
    ('Medium Priority', 'Medium Priority'),
    ('Low Priority', 'Low Priority'),
)

"""
Deparment model for adding departments
Name of the department and the members inside that department
members is m2m field
"""
class Department(models.Model):
    name = models.CharField(max_length = 250)
    members = models.ManyToManyField(CustomUser)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)    

"""
Form model for adding new forms
Each department can have multiple forms
Ordering done by descending id
"""
class Form(models.Model):
    department = models.ForeignKey(Department, on_delete = models.CASCADE)
    elements = models.JSONField()
    layout = models.JSONField()
    setting = models.JSONField()
    style = models.JSONField()

    class Meta:
        ordering = ['-id']

"""
Ticket model for adding new tickets
Ordering is done according to the descending timestamp
Response time refers to the time taken to solve the issue and close the ticket once it has been added
Response time is updated automatically when the closed_timestamp is set
Timestamp refers to the time when the model was first created
"""
class Ticket(models.Model):
    user = models.ForeignKey(CustomUser, null = True, on_delete = models.SET_NULL)
    organization = models.CharField(max_length = 350, blank = True, null = True)
    department = models.ForeignKey(Department, null = True, on_delete = models.SET_NULL)
    priority = models.CharField(choices = priority_choices, default = 'High Priority', max_length = 15)
    form = models.ForeignKey(Form, null = True, on_delete = models.SET_NULL)
    #response = models.TextField()
    ticket_response = models.JSONField(blank = True, null = True)

    status = models.CharField(choices = status_choices, max_length = 10, default = 'Pending')
    seen = models.BooleanField(default = False)
    reviewed = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add = True)

    closed_by = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, blank = True, null = True, related_name = 'closed_by')
    closing_remarks = models.TextField(blank = True, null = True)
    closed_timestamp = models.DateTimeField(blank = True, null = True)
    response_time = models.CharField(max_length = 250, blank = True, null = True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return str(self.user)    

"""
    def save(self, *args, **kwargs):
        if self.timestamp and self.closed_timestamp:
            time_diff = self.closed_timestamp - self.timestamp
            time_diff = time_diff.seconds
            time_diff = timedelta(seconds = time_diff)

            self.response_time = time_diff  
        super(Ticket, self).save(*args, **kwargs)    
"""


