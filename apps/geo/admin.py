from django.contrib import admin
from .models import Country, City

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'iso_code']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'projection_code']
    search_fields = ['name']