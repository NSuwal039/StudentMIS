from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import RoomTypeSerializer, RoomSerializer, RoomPictureSerializer, BookingSerializer, ExpenseSerializer
from .models import RoomType, Room, RoomPicture, Booking, Expense, Review
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.db.models import Q
import time
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import RoomTypeForm, RoomForm, ExpenseForm, BookingForm, ReviewForm
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect
import json

# Default no of items to be displayed in a listview
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

class RoomTypeList(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):    
        try:    
            room_type = RoomType.objects.all()
        except:
            raise Http404

        serializer = RoomTypeSerializer(room_type, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomTypeSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)    

class RoomTypeDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            room_type = RoomType.objects.get(id = id)
            return room_type
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, id):
        room_type = self.get_object(id)
        serializer = RoomTypeSerializer(room_type)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        serializer = RoomTypeSerializer(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        room_type = self.get_object(id)
        room_type.delete()
        return Response(status = status.HTTP_201_CREATED)  

class RoomList(APIView):
    def get(self, request):  
        try:    
            room = Room.objects.all()
        except:
            raise Http404

        serializer = RoomSerializer(room, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)   

class RoomDetail(APIView):
    def get_object(self, id):
        try:
            room = Room.objects.get(id = id)
            return room
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, id):
        room = self.get_object(id)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        serializer = RoomSerializer(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        room = self.get_object(id)
        room.delete()
        return Response(status = status.HTTP_201_CREATED)   

class RoomPictureList(APIView):
    def get(self, request):
        page = request.query_params.get('page')
        if not page:
            page = 1

        query = Q()    

        room = request.query_params.get('room')     
        if room:
            query &= Q(room = room)    
        try:    
            room_pictures = RoomPicture.objects.filter(query)
        except:
            raise Http404

        paginator = Paginator(room_pictures, page_count)
        page_obj = paginator.get_page(page)

        serializer = RoomPictureSerializer(page_obj, many = True)
        data = page_serializer(paginator, page_obj, page, serializer.data)
        return Response(data)    

    def post(self, request):
        serializer = RoomPictureSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST) 

class RoomPictureDetail(APIView):
    def get_object(self, id):
        try:
            room_picture = RoomPicture.objects.get(id = id)
            return room_picture
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, id):
        room_picture = self.get_object(id)
        serializer = RoomPictureSerializer(room_picture)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        serializer = RoomPictureSerializer(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        room_picture = self.get_object(id)
        room_picture.delete()
        return Response(status = status.HTTP_201_CREATED) 

class ExpenseList(APIView):
    def get(self, request):
        page = request.query_params.get('page')
        if not page:
            page = 1    
        try:    
            expense = Expense.objects.all()
        except:
            raise Http404

        paginator = Paginator(expense, page_count)
        page_obj = paginator.get_page(page)

        serializer = ExpenseSerializer(page_obj, many = True)
        data = page_serializer(paginator, page_obj, page, serializer.data)
        return Response(data)

    def post(self, request):
        serializer = ExpenseSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST) 

class ExpenseDetail(APIView):
    def get_object(self, id):
        try:
            expense = Expense.objects.get(id = id)
            return expense
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, id):
        expense = self.get_object(id)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        serializer = ExpenseSerializer(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        expense = self.get_object(id)
        expense.delete()
        return Response(status = status.HTTP_201_CREATED) 

class BookingList(APIView):
    def get(self, request):
        page = request.query_params.get('page')
        if not page:
            page = 1

        query = Q()    

        name = request.query_params.get('name')     
        if name:
            query &= Q(name__icontains = name)    

        try:    
            booking = Booking.objects.all().filter(query)
        except:
            raise Http404


        paginator = Paginator(booking, page_count)
        page_obj = paginator.get_page(page)

        serializer = BookingSerializer(page_obj, many = True)
        data = page_serializer(paginator, page_obj, page, serializer.data)
        return Response(data)

    def post(self, request):
        serializer = BookingSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()

            _id = serializer.data['id']
            try:
                booking = Booking.objects.get(id = _id)

            except ObjectDoesNotExist:
                pass
            else:    
                subject = 'Subject'
                html_message = render_to_string('email/booking_mail.html', {'booking' : booking})
                plain_message = strip_tags(html_message)
                to_email = booking.booked_by.email
                send_mail(subject, plain_message, settings.EMAIL_HOST_USER,[to_email], html_message = html_message)

            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST) 

