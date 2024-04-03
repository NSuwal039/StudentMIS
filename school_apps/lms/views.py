from telnetlib import STATUS
from django.db import connection
from django.db.models.query import QuerySet
from django.shortcuts import render
from numpy import save

from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.http import FileResponse
import pandas as pd
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status as drf_status
import datetime
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# '''email verification import'''
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core import mail
from django.utils.html import strip_tags
from rest_framework.authtoken.models import Token

page_count = 10

def page_serializer(paginator, page_obj, page, data):
    serialized_data = {
        'count' : paginator.count,
        'current_page' : int(page),
        'total_pages' : paginator.num_pages,
        'has_prevous_page' : page_obj.has_previous(),
        'has_next_page' : page_obj.has_next(),
        'data' : data
    }
    
    return serialized_data

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page'

book_status_values = {
    '0':'borrowed', #borrowed
    '1':'returned', #returned
    '2':'renewed',  #renewed
}

blank_json0 = {
    'category_name': '',
    'slug': '',
    'description': '',
    'cat_image': '',
    'created_at': '',
    'updated_at': '',
    'book_category': {
        'id': '',
        'title': '',
        'author': '',
        'summary': '',
        'isbn': '',
        'category': '',
        'language': '',
        'quantity': '',
        'image': '',
        'qr_code': '',
        'receive_quantity': '',
        'price': '',
        'created_at': '',
        'updated_at': '',

    }
}
@api_view(['GET'])
def get_book_category_csv(request):
    queryset = BookCategory.objects.all()
    if request.GET.get('start_date'):
        start_date = request.GET.get('start_date').replace('T',' ')
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__gte=start_date)
    if request.GET.get('end_date'):
        end_date = request.GET.get('end_date').replace('T',' ')
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__lte=end_date)
    
    if request.GET.get('category_name'):
        category_name = request.GET.get('category_name')
        queryset = queryset.filter(category_name__icontains=category_name)

    serializer = BookCategorySerializer(queryset, many=True)
    output = serializer.data
    output.insert(0, blank_json0)
    df = pd.json_normalize(output)
    df.rename(columns={
        'category_name': 'Book Category Name',
        'slug': 'Category Slug Name',
        'description': 'Category Description',
        'cat_image': 'Category Image Name',
        'created_at': 'Category Created At',
        'updated_at': 'Category Updated At',
        'book_category.title': 'Book Title',
        'book_category.author': 'Book Author',
        'book_category.summary': 'Book Summary',
        'book_category.isbn': 'Book ISBN',
        'book_category.category': 'Book Category',
        'book_category.image': 'Book Image Name',
        'book_category.qr_code': 'Book QR Image',
        'book_category.receive_quantity': 'Addtional Quantity',
        'book_category.price': 'Book Price',
        'book_category.created_at': 'Book Created At',
        'book_category.updated_at': 'Book Updated At',
    }, inplace=True)
    df = df[[
        'Book Category Name',
        'Category Slug Name',
        'Category Description',
        'Category Image Name',
        'Category Created At',
        'Category Updated At',
        'Book Title',
        'Book Author',
        'Book Summary',
        'Book ISBN',
        'Book Category',
        'Book Image Name',
        'Book QR Image',
        'Addtional Quantity',
        'Book Price',
        'Book Created At',
        'Book Updated At',
        ]
    ]
    df = df.drop([0])
    csv_file = df.to_csv(index=False)
    # return Response(serializer.data)
    response = FileResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=book-category-report.csv"
    return response

class BookCategoryViewset(viewsets.ModelViewSet):
    queryset = BookCategory.objects.all().order_by("-created_at")   
    serializer_class = BookCategorySerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
    filterset_fields = ['category_name', 'description']
    search_fields = ['category_name', 'description']
    ordering_fields = ['id']
    pagination_class = StandardPagination


blank_json1 = {
    'id': '',
    'title': '',
    'author': '',
    'summary': '',
    'isbn': '',
    'category': '',
    'language': '',
    'total_quantity': '',
    'quantity': '',
    'image': '',
    'qr_code': '',
    'receive_quantity': '',
    'price': '',
    'created_at': '',
    'updated_at': '',
}

@api_view(['GET'])
def get_books_csv(request):
    queryset = Books.objects.all()
    print('queryset::: ', queryset)
    if request.GET.get('start_date'):
        start_date = request.GET.get('start_date').replace('T',' ')
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__gte=start_date)
    if request.GET.get('end_date'):
        end_date = request.GET.get('end_date').replace('T',' ')
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__lte=end_date)
    
    if request.GET.get('title'):
        title = request.GET.get('title')
        queryset = queryset.filter(title__icontains=title)

    if request.GET.get('author'):
        author = request.GET.get('author')
        queryset = queryset.filter(author__icontains=author)

    if request.GET.get('isbn'):
        isbn = request.GET.get('isbn')
        queryset = queryset.filter(isbn__iexact=isbn)

    if request.GET.get('category'):
        category = request.GET.get('category')
        queryset = queryset.filter(category__icontains=category)

    if request.GET.get('created_at'):
        created_at = request.GET.get('created_at').replace('T',' ')
        created_at = datetime.strptime(created_at,'%Y-%m-%d')
        queryset = queryset.filter(created_at=created_at)    

    serializer = BookSerializer(queryset, many=True)
    output = serializer.data
    output.insert(0, blank_json1)
    df = pd.json_normalize(output)
    df.rename(columns={
        'title': 'Title',
        'author': 'Author',
        'summary': 'Summary',
        'isbn': 'ISBN',
        'category': 'Category',
        'total_quantity': 'Total Quantity',
        'receive_quantity': 'Addtional Quantity',
        'price': 'Price',
        'created_at': 'Created At',
        'updated_at': 'Updated At',
    }, inplace=True)
    df = df[[
        'Title',
        'Author',
        'Summary',
        'ISBN',
        'Category',
        'Total Quantity',
        'Addtional Quantity',
        'Price',
        'Created At',
        'Updated At',
        ]
    ]
    df = df.drop([0])
    csv_file = df.to_csv(index=False)
    # return Response(serializer.data)
    response = FileResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=books-report.csv"
    return response


