from django.contrib import admin
from .models import Bus,Bus_schedule,Route

from login.views import register

# Register your models here.
admin.site.register(Bus)
admin.site.register(Bus_schedule)
admin.site.register(Route)