class BookingDetail(APIView):
    def get_object(self, id):
        try:
            booking = Booking.objects.get(id = id)
            return booking
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, id):
        booking = self.get_object(id)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def put(self, request, id):
        serializer = BookingSerializer(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, id):
        booking = self.get_object(id)
        booking.delete()
        return Response(status = status.HTTP_201_CREATED) 


'''
Views defined below are all for adminlte and not api
'''        

class RoomTypeListView(View):
    def get(self, request):
        roomtypes = RoomType.objects.all()
        context = {'roomtypes' : roomtypes}
        return render(request, 'residential/roomtype-list.html', context)

class RoomTypeDetailView(View):
    def get(self, request, id):
        try:
            roomtype = RoomType.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            context = {'roomtype' : roomtype}
            return render(request, 'residential/roomtype-detail.html', context)        
            
class RoomTypeAddView(View):
    def get(self, request):
        form = RoomTypeForm()
        context = {'form' : form}
        return render(request, 'residential/roomtype-add.html', context)

    def post(self, request):    
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room Type successfully added')
            return redirect('/residential/roomtypes/')
        else:
            messages.error(request, 'Something went wrong.')    

class RoomTypeEditView(View):
    def get(self, request, id):
        try:
            roomtype = RoomType.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            form = RoomTypeForm(instance = roomtype)
            context = {'form' : form, 'roomtype' : roomtype}
            return render(request, 'residential/roomtype-edit.html', context)

    def post(self, request, id):
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room Type successfully changed')
            return redirect('/residential/roomtypes/')
        else:
            messages.error(request, 'Something went wrong')    

class RoomTypeDeleteView(View):
    def get(self, request, id):
        try:
            roomtype = RoomType.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            roomtype.delete()  
            messages.success(request, 'Room type successfully deleted')
            return redirect('/residential/roomtypes/')


class RoomListView(View):
    def get(self, request):
        room = Room.objects.all()
        context = {'room' : room}
        return render(request, 'residential/room-list.html', context) 

class RoomDetailView(View):
    def get(self, request, id):
        try:
            room = Room.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            room_pictures = RoomPicture.objects.filter(room = room)
            context = {'room' : room, 'room_pictures' : room_pictures}
            return render(request, 'residential/room-detail.html', context)        

class RoomAddView(View):
    def get(self, request):
        room_form = RoomForm()
        context = {'room_form' : room_form}
        return render(request, 'residential/room-add.html', context)

    def post(self, request):
        room_form = RoomForm(request.POST)
        if room_form.is_valid():
            room = room_form.save()
            pictures = request.FILES.getlist('files')

            bulk_list = [RoomPicture(room = room, photo = pic) for pic in pictures]
            RoomPicture.objects.bulk_create(bulk_list)        
            return redirect('/residential/rooms/')

        else:
            return redirect('/residential/rooms/')        

       

class RoomEditView(View):
    def get(self, request, id):
        try:
            room = Room.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:        
            room_form = RoomForm(instance = room)
            room_pictures = RoomPicture.objects.filter(room = room)
            context = {'room_form' : room_form, 'room' : room, 'room_pictures' : room_pictures}
            return render(request, 'residential/room-edit.html', context)

    def post(self, request, id):
        try:
            room = Room.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            room_form = RoomForm(request.POST, request.FILES, instance = room)
            if room_form.is_valid():     
                room_form.save() 
                pictures = request.FILES.getlist('files')

                bulk_list = [RoomPicture(room = room, photo = pic) for pic in pictures]
                RoomPicture.objects.bulk_create(bulk_list)        
                return redirect('/residential/rooms/')

            else:
                return redirect('/residential/rooms/') 

class RoomDeleteView(View):
    def get(self, request, id):
        try:
            room = Room.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            room.delete()        
            return redirect('/residential/rooms/')

class RoomPictureDeleteView(View):
    def get(self, request, id, room_id):
        try:
            room_picture = RoomPicture.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            room_picture.delete()
            redirect_url = '/residential/room/edit/' + str(room_id) + '/#nav-pictures'
            return redirect(redirect_url)

class ExpenseListView(View):
    def get(self, request):
        expenses = Expense.objects.all()
        context = {'expenses' : expenses}
        return render(request, 'residential/expense-list.html', context)

class ExpenseDetailView(View):
    def get(self, request, id):
        try:
            expense = Expense.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            context = {'expense' : expense}
            return render(request, 'residential/expense-detail.html', context)

