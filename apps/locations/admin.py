from django.contrib import admin
from apps.locations.models import UserLocation

# Register your models here.
@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'point']