from django.shortcuts import get_object_or_404
# import dramatiq
from django.conf import settings
from django.core.mail import send_mail

from school_apps.lms.models import LibraryProfile


# @dramatiq.actor
# def send_alert_email(bookissue_id):
#     try:
#         get_email = get_object_or_404(BookIssue, id=bookissue_id)
#         print("get email::: ", get_email)
#     except Exception as e:
#         print("error occured::: {}".format(e))
#     else:        
#         subject = 'Dear Student'
#         plain_message = 'Please Return Book by Tomorrow or you will be fine charged'
#         to_email = get_email
#         send_mail(subject, plain_message, settings.EMAIL_HOST_USER,[to_email])



# @dramatiq.actor
def email_member_predue(obj):
    subject = 'Dear Member'
    message = 'Please Return Book by Tomorrow or you will be fine charged'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [obj])

# @dramatiq.actor
def email_member_overdue(obj):
    member=LibraryProfile.objects.get(id=obj)
    member.overdue_count+=1
    member.save()
    subject = 'Dear Member'
    message = 'Please Return Book as soon as possible. You are been fined'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [member.email])



