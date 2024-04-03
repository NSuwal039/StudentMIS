
from tokenize import blank_re
from django.db.models.signals import post_save ,m2m_changed
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.urls import reverse
from django.http import JsonResponse
# from members.models import Member
import string
import random
from django.utils.text import slugify
from student_management_app.models import CustomUser, Student
from django.dispatch import receiver
from student_management_app.models import CustomUser ,Staff ,AdminUser

# def rand_slug():
#     return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


class BookCategory(models.Model):
    category_name = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True, null=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Book Category'
        db_table = 'tbl_category'

    def get_url(self):
        return ''
        # return reverse('store:products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name

class Author(models.Model):
    firstname=models.CharField(max_length=300)
    middlename=models.CharField(max_length=300,blank=True,null=True)
    lastname=models.CharField(max_length=300)
    nationality=models.CharField(max_length=100,null=True,blank=True)
    introduction=models.TextField(blank=True,null=True)
    photo=models.ImageField(upload_to='library/author',null=True, blank=True)

    def __str__(self):
        if self.middlename is None:
            return f'{self.firstname}{self.lastname}'
        else:
            return f'{self.firstname}{self.middlename}{self.lastname}'

class Publication(models.Model):
    name=models.CharField(max_length=300)
    location=models.CharField(max_length=100,null=True,blank=True)
    introduction=models.TextField(blank=True,null=True)
    photo=models.ImageField(upload_to='library/publication',null=True, blank=True)

    def __str__(self):
        return self.name

class Library(models.Model):
    name=models.CharField(max_length=300)
    location=models.CharField(max_length=100,null=True,blank=True)
    staff_max_borrow=models.PositiveIntegerField(default=4)
    faculty_max_borrow=models.PositiveIntegerField(default=5)
    student_max_borrow=models.PositiveIntegerField(default=5)
    public_max_borrow=models.PositiveIntegerField(default=3)
    staff_max_hold=models.PositiveIntegerField(default=4)
    faculty_max_hold=models.PositiveIntegerField(default=5)
    student_max_hold=models.PositiveIntegerField(default=5)
    public_max_hold=models.PositiveIntegerField(default=3)
    fines_per_day_per_book=models.PositiveIntegerField(default=1)
    maximum_fine_multiplier=models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    overdue_cost=models.DecimalField(max_digits=3, decimal_places=2, default=2.5)
    max_number_of_overdue=models.PositiveIntegerField(default=3)
    overdue_period=models.PositiveIntegerField(default=50)
    head_librarian=models.ForeignKey(Staff,on_delete=models.CASCADE,null=True,blank=True,related_name='library_head_librarian')

    def __str__(self):
        return self.name




class Books(models.Model):
    TYPE = (
        ('Book', 'Book'),
        ('Serial', 'Serial'),
    )
    title = models.CharField(max_length=500)
    author = models.ManyToManyField(Author,blank=True,related_name='book_author')
    publication=models.ForeignKey(Publication,on_delete=models.CASCADE,null=True,blank=True)
    place_of_publication=models.CharField(max_length=255,null=True,blank=True)
    year_of_publication=models.CharField(max_length=10,null=True,blank=True)
    total_pages=models.IntegerField(null=True,blank=True)
    edition=models.CharField(max_length=100,blank=True,null=True)
    volume=models.CharField(max_length=100,blank=True,null=True)
    series=models.CharField(max_length=100,blank=True,null=True)
    note = models.TextField(blank=True,null=True)
    remark = models.TextField(blank=True,null=True)
    keywords = models.TextField(blank=True,null=True)
    language = models.CharField(max_length=250)
    image = models.ImageField(upload_to='books/book_image',null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, related_name='book_category')
    subject=models.CharField(max_length=250,blank=True,null=True)

    class_no = models.CharField(max_length=30, unique=True)

    library=models.ForeignKey(Library,null=True,blank=True,on_delete=models.CASCADE)
    call_no = models.CharField(max_length=30, null=True, blank=True)
    total_quantity=models.PositiveIntegerField(default=0)
    general_quantity=models.PositiveIntegerField(default=0)
    reference_quantity=models.PositiveIntegerField(default=0)

    qr_code = models.ImageField(null=True, blank=True, upload_to='books/book_qr_image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    type=models.CharField(max_length=20,choices=TYPE,default='Book')
    isbn = models.IntegerField(unique=True,null=True,blank=True)
    media_type=models.CharField(max_length=255,null=True,blank=True)
    issn = models.IntegerField(unique=True,null=True,blank=True)
    
    class Meta:
        ordering=['-id']

    def __str__(self):
        return self.title

@receiver(post_save, sender=Books)
def postsave_data(sender, instance, created, *args, **kwargs):
    if created:
        try:
            # import pdb;pdb.set_trace()
            a = instance.class_no
            if instance.publication is not None:
                b = instance.publication.name[0:3].upper()
            elif instance.publication is None and instance.author is not None:
                b = instance.author.lastname[0:3].upper()
            c = instance.title.split()
            if c[0].upper() == 'A' or c[0].upper() == 'AN' or c[0].upper() == 'THE':
                d = c[1][0:1].lower()
            else:
                d=c[0][0-1].lower()
            e = instance.edition
            if instance.volume is not None:
                f = instance.volume
            else:
                f = ""
            instance.call_no = f'{a} {b}-{d} {e} {f}'
            instance.save()
        except Exception as e:
            print("error occured:::: ", e)

class AddBook(models.Model):
    book=models.ForeignKey(Books, on_delete=models.CASCADE, related_name='book_transaction')
    general_quantity=models.PositiveIntegerField(default=0)
    reference_quantity=models.PositiveIntegerField(default=0)
    added_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    added_at=models.DateTimeField(auto_now_add=True)


gender_choice = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Others', 'Others'),
)
profile_status_choice = (
    ('pending', 'pending'),
    ('approved', 'approved'),
    ('rejected', 'rejected'),
)
user_type_choice = (
    ('Student', 'Student'),
    ('Staff', 'Staff'),
    ('Faculty', 'Faculty'),
    ('Public', 'Public'),
)
member_status=(
    ('Active', 'Active'),
    ('Suspended', 'Suspended'),
    ('Expired', 'Expired'),
)

