import arrow
import dramatiq
from .models import Booking
from django.core.mail import send_mail
from django.conf import settings

@dramatiq.actor
def send_review(booking_id):
    try:
        booking = Booking.objects.get(id = booking_id)
    except ObjectDoesNotExist:
        pass
    else:        
        subject = 'Thank you for staying with us'
        plain_message = 'Leave a review here http://127.0.0.1:8000/residential/customer/review/'
        to_email = booking.booked_by.email
        send_mail(subject, plain_message, settings.EMAIL_HOST_USER,[to_email])