class LibraryViewset(viewsets.ModelViewSet):
    queryset = Library.objects.all()  
    serializer_class = LibrarySerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )

class AuthorViewset(viewsets.ModelViewSet):
    queryset = Author.objects.all()  
    serializer_class = AuthorSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )

class PublicationViewset(viewsets.ModelViewSet):
    queryset = Publication.objects.all()  
    serializer_class = PublicationSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

class BookViewset(viewsets.ModelViewSet):
    queryset = Books.objects.all().order_by("-created_at")   
    serializer_class = BookSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend,
                        filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type','author','category','publication','call_no']


    def perform_create(self, serializer):
        if self.request.user.has_perm('lms.add_books'):
            objs = serializer.save()
            for x in range(0,objs.general_quantity):
                if UniqueBook.objects.filter(book=objs).exists():
                    b=UniqueBook.objects.filter(book=objs).last().accession_no
                    a=f'{int(b)+1:015}'
                else:
                    a=f'{objs.id:06}{0+1:09}'
                abc=UniqueBook.objects.create(accession_no=a,book=objs,section='General')
                url = get_current_site(self.request).domain
                data=f'{url}/api/unique-book/{abc.accession_no}'
                qr_image = qrcode.make(data)
                qr_offset = Image.new('RGB', (qr_image.size[0], qr_image.size[1]), 'white')
                qr_offset.paste(qr_image)
                file_name = f'{abc.accession_no}-qr.png'
                stream = BytesIO()
                qr_offset.save(stream, 'PNG')
                abc.qr_code.save(file_name, File(stream),save = True)
                qr_offset.close()
            for x in range(0,objs.reference_quantity):
                if UniqueBook.objects.filter(book=objs).exists():
                    b=UniqueBook.objects.filter(book=objs).last().accession_no
                    a=f'{int(b)+1:015}'
                else:
                    a=f'{objs.id:06}{0+1:09}'
                abc=UniqueBook.objects.create(accession_no=a,book=objs,section='Reference')
                url = get_current_site(self.request).domain
                data=f'{url}/api/unique-book/{abc.accession_no}'
                qr_image = qrcode.make(data)
                qr_offset = Image.new('RGB', (qr_image.size[0], qr_image.size[1]), 'white')
                qr_offset.paste(qr_image)
                file_name = f'{abc.accession_no}-qr.png'
                stream = BytesIO()
                qr_offset.save(stream, 'PNG')
                abc.qr_code.save(file_name, File(stream),save = True)
                qr_offset.close()
            objs.total_quantity=objs.general_quantity + objs.reference_quantity
            objs.save()
            return Response(serializer.data, status=drf_status.HTTP_201_CREATED)
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)

class AddBookViewset(viewsets.ModelViewSet):
    queryset=AddBook.objects.all()
    serializer_class = AddBookSerializer
    authentication_classes=(TokenAuthentication,SessionAuthentication)
    permission_classes=(IsAuthenticated,)

    def perform_create(self, serializer):
        if self.request.user.has_perm('lms.add_addbook'):
            objs = serializer.save()
            b=UniqueBook.objects.filter(book=objs.book).last().accession_no
            a=f'{int(b)+1:015}'
            for x in range(0,objs.general_quantity):
                abc=UniqueBook.objects.create(accession_no=a,book=objs.book,section='General')
                url = get_current_site(self.request).domain
                data=f'{url}/api/unique-book/{abc.accession_no}'
                qr_image = qrcode.make(data)
                qr_offset = Image.new('RGB', (qr_image.size[0], qr_image.size[1]), 'white')
                qr_offset.paste(qr_image)
                file_name = f'{abc.accession_no}-qr.png'
                stream = BytesIO()
                qr_offset.save(stream, 'PNG')
                abc.qr_code.save(file_name, File(stream),save = True)
                qr_offset.close()
            for x in range(0,objs.reference_quantity):
                abc=UniqueBook.objects.create(accession_no=a,book=objs.book,section='Reference')
                url = get_current_site(self.request).domain
                data=f'{url}/api/unique-book/{abc.accession_no}'
                qr_image = qrcode.make(data)
                qr_offset = Image.new('RGB', (qr_image.size[0], qr_image.size[1]), 'white')
                qr_offset.paste(qr_image)
                file_name = f'{abc.accession_no}-qr.png'
                stream = BytesIO()
                qr_offset.save(stream, 'PNG')
                abc.qr_code.save(file_name, File(stream),save = True)
                qr_offset.close()
            book=Books.objects.get(id=objs.book.id)
            book.general_quantity += objs.general_quantity
            book.reference_quantity += objs.reference_quantity
            total_quantity=objs.general_quantity + objs.reference_quantity
            book.total_quantity += total_quantity
            book.save()
            return Response(serializer.data, status=drf_status.HTTP_201_CREATED)
        
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)

class UniqueBookViewset(viewsets.ModelViewSet):
    queryset = UniqueBook.objects.all().order_by("-created_at")   
    serializer_class = UniqueBookSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['book','book_status','section','accession_no','book_borrow_by','book_hold_by']
    lookup_field='accession_no'

