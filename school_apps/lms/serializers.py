from attr import field
from django.db.models import fields
from .models import *
from rest_framework import serializers
from student_management_app.api.serializers import CustomUserSerializer, ExtraUserSerializer, StaffSerializer, StudentSerializer

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = "__all__"   
        read_only_fields=['call_no','total_quantity','qr_code',] 

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__" 

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__" 

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = "__all__"  

class AddBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddBook
        fields = "__all__" 

class UniqueBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueBook
        fields = "__all__"    

class BorrowedBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLoan.book.through
        fields = "__all__"    
class BookCategorySerializer(serializers.ModelSerializer):
    book_category = BookSerializer(many=True, read_only=True)
    class Meta:
        model = BookCategory
        fields = "__all__"

    def get_book_category(self, obj):
        try:
           c = Books.objects.filter(category=obj.id)
           return BookSerializer(c).data
        except (Books.DoesNotExist, AttributeError) as e:
            return []

class BookIssueSerializer(serializers.ModelSerializer):
    # book = serializers.SerializerMethodField()
    class Meta:
        model = BookLoan
        fields = '__all__' 

    def get_book(self,obj):
        book = obj.book
        return UniqueBookSerializer(book,many=True).data

class LibraryProfileFineSerializer(serializers.Serializer):
    fine=serializers.CharField()
    class Meta:
        fields=['fine']

class LibraryProfileSeralizer(serializers.ModelSerializer):
    class Meta:
        model = LibraryProfile
        fields = '__all__'
        read_only_fields=['approved_by','approved_at','rejected_by','rejected_at','hold_books','qr_code','membership_status','status','membership_started_at','membership_ended_at','rejected_remarks','overdue_count']
class LibraryProfileVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryProfile
        fields = ['status'] 
class LibraryProfileRenewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryProfile
        fields = ['membership_ended_at'] 

class BookReservationSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()
    class Meta:
        model = BookReservation
        fields = '__all__' 
        read_only_fields=['created_at','book_status','approved_by','approved_at','rejected_by','rejected_at','rejected_remarks']

    def get_book(self,obj):
        book = obj.book
        return UniqueBookSerializer(book,many=True).data

class BookReservationAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReservation
        fields = ['book_status',"rejected_remarks",'approved_by','approved_at','rejected_by','rejected_at',] 
        read_only_fields=['approved_by','approved_at','rejected_by','rejected_at']


class BookReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReturn
        fields = "__all__"

class FinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinePayment
        fields = "__all__"

class BookRenewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRenew
        fields = "__all__"