from django.urls import path
from .views import RoomTypeList, RoomTypeDetail, RoomList, RoomDetail, RoomPictureList, RoomPictureDetail, ExpenseList, ExpenseDetail, BookingList, BookingDetail
app_name='residential'
urlpatterns = [
    path('room-type/', RoomTypeList.as_view(), name = 'api-room-type-list'),
    path('room-type/<int:id>/', RoomTypeDetail.as_view(), name = 'api-room-type-detail'),
    path('room/', RoomList.as_view(), name = 'api-room-list'),
    path('room/<int:id>/', RoomDetail.as_view(), name = 'api-room-detail'),
    path('room-picture/', RoomPictureList.as_view(), name = 'api-room-picture-list'),
    path('room-picture/<int:id>/', RoomPictureDetail.as_view(), name = 'api-room-picture-detail'),
    path('expense/', ExpenseList.as_view(), name = 'api-expense-list'),
    path('expense/<int:id>/', ExpenseDetail.as_view(), name = 'api-expense-detail'),
    path('booking/', BookingList.as_view(), name = 'api-booking-list'),
    path('booking/<int:id>/', BookingDetail.as_view(), name = 'api-booking-detail'),
]