blank_json2 = {
    'id': '',
    'book_issue': '',
    'book': '',
    'status': '',
    'issue_date': '',
    'return_date': '',
    'expirydate': '',
    'fine_per_book': '',
    'days': '',
    'fine_per_day': '',
    'renewal_date': '',
}

@api_view(['GET'])
def get_book_issues_csv(request):
    queryset = borrowed_books.objects.all()
    print('queryset::: ', queryset)
    if request.GET.get('start_date'):
        start_date = request.GET.get('start_date').replace('T',' ')
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__gte=start_date)
    if request.GET.get('end_date'):
        end_date = request.GET.get('end_date').replace('T',' ')
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__lte=end_date)
    
    if request.GET.get('member'):
        member = request.GET.get('member')
        queryset = queryset.filter(member__icontains=member)

    if request.GET.get('book'):
        book = request.GET.get('book')
        queryset = queryset.filter(book__icontains=book)

    if request.GET.get('issue_date'):
        issue_date = request.GET.get('issue_date').replace('T',' ')
        issue_date = datetime.strptime(issue_date,'%Y-%m-%d')
        queryset = queryset.filter(issue_date=issue_date)   

    if request.GET.get('return_date'):
        return_date = request.GET.get('return_date').replace('T',' ')
        return_date = datetime.strptime(return_date,'%Y-%m-%d')
        queryset = queryset.filter(return_date=return_date)    

    if request.GET.get('expirydate'):
        expirydate = request.GET.get('expirydate').replace('T',' ')
        expirydate = datetime.strptime(expirydate,'%Y-%m-%d')
        queryset = queryset.filter(expirydate=expirydate) 

    if request.GET.get('renewal_date'):
        renewal_date = request.GET.get('renewal_date').replace('T',' ')
        renewal_date = datetime.strptime(renewal_date,'%Y-%m-%d')
        queryset = queryset.filter(renewal_date=renewal_date) 

    serializer = BorrowedBooksSerializer(queryset, many=True)
    output = serializer.data
    output.insert(0, blank_json2)
    df = pd.json_normalize(output)
    df.rename(columns={
        'book_issue': 'Book Issue ID',
        'book': 'Book Name',
        'status': 'Status',
        'return_date': 'Return Date',
        'expirydate': 'Expiry Date',
        'fine_per_book': 'Fine/Book',
        'days': 'Days',
        'fine_per_day': 'Fine/Day',
        'renewal_date': 'Renewal Date',
    }, inplace=True)
    df = df.drop([0])
    # df['Member Name'] = [ CustomUser.objects.get(id=i).full_name for i in df['Member ID']]
    # df['Book Name'] = [ Books.objects.filter(id=i).title for i in df['Book Name']]
    df = df[[
        'Book Issue ID',
        'Book Name',
        'Status',
        'Return Date',
        'Expiry Date',
        'Fine/Book',
        'Days',
        'Fine/Day',
        'Renewal Date',
        ]
    ]
    df['Book Name'] = [ Books.objects.filter(title=c) for c in df["Book Name"].values]
    csv_file = df.to_csv(index=False)
    # return Response(serializer.data)
    response = FileResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=book-issues-report.csv"
    return response

