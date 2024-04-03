from django.db import models
from student_management_app.models import CustomUser
import arrow
import redis
from django.conf import settings
from student_management_app.models import CustomUser
from django.core.exceptions import ValidationError

booking_status = (
    ('Booked', 'Booked'),
    ('Residing', 'Residing'),
    ('Left', 'Left'),
)

class RoomType(models.Model):
    room_type = models.CharField(max_length = 350)
    rate = models.PositiveIntegerField()

    def __str__(self):
        return str(self.room_type)

    class Meta:
        ordering = ['-id']    

class Room(models.Model):
    room_name = models.CharField(max_length = 250, unique = True)
    building = models.CharField(max_length = 250)
    floor = models.CharField(max_length = 100)
    room_type = models.ForeignKey(RoomType, on_delete = models.CASCADE)
    inventory = models.JSONField(blank = True, null = True)
    members = models.ManyToManyField(CustomUser, blank = True)
    thumbnail = models.FileField(upload_to = 'residential/room-thumbnails/', blank = True, null = True)
    capacity = models.PositiveIntegerField()
    availability = models.BooleanField(default = True)
    google_plus_code = models.CharField(max_length = 350, blank = True, null = True)

    class Meta:
        ordering = ['-id']  

    def __str__(self):
        return str(self.room_name)    

    def save(self, *args, **kwargs): 
        super(Room, self).save(*args, **kwargs)     
        if self.availability:  
            if (self.members.count() >= self.capacity):
                self.availability = False
                super(Room, self).save(*args, **kwargs) 
            else:
                self.availability = True    
                super(Room, self).save(*args, **kwargs) 

class RoomPicture(models.Model):
    room = models.ForeignKey(Room, on_delete = models.CASCADE)
    photo = models.FileField(upload_to = 'residential/room/')

    def __str__(self):
        return str(self.room)  

    class Meta:
        ordering = ['-id']    

class Expense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    room = models.ForeignKey(Room, on_delete = models.SET_NULL, null = True)
    details = models.JSONField(blank = True, null = True)

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ['-id']    

class Booking(models.Model):
    booked_by = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, null = True)
    purpose = models.TextField()
    remarks = models.TextField(blank = True, null = True)

    room = models.ForeignKey(Room, on_delete = models.SET_NULL, null = True)

    booked_on = models.DateTimeField(auto_now_add = True)
    booking_start = models.DateTimeField(blank = True, null = True)
    booking_end = models.DateTimeField(blank = True, null = True)
    task_id = models.CharField(max_length=50, blank=True, editable=False)

    status = models.CharField(choices = booking_status, max_length = 20, default = 'Booked')

    def __str__(self):
        return str(self.id)

    def schedule_review(self):
        review_time = arrow.get(self.booking_end)
        now = arrow.now()
        milli = (review_time - now).total_seconds()
        milli_to_wait =  milli * 1000
        
        from .tasks import send_review
        result = send_review.send_with_options(
            args=(self.id,),
            delay = milli_to_wait
        )
        return result.options['redis_message_id']

    '''
    def clean(self):
        """Checks that appointments are not scheduled in the past"""

        appointment_time = arrow.get(self.booking_end)

        if appointment_time < arrow.utcnow():
            raise ValidationError(
                'You cannot schedule an appointment for the past. '
                'Please check your time and time_zone')    
        
    '''
    def save(self, *args, **kwargs):
        if self.task_id:
            self.cancel_task()
        super(Booking, self).save(*args, **kwargs)  

        self.task_id = self.schedule_review()

        super(Booking, self).save(*args, **kwargs)  

    def cancel_task(self):
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.hdel("dramatiq:default.DQ.msgs", self.task_id)    

    class Meta:
        ordering = ['booked_on']    

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, null = True)
    booking = models.ForeignKey(Booking, on_delete = models.SET_NULL, null = True)
    review = models.TextField()
    rating = models.DecimalField(max_digits = 3, decimal_places = 2)
    timestamp = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return str(self.id)

   


