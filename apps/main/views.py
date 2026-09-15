from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import UserRegistrationForm
from apps.users.models import UserProfile
from apps.services.models import ServiceCategory

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_url = request.build_absolute_uri(f'/activate/{uid}/{token}/')
            
            subject = 'Activate your CIM account'
            message = render_to_string('main/email_activation.txt', {
                'user': user,
                'activation_url': activation_url,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            return redirect('main:registration_done')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})

def registration_done(request):
    return render(request, 'main/registration_done.html')

def home(request):
    return render(request, 'main/home.html')

@login_required
def user_map(request):
    profile = request.user.userprofile
    if not profile.city:
        raise Exception("User must have a city assigned")
    
    city = profile.city
    context = {
        'city_name': city.name,
        'city_center_lat': city.center_point.y,
        'city_center_lon': city.center_point.x,
        'city_projection_code': city.projection_code or 'EPSG:3857',
        'city_projection_def': city.projection_definition or '',
    }
    context.update({
        'service_categories': ServiceCategory.objects.filter(is_active=True)
    })
    return render(request, 'main/user_map.html', context)

@login_required
def user_map_yandex(request):
    profile = request.user.userprofile
    if not profile.city:
        raise Exception("User must have a city assigned")
    
    city = profile.city
    # Provide fallbacks in case center_point is NULL
    lat = float(city.center_point.y)
    lon = float(city.center_point.x)

    context = {
        'city_name': city.name,
        'city_center_lat': lat,
        'city_center_lon': lon,
    }
    context.update({
        'service_categories': ServiceCategory.objects.filter(is_active=True)
    })
    return render(request, 'main/user_map_yandex.html', context)

def login(request):
    return render(request, 'main/login.html')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        messages.success(request, 'Your account has been activated!')
        return redirect('main:home')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('main:register')
    
def logout(request):
    return render(request, 'main/logged_out.html')