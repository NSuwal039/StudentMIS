from django.urls import path
from .views import RoomTypeAddView, RoomTypeDetailView, RoomTypeEditView, RoomTypeDeleteView, RoomTypeListView, RoomListView, RoomAddView, RoomDetailView, RoomEditView, RoomDeleteView, RoomPictureDeleteView, ExpenseListView, ExpenseDetailView, ExpenseAddView, ExpenseEditView, ExpenseDeleteView, BookingListView, BookingDetailView, BookingAddView, BookingEditView, BookingDeleteView, CustomerAddReview, ReviewListView, ReviewDetailView, ReviewDeleteView

app_name='residential'
urlpatterns = [
    # Room Type urls
    path('roomtypes/', RoomTypeListView.as_view(), name = 'room-types'),
    path('roomtype/<int:id>/', RoomTypeDetailView.as_view(), name = 'room-type-detail'),
    path('roomtype/add/', RoomTypeAddView.as_view(), name = 'room-type-add'),
    path('roomtype/edit/<int:id>/', RoomTypeEditView.as_view(), name = 'room-type-edit'),
    path('roomtype/delete/<int:id>/', RoomTypeDeleteView.as_view(), name = 'room-type-delete'),

    # Room urls
    path('rooms/', RoomListView.as_view(), name = 'room-list'),
    path('room/add/', RoomAddView.as_view(), name = 'room-add'),
    path('room/<int:id>/', RoomDetailView.as_view(), name = 'room-detail'),
    path('room/edit/<int:id>/', RoomEditView.as_view(), name = 'room-edit'),
    path('room/delete/<int:id>/', RoomDeleteView.as_view(), name = 'room-delete'),

    # Room Picture urls
    path('roompicture/delete/<int:id>/<int:room_id>/', RoomPictureDeleteView.as_view(), name = 'room-picture-delete'),

    # Expense urls
    path('expenses/', ExpenseListView.as_view(), name = 'expense-list'),
    path('expense/add/', ExpenseAddView.as_view(), name = 'expense-add'),
    path('expense/<int:id>/', ExpenseDetailView.as_view(), name = 'expense-detail'),
    path('expense/edit/<int:id>/', ExpenseEditView.as_view(), name = 'expense-edit'),
    path('expense/delete/<int:id>/', ExpenseDeleteView.as_view(), name = 'expense-delete'),

    # Booking urls
    path('bookings/', BookingListView.as_view(), name = 'booking-list'),
    path('booking/add/', BookingAddView.as_view(), name = 'booking-add'),
    path('booking/<int:id>/', BookingDetailView.as_view(), name = 'booking-detail'),
    path('booking/edit/<int:id>/', BookingEditView.as_view(), name = 'booking-edit'),
    path('booking/delete/<int:id>/', BookingDeleteView.as_view(), name = 'booking-delete'),

    # Review urls
    path('customer/review/', CustomerAddReview.as_view(), name = 'customer-add-review'),
    path('reviews/', ReviewListView.as_view(), name = 'review-list'),
    path('review/<int:id>/', ReviewDetailView.as_view(), name = 'review-detail'),
    path('review/delete/<int:id>/', ReviewDeleteView.as_view(), name = 'review-delete'),
]