class BookIssueViewset(viewsets.ModelViewSet):
    queryset = BookLoan.objects.all()  
    serializer_class = BookIssueSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        if request.user.has_perm('lms.add_bookloan'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            books=serializer.validated_data['book']
            length=len(books)
            bb=serializer.validated_data['member'].borrowed_books
            if serializer.validated_data['member'].user_type == 'Student':
                max_borrow=serializer.validated_data['member'].library.student_max_borrow
            elif serializer.validated_data['member'].user_type == 'Staff':
                max_borrow=serializer.validated_data['member'].library.staff_max_borrow
            elif serializer.validated_data['member'].user_type == 'Faculty':
                max_borrow=serializer.validated_data['member'].library.faculty_max_borrow
            else:
                max_borrow=serializer.validated_data['member'].library.public_max_borrow
            difference=max_borrow-length-bb
            if difference >= 0:
                book_issue = serializer.save(issue_date = timezone.now())
                mem=book_issue.member
                mem.borrowed_books+=length
                mem.save()
                for item in books:
                    # import pdb;pdb.set_trace()
                    item.expirydate=book_issue.expirydate
                    item.book_status='Borrowed'
                    item.book_borrow_by=book_issue.member
                    item.save()
                    book_issue.book.add(item.id)
                try:
                    mail_subject = "Book Issued Details"
                    html_message = render_to_string("email_sending/book_issue_email.html", {
                        'user': book_issue.member,
                        'book_issued_date': book_issue.issue_date,
                        'book_expiry_date': book_issue.expirydate,
                        'book_status': "Borrowed",
                        'books': book_issue.book.all(),
                    })
                    from_email = 'nirmalpandey27450112@gmail.com'
                    to_email = book_issue.member.email
                    plain_message = strip_tags(html_message)
                    mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
                except Exception as e:
                    print("error occured::: {}".format(e))
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=drf_status.HTTP_201_CREATED, headers=headers)
            else:
                diff=abs(difference)
                return Response({"error": f"Borrow Limit Exceeded.{diff} more items than limit"}, status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)


    # @action(detail=True, methods=['GET', 'PATCH'],  url_path='return')
    # def book_return(self, request, pk=None):
    #     if request.user.has_perm('lms.view_bookissue') and request.user.has_perm('lms.change_bookissue'):
    #         book_detail = self.get_object()
    #         emp_list = []
    #         for item in request.data['book_id']:
    #             temp_obj = borrowed_books.objects.get(book_issue = book_detail, book = UniqueBook.objects.get(pk=item))
    #             temp_obj.status = 'returned'
    #             print("get total quantity::: ", temp_obj)
    #             # import pdb; pdb.set_trace()
    #             temp_obj.book.book.total_quantity += 1
    #             temp_obj.return_date = timezone.now()
    #             temp_obj.book.save()
    #             temp_obj.save()
    #             if temp_obj.return_date > temp_obj.expirydate:
    #                 temp_obj.days = temp_obj.return_date - temp_obj.expirydate
    #                 temp_obj.fine_per_day = item['fine_per_day']
    #                 temp_obj.fine_per_book += temp_obj.days * temp_obj.fine_per_day
    #                 temp_obj.save()
    #             emp_list.append(temp_obj)
                
    #         try:
    #             mail_subject = "Book Returned Details"
    #             html_message = render_to_string("email_sending/book_return_email.html", {
    #                 'user': book_detail.member,
    #                 'book_list': emp_list,
    #             })
    #             from_email = 'nirmalpandey27450112@gmail.com'
    #             to_email = book_detail.member.email
    #             plain_message = strip_tags(html_message)
    #             mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
    #             print("email send sucessfully!")
    #         except Exception as e:
    #             print("error occured::: {}".format(e))

    #         for item in emp_list:
    #             # print("fine fff:::", item.fine_per_book)
    #             item.fine_per_book += item.fine_per_book
    #         book_detail.total_fine = item.fine_per_book
    #         # print('fine total::: ',book_detail.total_fine )
    #         book_detail.save()

    #         return Response(BookIssueSerializer(book_detail).data, status=drf_status.HTTP_200_OK)

    #     else:
    #         return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=True, methods=['GET', 'PATCH'],  url_path='renew')
    # def book_renew(self, request, *args, **kwargs):
    #     if request.user.has_perm('lms.view_bookissue') and request.user.has_perm('lms.change_bookissue'):
    #         book_detail = self.get_object()
    #         print("Getting Book Detail::: ", book_detail)
    #         emp_list = []
    #         for item in request.data['book_id']:
    #             temp_obj = borrowed_books.objects.get(book_issue = book_detail, book = UniqueBook.objects.get(pk=item))
    #             temp_obj.status = 'renewed'
    #             temp_obj.renewal_date = timezone.now()
    #             temp_obj.expirydate = timezone.now() + timedelta(days=7)
    #             temp_obj.save()
    #             emp_list.append(temp_obj)
                
    #         try:
    #             mail_subject = "Book Renew Details"
    #             html_message = render_to_string("email_sending/book_renewal_email.html", {
    #                 'user': book_detail.member,
    #                 'book_list': emp_list,
    #             })
    #             from_email = 'nirmalpandey27450112@gmail.com'
    #             to_email = book_detail.member.email
    #             plain_message = strip_tags(html_message)
    #             mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
    #             print("email send sucessfully!")
    #         except Exception as e:
    #             print("error occured::: {}".format(e))
    #         return Response(BookIssueSerializer(book_detail).data, status=drf_status.HTTP_200_OK)
        
    #     else:
    #         return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     print(serializer.initial_data)
    #     serializer.is_valid(raise_exception=True)
    #     id = kwargs['pk']
    #     b = BookIssue.objects.get(id=id)
    #     if request.data["action"] == "edit":
    #         serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #         serializer.is_valid(raise_exception=True)
    #         self.perform_update(serializer)
    #         return Response(serializer.data, status=drf_status.HTTP_200_OK)

        # if request.data['action'] == 'return':
        #     book_issue = serializer.save()
        #     print("member::: ", request.user)
        #     print("Issued Book Name::: ", book_issue.book)
        #     print("logged user email::: ", book_issue.member.email)
        #     book = book_issue.book
        #     book.total_quantity += 1
        #     book.save()
        #     b.status = request.data['status']
        #     b.return_date = timezone.now()
        #     return_date = b.return_date
        #     print("return date::: ", type(return_date))
        #     print("return date::: ", return_date)
        #     b.days = request.data['days']
        #     b.fine_per_day = request.data['fine_per_day']
        #     b.total_fine = b.days * b.fine_per_day
        #     # if return_date > book_expiry:
        #     #     days_count = (return_date - book_expiry).days
        #     #     b.fine = 15 * days_count
        #     # else:
        #     #     b.fine = 0
            
        #     b.save()
        #     user = book_issue.member
        #     user_email = book_issue.member.email
        #     book_name = book_issue.book
        #     print("book_name::: ", book_name)
        #     book_status = book_issue.status
        #     book_issued_date = book_issue.issue_date
        #     book_expiry_date = book_issue.expirydate
            # try:
            #     mail_subject = "Book Returned Details"
            #     html_message = render_to_string("email_sending/book_issue_email.html", {
            #         'user': user,
            #         'book_name': book_name,
            #         'book_issued_date': book_issued_date,
            #         'book_expiry_date': book_expiry_date,
            #         'book_status': book_status,
            #     })
            #     from_email = 'nirmalpandey27450112@gmail.com'
            #     to_email = user_email
            #     plain_message = strip_tags(html_message)
            #     mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
            #     print("email send sucessfully!")
            # except Exception as e:
            #     print("error occured::: {}".format(e))
        # return Response(BookIssueSerializer(b).data, status=drf_status.HTTP_200_OK)

# class BookRenewViewset(viewsets.ModelViewSet):
#     queryset = BookRenew.objects.all()  
#     serializer_class = BookRenewSeralizer
#     authentication_classes = (TokenAuthentication, SessionAuthentication)
#     permission_classes = (IsAuthenticated, )


