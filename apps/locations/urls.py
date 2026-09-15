from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('api/locations/', views.get_locations, name='get_locations'),  # GET
    path('api/locations/create/', views.save_location, name='save_location'),  # POST (rename to avoid conflict)
    path('api/locations/<int:location_id>/', views.location_detail, name='location_detail'),
]