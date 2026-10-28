from django.contrib import admin
from .models import Owner, Tenant, Location, Hostel, Room

admin.site.register(Owner)
admin.site.register(Tenant)
admin.site.register(Location)
admin.site.register(Hostel)
admin.site.register(Room)

# Register your models here.