#     def list(self, request, *args, **kwargs):
#         queryset = BookRenew.objects.all() 
        
#         if request.GET.get('book_issue.title'):
#             title = request.GET.get('title')
#             queryset = self.queryset.filter(title__icontains=title)

#         if request.GET.get('renewal_at'):
#             renewal_at = request.GET.get('renewal_at').replace('T',' ')
#             renewal_at = datetime.strptime(renewal_at,'%Y-%m-%d')
#             queryset = queryset.filter(renewal_at=renewal_at)    
        
#         self._datatables_filtered_count = len(queryset)
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             serialized_data = serializer.data
#             return self.get_paginated_response(serialized_data)

#         serializer = self.get_serializer(queryset, many=True)
#         serialized_data = serializer.data
#         return Response(serialized_data)

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         id = kwargs['pk']
#         b = BookRenew.objects.get(id=id)
#         if request.data["action"] == "edit":
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             return Response(serializer.data, status=drf_status.HTTP_200_OK)

#         if request.data['action'] == 'renew':
#             book_renew = serializer.save()
#             print("Renew Book Name::: ", book_renew.book_issue.book)
#             b.book_issue.expirydate = timezone.now() + timedelta(days=1)
#             print("new book expiry date::: ", b.book_issue.expirydate)
#             b.renewal_at = timezone.now()
#             print(b.renewal_at)
#             b.save()
#             user = book_renew.member
#             user_email = book_renew.member.email
#             book_name = book_renew.book
#             print("book_name::: ", book_name)
#             book_status = book_renew.status
#             book_issued_date = book_renew.issue_date
#             book_renewal_at = book_renew.renewak_at
#             book_expiry_date = book_renew.expirydate
#             try:
#                 mail_subject = "Book Returned Details"
#                 html_message = render_to_string("email_sending/book_renewal_email.html", {
#                     'user': user,
#                     'book_name': book_name,
#                     'book_issued_date': book_issued_date,
#                     'book_expiry_date': book_expiry_date,
#                     'book_renewal_at': book_renewal_at,
#                     'book_status': book_status,
#                 })
#                 from_email = 'nirmalpandey27450112@gmail.com'
#                 to_email = user_email
#                 plain_message = strip_tags(html_message)
#                 mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
#                 print("email send sucessfully!")
#             except Exception as e:
#                 print("error occured::: {}".format(e))
#             return Response(BookRenewSeralizer(b).data, status=drf_status.HTTP_200_OK)


blank_json3 = {
    'id': '',
    "book_issue_member_details": {
        "id": "",
        "book": {
            "id": "",
            "book": {
                "id": "",
                "title": "",
                "author": "",
                "summary": "",
                "isbn": "",
                "category": {
                    "id": "",
                    "category_name": "",
                    "description": "",
                    "summary": "",
                    "created_at": "",
                    "updated_at": "",
                },
                "language": "",
                "receive_quantity": "",
                "price": "",
                "created_at": "",
                "updated_at": "",
            },
            "status": "",
            "total_fine": "",
            "issue_date": "",
            "return_date": "",
            "expirydate": "",
            "task_id": "",
            "renewal_date": "",
        },
        "status": "",
        "total_fine": "",
        "issue_date": "",
        "return_date": "",
        "expirydate": "",
        "task_id": "",
        "renewal_date": "",
    },
    'user_type': '',
    'member': '',
    'first_name': '',
    'middle_name': '',
    'last_name': '',
    'permanent_address': '',
    'temporary_address': '',
    'country': '',
    'city': '',
    'telephone_no': '',
    'mobile_no': '',
    'email': '',
    'gender': '',
    'occupation': '',
    'birth_of_date': '',
    'roll_no': '',
    'library_card_no': '',
    'membership_started_at': '',
    'membership_ended_at': '',
    'created_at': '',
    'borrowed_books': '',
}

