from django.contrib import admin
from .models import Department, Ticket, Form

class DepartmentAdmin(admin.ModelAdmin):
    pass

class FormAdmin(admin.ModelAdmin):
    pass    

class TicketAdmin(admin.ModelAdmin):
    pass    

admin.site.register(Form, FormAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Ticket, TicketAdmin)    
