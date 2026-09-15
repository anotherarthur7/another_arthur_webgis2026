from django.urls import path
from django.urls import include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.user_map, name='user_map'),
    path('register/', views.register, name='register'),
    path('register/done/', views.registration_done, name='registration_done'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='main/logged_out.html'), name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('map-yandex/', views.user_map_yandex, name='user_map_yandex'),
]