@api_view(['GET'])
def get_library_profile_csv(request):
    queryset = LibraryProfile.objects.all()
    print('queryset::: ', queryset)
    if request.GET.get('start_date'):
        start_date = request.GET.get('start_date').replace('T',' ')
        start_date = datetime.strptime(start_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__gte=start_date)
    if request.GET.get('end_date'):
        end_date = request.GET.get('end_date').replace('T',' ')
        end_date = datetime.strptime(end_date,'%Y-%m-%d')
        queryset = queryset.filter(created_at__lte=end_date)
    
    if request.GET.get('member'):
        member = request.GET.get('member')
        queryset = queryset.filter(member__icontains=member)

    if request.GET.get('first_name'):
        first_name = request.GET.get('first_name')
        queryset = queryset.filter(first_name__icontains=first_name)

    if request.GET.get('middle_name'):
        middle_name = request.GET.get('middle_name')
        queryset = queryset.filter(middle_name__icontains=middle_name)

    if request.GET.get('last_name'):
        last_name = request.GET.get('last_name')
        queryset = queryset.filter(last_name__icontains=last_name)

    if request.GET.get('email'):
        email = request.GET.get('email')
        queryset = queryset.filter(email__icontains=email)

    if request.GET.get('membership_started_at'):
        membership_started_at = request.GET.get('membership_started_at').replace('T',' ')
        membership_started_at = datetime.strptime(membership_started_at,'%Y-%m-%d')
        queryset = queryset.filter(membership_started_at=membership_started_at)   

    if request.GET.get('membership_ended_at'):
        membership_ended_at = request.GET.get('membership_ended_at').replace('T',' ')
        membership_ended_at = datetime.strptime(membership_ended_at,'%Y-%m-%d')
        queryset = queryset.filter(membership_ended_at=membership_ended_at)    

    serializer = LibraryProfileSeralizer(queryset, many=True)
    output = serializer.data
    output.insert(0, blank_json3)
    df = pd.json_normalize(output)
    df.rename(columns={
        'book_issue_member_details.book.book.title': 'Book Title',
        'book_issue_member_details.book.book.isbn': 'Book ISBN',
        'book_issue_member_details.book.book.category.category_name': 'Book Category',
        'book_issue_member_details.book.book.language': 'Book Language',
        'book_issue_member_details.book.book.price': 'Book Price',
        'book_issue_member_details.book.status': 'Book Status',
        'book_issue_member_details.book.total_fine': 'Total Fine',
        'book_issue_member_details.book.issue_date': 'Book Issued Date',
        'book_issue_member_details.book.return_date': 'Book Returned Date',
        'book_issue_member_details.book.renewal_date': 'Book Renewal Date',
        'user_type': 'User Type',
        'member': 'Member',
        'first_name': 'First Name',
        'middle_name': 'Middle Name',
        'last_name': 'Last Name',
        'permanent_address': 'Permanent Address',
        'temporary_address': 'Temporary Address',
        'country': 'Country',
        'city': 'City',
        'telephone_no': 'Telephone No.',
        'mobile_no': 'Mobile No.',
        'email': 'Email Address',
        'gender': 'Gender',
        'occupation': 'Occupation',
        'birth_of_date': 'Birth of Date',
        'roll_no': 'Roll No.',
        'library_card_no': 'Library Card No',
        'membership_started_at': 'Membership Started At',
        'membership_ended_at': 'Membership Ended At',
        'created_at': 'Created At',
    }, inplace=True)
    df = df.drop([0])
    # df['Member Name'] = [ CustomUser.objects.get(id=i).full_name for i in df['Member ID']]
    # df['Book Name'] = [ Books.objects.filter(id=i).title for i in df['Book Name']]
    df = df[[
        'Book Title',
        'Book ISBN',
        'Book Category',
        'Book Language',
        'Book Price',
        'Book Status',
        'Total Fine',
        'Book Issued Date',
        'Book Returned Date',
        'Book Renewal Date',
        'User Type',
        'Member',
        'First Name',
        'Middle Name',
        'Last Name',
        'Permanent Address',
        'Temporary Address',
        'Country',
        'City',
        'Telephone No.',
        'Mobile No.',
        'Email Address',
        'Gender',
        'Occupation',
        'Birth of Date',
        'Roll No.',
        'Library Card No',
        'Membership Started At',
        'Membership Ended At',
        'Created At',
        ]
    ]
    csv_file = df.to_csv(index=False)
    response = FileResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=libray-profile-report.csv"
    return response