def get_membership_expiry():
    return timezone.now() + timedelta(days=365)
class LibraryProfile(models.Model):
    user_type = models.CharField(max_length=30, choices=user_type_choice)
    member=models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='library_member_details', null=True, blank=True)
    library=models.ForeignKey(Library,on_delete=models.Model,null=True,blank=True)
    membership_status=models.CharField(max_length=30, choices=member_status, default='Active')
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=profile_status_choice, default='pending')
    user_photo = models.ImageField(upload_to = 'books/libraryprofile/', null=True, blank=True)
    permanent_address = models.CharField(max_length=300)
    temporary_address = models.CharField(max_length=300)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=200)
    telephone_no = models.CharField(max_length=15, null=True, blank=True)
    mobile_no = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=30, choices=gender_choice)
    occupation = models.CharField(max_length=300)
    birth_of_date = models.DateField()
    subject = models.CharField(max_length=300, null=True, blank=True)
    academic_year = models.CharField(max_length=20, null=True, blank=True)
    faculty = models.CharField(max_length=100, null=True, blank=True)
    roll_no = models.CharField(max_length=100, null=True, blank=True)
    library_card_no = models.CharField(max_length=100, null=True, blank=True)
    membership_started_at = models.DateTimeField(default=timezone.now)
    membership_ended_at = models.DateTimeField(default=get_membership_expiry)
    # OPAC_id = models.CharField(max_length=100, null=True, blank=True)
    # OPAC_password = models.CharField(max_length=100, null=True, blank=True)
    qr_code = models.ImageField(null=True, blank=True, upload_to='books/library_profile_qr_image')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=250, blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.CharField(max_length=250, blank=True, null=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    rejected_remarks = models.CharField(max_length=500, null=True, blank=True)
    overdue_count=models.PositiveIntegerField(default=0)
    borrowed_books = models.PositiveIntegerField(default=0)
    hold_books = models.PositiveIntegerField(default=0)
    remainingfine=models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.first_name + self.middle_name + self.last_name

class UniqueBook(models.Model):
    SINGLE_BOOK_STATUS = (
        ('Hold', 'Hold'),
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
        ('Renewed', 'Renewed'),
        ('Idle', 'Idle'),
        ('Acquired','Acquired')
    )
    SINGLE_BOOK_SECTION = (
        ('Reference', 'Reference'),
        ('General', 'General'),
    )
    book=models.ForeignKey(Books, on_delete=models.CASCADE, related_name='unique_book_detail')
    accession_no = models.CharField(max_length=30, null=True, blank=True)
    qr_code = models.ImageField(null=True, blank=True, upload_to='books/book_qr_image')
    book_status = models.CharField(max_length=30, choices=SINGLE_BOOK_STATUS, default='Idle')
    section = models.CharField(max_length=30, choices=SINGLE_BOOK_SECTION, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    book_hold_by=models.ForeignKey(LibraryProfile,on_delete=models.CASCADE,null=True,blank=True,related_name="book_hold")
    book_borrow_by=models.ForeignKey(LibraryProfile,on_delete=models.CASCADE,null=True,blank=True,related_name="book_borrow")
    expirydate = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.accession_no

def get_expiry():
    return datetime.now() + timedelta(days=7)


book_status = (
    ('borrowed', 'borrowed'), #borrowed
    ('returned', 'returned'), #returned
    ('renewed', 'renewed'),  #renewed
)

class BookLoan(models.Model):
    member=models.ForeignKey('LibraryProfile', on_delete=models.CASCADE, related_name='book_loan_member_details')
    book = models.ManyToManyField(UniqueBook, related_name='uniquebook_loan_details')
    issue_date = models.DateTimeField(auto_now_add=True)
    expirydate = models.DateTimeField(default=get_expiry)
    class Meta:
            verbose_name_plural = 'tbl_bookloan'
    
class BookReturn(models.Model):
    member=models.ForeignKey(LibraryProfile, on_delete=models.CASCADE, related_name='return_member')
    book = models.ForeignKey(UniqueBook, related_name='return_loan',on_delete=models.CASCADE)
    return_date = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=BookReturn)
def postsave_data(sender, instance, created, *args, **kwargs):     
    try:
        if created:
            for x in Schedular.objects.filter(book=instance.book):
                cancel_task(x)
                x.delete()
    except Exception:
        return JsonResponse({"success":"false"})
class FinePayment(models.Model):
    member=models.ForeignKey(LibraryProfile, on_delete=models.CASCADE, related_name='fine_member')
    amount=models.PositiveIntegerField(default=0)

class BookRenew(models.Model):
    member=models.ForeignKey(LibraryProfile, on_delete=models.CASCADE, related_name='renewbook_member')
    book = models.ForeignKey(UniqueBook, related_name='book_renew',on_delete=models.CASCADE)
    renew_date = models.DateTimeField(auto_now_add=True)
    expiry_date=models.DateTimeField()

@receiver(post_save, sender=BookRenew)
def postsave_data(sender, instance, created, *args, **kwargs):     
    try:
        if created:
            for x in Schedular.objects.filter(book=instance.book):
                cancel_task(x)
                x.delete()
                predue_schedule(x,instance)
                overdue_schedule(x,instance)
    except Exception:
        return JsonResponse({"success":"false"})
        
from .tasks import email_member_overdue,email_member_predue
from datetime import datetime, timedelta
import arrow
import redis

def predue_schedule(book,instance):
    member=instance.member
    review_time = arrow.get(instance.expirydate) - timedelta(days=1)
    now = arrow.now()
    milli = (review_time - now).total_seconds()
    milli_to_wait =  milli * 1000
    result = email_member_predue.send_with_options(
            args = (member.email),
            delay = milli_to_wait 
            )
    Schedular.objects.create(book=book,sch_type="Predue",task_id=result.options['redis_message_id'])

def cancel_task(instance):
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.hdel("dramatiq:default.DQ.msgs", instance.task_id)

def overdue_schedule(book,instance):
    member=instance.member
    overdue_period = member.library.overdue_period
    now = arrow.now()
    overdue_count = member.library.max_number_of_overdue
    for x in range(overdue_count):
        multiplier=(x-1)*overdue_period
        review_time = arrow.get(instance.expirydate) + timedelta(days=multiplier)
        milli = (review_time - now).total_seconds()
        milli_to_wait =  milli * 1000
        result = email_member_overdue.send_with_options(
            args = (member.id),
            delay = milli_to_wait 
            )
        Schedular.objects.create(book=book,sch_type="Overdue",task_id=result.options['redis_message_id'])

from django.db import transaction
def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))
    return inner

