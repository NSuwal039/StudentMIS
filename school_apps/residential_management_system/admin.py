from django.contrib import admin
from .models import RoomType, Room, RoomPicture, Booking

admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(RoomPicture)
admin.site.register(Booking)