class LibraryProfileViewset(viewsets.ModelViewSet):
    queryset = LibraryProfile.objects.all()  
    serializer_class = LibraryProfileSeralizer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type','membership_status','member','status']

    def get_queryset(self):
        expired_objs=self.queryset.filter(membership_ended_at__lt=timezone.now())
        for x in expired_objs:
            x.membership_status='Expired'
            x.save()
        return self.queryset

    def perform_create(self, serializer):
        objs = serializer.save()
        data = str(objs.id) + "\n" + str(str(objs.first_name) + str(objs.middle_name) + str(objs.last_name)) + "\n" + str(objs.email)+ "\n" + str(objs.mobile_no) + "\n" + str(objs.temporary_address)
        qr_image = qrcode.make(data)
        qr_offset = Image.new('RGB', (qr_image.size[0], qr_image.size[1]), 'white')
        qr_offset.paste(qr_image)
        file_name = f'{objs.email}-qr.png'
        stream = BytesIO()
        qr_offset.save(stream, 'PNG')
        objs.qr_code.save(file_name, File(stream),save = True)
        qr_offset.close()
        return Response(serializer.data, status=drf_status.HTTP_201_CREATED)
  
    @action(detail=True, methods=['PUT'],  url_path='profile-verify',serializer_class=LibraryProfileVerifySerializer)
    def profile_verify(self, request,pk=None, *args, **kwargs):
        try:
            objs = self.get_object()
            serializer = self.get_serializer(objs,data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['status'] == 'approved':
                profile = serializer.save(approved_by=request.user.email,approved_at=timezone.now(),status='approved')
                user = profile.member
                full_name = (profile.first_name + ' ' + profile.middle_name + ' ' + profile.last_name) if profile.middle_name is not None else (profile.first_name + ' ' + profile.last_name)
                user_email = profile.email
                try:
                    mail_subject = "Library Profile Activation"
                    html_message = render_to_string("email_sending/profile_activation_email.html", {
                        'user': user,
                        'full_name': full_name,
                    })
                    from_email = 'nirmalpandey27450112@gmail.com'
                    to_email = user_email
                    plain_message = strip_tags(html_message)
                    mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
                except Exception as e:
                    print("error occured::: {}".format(e))
                return Response(LibraryProfileSeralizer(objs).data, status=drf_status.HTTP_200_OK)
            elif serializer.validated_data['status'] == 'rejected':
                profile = serializer.save(rejected_at=timezone.now(),rejected_by=request.user.email,status='rejected')
                user = profile.member
                full_name = (profile.first_name + ' ' + profile.middle_name + ' ' + profile.last_name) if profile.middle_name is not None else (profile.first_name + ' ' + profile.last_name)
                user_email = profile.email
                try:
                    mail_subject = "Library Profile Rejection"
                    html_message = render_to_string("email_sending/profile_rejection_email.html", {
                        'user': user,
                        'full_name': full_name,
                        'rejected_remarks': profile.rejected_remarks,
                    })
                    from_email = 'nirmalpandey27450112@gmail.com'
                    to_email = user_email
                    plain_message = strip_tags(html_message)
                    mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
                except Exception as e:
                    print("error occured::: {}".format(e))
                return Response(LibraryProfileSeralizer(objs).data, status=drf_status.HTTP_200_OK)
            else:
                return Response({"message":"Profile status is still pending"}, status=drf_status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'success':False}, status=drf_status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['PUT'],  url_path='membership-renew',serializer_class=LibraryProfileRenewSerializer)
    def membership_renew(self, request,pk=None, *args, **kwargs):
        try:
            objs = self.get_object()
            serializer = self.get_serializer(objs,data=request.data)
            serializer.is_valid(raise_exception=True)
            if objs.membership_status=='Expired' and serializer.validated_data['membership_ended_at'] is not None:
                obj=serializer.save(membership_started_at=timezone.now(),membership_status="Active") 
                return Response(LibraryProfileSeralizer(objs).data , status=drf_status.HTTP_200_OK) 
            else:
                return Response({"message":"Your Membership is not expired or Membership end date not provided"}, status=drf_status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'success':False}, status=drf_status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=True, methods=['GET'],  url_path='books',serializer_class=UniqueBookSerializer)
    # def loan_books(self, request,pk=None, *args, **kwargs):
    #     try:
    #         objs = self.get_object()
    #         ok=objs.book_borrow.filter(book_status="Borrowed")
    #         # import pdb;pdb.set_trace()
    #         return Response(UniqueBookSerializer(ok).data,status=drf_status.HTTP_200_OK)
    #     except:
    #         return Response({'success':False}, status=drf_status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'],  url_path='acquiredfine')
    def acquired_fine(self, request,pk=None, *args, **kwargs):
        try:
            objs = self.get_object()
            overdue_count=objs.overdue_count
            price_dict={"total_amount":0,"overdue_fine":0}
            library=objs.library
            fine_per_day=library.fines_per_day_per_book
            fine_multiplier=library.maximum_fine_multiplier
            overdue_cost=library.overdue_cost
            overdue_amount=overdue_count*overdue_cost
            price_dict['overdue_fine'] +=overdue_amount
            price_dict['overdue_fine'] +=overdue_amount
            for x in objs.book_borrow.filter(book_status__in=["Borrowed","Renewed"]):
                max_fine=x.book.price*fine_multiplier
                expiry=x.expirydate
                if expiry < timezone.now():
                    expired_time=timezone.now()-expiry
                    expired_days=expired_time.days
                    fine=expired_days*fine_per_day
                    if max_fine <= fine:
                        final=max_fine
                    else:
                        final=fine
                    price_dict[f'{x.book.title}-{x.accession_no}']=final
                    price_dict['total_amount'] +=final
            return Response(price_dict ,status=drf_status.HTTP_200_OK) 
        except:
            return Response({'success':False}, status=drf_status.HTTP_400_BAD_REQUEST)
    
class BookReservationViewset(viewsets.ModelViewSet):
    queryset = BookReservation.objects.all()  
    serializer_class = BookReservationSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        if request.user.has_perm('lms.add_bookreservation'):
            serializer = self.get_serializer(data=request.data)
            id_list = serializer.initial_data['book']
            import json;
            id_array=json.loads(id_list)
            length=len(id_array)
            serializer.is_valid(raise_exception=True)
            bb=serializer.validated_data['member'].hold_books
            if serializer.validated_data['member'].user_type == 'Student':
                max_hold=serializer.validated_data['member'].library.student_max_hold
            elif serializer.validated_data['member'].user_type == 'Staff':
                max_hold=serializer.validated_data['member'].library.staff_max_hold
            elif serializer.validated_data['member'].user_type == 'Faculty':
                max_hold=serializer.validated_data['member'].library.faculty_max_hold
            else:
                max_hold=serializer.validated_data['member'].library.public_max_hold
            difference=max_hold-length-bb
            if difference >= 0:
                book_reserve = serializer.save(created_at = timezone.now())
                for item in id_array:
                    temp_obj = UniqueBook.objects.get(id=item)
                    book_reserve.book.add(temp_obj)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=drf_status.HTTP_201_CREATED, headers=headers)
            else:
                diff=abs(difference)
                return Response({"error": f"Borrow Limit Exceeded.{diff} more items than limit"}, status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT'],  url_path='hold_verify',serializer_class=BookReservationAcceptSerializer)
    def hold_accept(self, request,pk=None, *args, **kwargs):
        try:
            book_reserve = self.get_object()
            serializer = self.get_serializer(book_reserve,data=request.data)
            serializer.is_valid(raise_exception=True)
            length=len(book_reserve.book.all())
            if serializer.validated_data['book_status']=='Accepted':
                obj=serializer.save(approved_by=self.request.user.email,approved_at=timezone.now())
                mem=obj.member
                mem.hold_books+=length
                mem.save()
                for item in book_reserve.book.all():
                        temp_obj = UniqueBook.objects.get(id=item.id)
                        temp_obj.book_status='Hold'
                        temp_obj.book_hold_by=book_reserve.member
                        temp_obj.save()
                try:
                    mail_subject = "Book Reservation Details"
                    html_message = render_to_string("email_sending/book_reserve_email.html", {
                        'user': obj.member,
                        'book_reserved_date': obj.created_at,
                        'book_reservation_date': obj.reservation_date,
                        'book_status': obj.book_status,
                        'books': obj.book.all(),
                    })
                    from_email = 'nirmalpandey27450112@gmail.com'
                    to_email = obj.member.email
                    plain_message = strip_tags(html_message)
                    mail.send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
                except Exception as e:
                    print("error occured::: {}".format(e))   
                return Response(BookReservationSerializer(book_reserve).data, status=drf_status.HTTP_200_OK) 
            elif serializer.validated_data['book_status']=='Rejected':
                serializer.save(rejected_by=self.request.user.email,rejected_at=timezone.now())
                return Response(BookReservationSerializer(book_reserve).data, status=drf_status.HTTP_200_OK)
            else:
                serializer.save()
                return Response(BookReservationSerializer(book_reserve).data, status=drf_status.HTTP_200_OK)
        except:
            return Response({'success':False}, status=drf_status.HTTP_400_BAD_REQUEST)



class BookReturnViewset(viewsets.ModelViewSet):
    queryset = BookReturn.objects.all()  
    serializer_class =BookReturnSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if request.user.has_perm('lms.add_bookreturn'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['book'] in serializer.validated_data['member'].book_borrow.filter(book_status__in=["Borrowed","Renewed"]):
                member=serializer.validated_data['member']
                book=serializer.validated_data['book']
                total_fine=0
                overdue_count=member.overdue_count
                overdue_cost=member.library.overdue_cost
                total_fine +=overdue_count*overdue_cost
                fine_per_day=member.library.fines_per_day_per_book
                fine_multiplier=member.library.maximum_fine_multiplier
                max_fine=book.book.price*fine_multiplier
                expiry=book.expirydate
                if expiry < timezone.now():
                    expired_time=timezone.now()-expiry
                    expired_days=expired_time.days
                    fine=expired_days*fine_per_day
                    if max_fine <= fine:
                        final=max_fine
                    else:
                        final=fine
                    total_fine += final
                member.borrowed_books-=1
                member.overdue_count=0
                member.remainingfine += total_fine
                member.save()
                book.expirydate=None
                book.book_borrow_by=None
                book.book_status='Idle'
                book.save()
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=drf_status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"error": f"Book not borrowed by the user"}, status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)