class ExpenseAddView(View):
    def get(self, request):
        form = ExpenseForm()
        context = {'form' : form}
        return render(request, 'residential/expense-add.html', context)

    def post(self, request):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/residential/expenses/')
        else:
            return redirect('/residential/expense/add/')
            messages.error(request, 'Something went wrong')        

class ExpenseEditView(View):
    def get(self, request, id):
        try:
            expense = Expense.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            form = ExpenseForm(instance = expense)
            context = {'form' : form, 'expense' : expense}
            return render(request, 'residential/expense-edit.html', context)

    def post(self, request, id):
        try:
            expense = Expense.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            form = ExpenseForm(request.POST, instance = expense)
            if form.is_valid():
                form.save()
                return redirect('/residential/expenses/')
            else:
                messages.error(request, 'Something went wrong')
                return redirect('/residential/expenses/')    

class ExpenseDeleteView(View):
    def get(self, request, id):
        try:
            expense = Expense.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            expense.delete()
            messages.success(request, 'Successfully deleted')
            return redirect('/residential/expenses/')

class BookingListView(View):
    def get(self, request):
        bookings = Booking.objects.all()
        context = {'bookings' : bookings}
        return render(request, 'residential/booking-list.html', context)

class BookingDetailView(View):
    def get(self, request, id):
        try:
            booking = Booking.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            context = {'booking' : booking}
            return render(request, 'residential/booking-detail.html', context)

class BookingAddView(View):
    def get(self, request):
        form = BookingForm()
        context = {'form' : form}
        return render(request, 'residential/booking-add.html', context)

    def post(self, request):
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            subject = 'Subject'
            html_message = render_to_string('email/booking_mail.html', {'booking' : booking})
            plain_message = strip_tags(html_message)
            to_email = booking.booked_by.email
            send_mail(subject, plain_message, settings.EMAIL_HOST_USER,[to_email], html_message = html_message)
            return redirect('/residential/bookings/')

class BookingEditView(View):
    def get(self, request, id):
        try:
            booking = Booking.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            form = BookingForm(instance = booking)
            context = {'form' : form, 'booking' : booking}
            return render(request, 'residential/booking-edit.html', context)

    def post(self, request, id):
        try:
            booking = Booking.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            form = BookingForm(request.POST, instance = booking)
            if form.is_valid():
                form.save()
                return redirect('/residential/bookings/')
            else:
                messages.error(request, 'Something went wrong')    
                return redirect('/residential/bookings/')

class BookingDeleteView(View):
    def get(self, request, id):
        try:
            booking = Booking.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            booking.delete()
            messages.success(request, 'Booking deleted successfully')
            return redirect('/residential/bookings/')

class ReviewListView(View):
    def get(self, request):
        review = Review.objects.all()
        context = {'review' : review}
        return render(request, 'residential/review-list.html', context)

class ReviewDetalView(View):
    def get(self, request, id):
        try:
            review = Review.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            context = {'review' : review}
            return render(request, 'residential/review-detail.html', context) 

class CustomerAddReview(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/residential/customer/review/')
        return render(request, 'residential/customer-review.html')

    def post(self, request):
        if request.user.is_authenticated:
            _user = request.user
            if request.is_ajax:
                _review = request.POST['review']
                _rating = float(request.POST['rating'])
                try:
                    _booking = Booking.objects.filter(booked_by = _user).latest('booked_on')
                except ObjectDoesNotExist:
                    return JsonResponse({'status' : 'notok'})
                else:        
                    if _review and _rating and _booking:
                        review = Review.objects.create(
                            user = _user,
                            review = _review,
                            rating = _rating,
                            booking = _booking
                        )           
                    return JsonResponse({'status' : 'ok'})   

        else:
            return JsonResponse({'status' : 'notok'})   

class ReviewListView(View):
    def get(self, request):
        review = Review.objects.all()
        context = {'review' : review}
        return render(request, 'residential/review-list.html', context)

class ReviewDetailView(View):
    def get(self, request, id):
        try:
            review = Review.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            context = {'review' : review}
            return render(request, 'residential/review-detail.html', context)

class ReviewDeleteView(View):
    def get(self, request, id): 
        try:
            review = Review.objects.get(id = id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            review.delete()
            messages.success(request, 'Review successfully deleted')             
            return redirect('/residential/reviews/')     



                            




    




            