@receiver(m2m_changed,sender=BookLoan.book.through)
@on_transaction_commit
def schedule_logic(sender, instance, **kwargs):
    try:
        for x in instance.book.all():
            predue_schedule(x,instance)
            overdue_schedule(x,instance)
    except Exception:
        return JsonResponse({"success":"false"})
class Schedular(models.Model):
    book=models.ForeignKey(UniqueBook,on_delete=models.CASCADE)
    sch_type=models.CharField(max_length=100, choices=book_status, default='Predue')
    task_id=models.CharField(max_length=50, blank=True, editable=False)

book_reservation_status = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'), 
)
class BookReservation(models.Model):
    member=models.ForeignKey('LibraryProfile', on_delete=models.CASCADE, related_name='book_member_details', null=True, blank=True,)
    book = models.ManyToManyField(UniqueBook, related_name='library_books', through='ReservedBooks')
    book_status = models.CharField(max_length=100, choices=book_reservation_status, default='Pending')
    reservation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=250, blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.CharField(max_length=250, blank=True, null=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    rejected_remarks = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.book_status

class ReservedBooks(models.Model):
    reserve_book = models.ForeignKey(BookReservation, on_delete=models.CASCADE, related_name='book_reserve_details')
    book = models.ForeignKey(UniqueBook, on_delete=models.CASCADE, related_name='books')
    book_status = models.CharField(max_length=100, choices=book_reservation_status, default='Pending')
    reservation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=250, blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.CharField(max_length=250, blank=True, null=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    rejected_remarks = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.status

TRANSACTION=(
    ("Return","Return"),
    ("Renew","Renew"),
)