class FinePaymentViewset(viewsets.ModelViewSet):
    queryset = FinePayment.objects.all()  
    serializer_class =FinePaymentSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if request.user.has_perm('lms.add_finepayment'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            member=serializer.validated_data['member']
            if serializer.validated_data['amount']<=member.remainingfine:
                member.remainingfine-=serializer.validated_data['amount']
                member.save()
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=drf_status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"error": f"Payment amount more than fine"}, status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)

class BookRenewViewset(viewsets.ModelViewSet):
    queryset = BookRenew.objects.all()  
    serializer_class =BookRenewSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if request.user.has_perm('lms.add_bookrenew'):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['book'] in serializer.validated_data['member'].book_borrow.filter(book_status__in=["Borrowed","Renewed"]):
                member=serializer.validated_data['member']
                book=serializer.validated_data['book']
                total_fine=0
                overdue_count=member.overdue_count
                overdue_cost=member.library.overdue_cost
                total_fine +=overdue_count*overdue_cost
                fine_per_day=member.library.fines_per_day_per_book
                fine_multiplier=member.library.maximum_fine_multiplier
                max_fine=book.book.price*fine_multiplier
                expiry=book.expirydate
                if expiry < timezone.now():
                    expired_time=timezone.now()-expiry
                    expired_days=expired_time.days
                    fine=expired_days*fine_per_day
                    if max_fine <= fine:
                        final=max_fine
                    else:
                        final=fine
                    total_fine += final
                member.borrowed_books-=1
                member.overdue_count=0
                member.remainingfine += total_fine
                member.save()
                book.expirydate=serializer.validated_data['expirydate']
                book.book_borrow_by=member
                book.book_status='Renewed'
                book.save()
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=drf_status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"error": f"Book not borrowed by the user.Only borrowed books can be renewed"}, status=drf_status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "permission not allowed"}, status=drf_status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def advanced_search(request):
    query=request.GET.get('query',None)
    if query:
        from django.db.models import Q
        bookcategory=BookCategory.objects.filter(category_name__icontains=query)
        author=Author.objects.filter(Q(firstname__icontains=query) | Q(middlename__icontains=query) | Q(lastname__icontains=query) | Q(nationality__icontains=query))
        publication=Publication.objects.filter(name__icontains=query)
        library=Library.objects.filter(Q(name__icontains=query) | Q(location__icontains=query))
        books=Books.objects.filter(Q(title__icontains=query) | Q(place_of_publication__icontains=query) | Q(year_of_publication__icontains=query) | Q(edition__icontains=query) | Q(volume__icontains=query) | Q(series__icontains=query) | Q(keywords__icontains=query) | Q(language__icontains=query) | Q(subject__icontains=query) | Q(class_no__icontains=query) | Q(call_no__icontains=query) | Q(isbn__icontains=query) | Q(media_type__icontains=query) | Q(issn__icontains=query))
        uniquebook=UniqueBook.objects.filter(accession_no__icontains=query)
        library_profile=LibraryProfile.objects.filter(Q(first_name__icontains=query) | Q(middle_name__icontains=query) | Q(last_name__icontains=query) | Q(library_card_no__icontains=query))
        return Response({"book":BookCategorySerializer(bookcategory,many=True).data,"author":AuthorSerializer(author,many=True).data,"publication":PublicationSerializer(publication,many=True).data,"library":LibrarySerializer(library,many=True).data,"books":BookSerializer(books,many=True).data,"uniquebook":UniqueBookSerializer(uniquebook,many=True).data,"library_profile":LibraryProfileSeralizer(library_profile,many=True).data})
    else:
        return Response({"message": "Please Enter the Query"})
