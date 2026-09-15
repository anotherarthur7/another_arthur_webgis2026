# apps/heatmaps/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from apps.users.models import UserProfile
from apps.geo.models import City
from apps.services.models import ServiceCategory
from apps.heatmaps.utils import generate_heatmap_grid
from django.views.decorators.http import require_GET
from apps.subscriptions.models import Subscription

@login_required
def heatmap_view(request):
    profile = request.user.userprofile
    if not profile.is_business_user():
        return redirect('main:home')
    
    subscription, _ = Subscription.objects.get_or_create(
        user_profile=profile,
        defaults={'plan': 'demo'}
    )
    
    context = {
        'city_name': profile.city.name if profile.city else 'Your City',
        'service_categories': ServiceCategory.objects.filter(is_active=True),
        'city_center_lon': profile.city.center_point.x if profile.city and profile.city.center_point else 92.8558,
        'city_center_lat': profile.city.center_point.y if profile.city and profile.city.center_point else 56.0184,
        'is_premium': subscription.is_premium(),
    }
    return render(request, 'heatmaps/heatmap.html', context)

@login_required
@require_GET
def get_heatmap_data(request):
    try:
        profile = request.user.userprofile
        if not profile.is_business_user():
            return JsonResponse({'error': 'Access denied'}, status=403)
        if not profile.city or not profile.city.center_point:
            return JsonResponse({'error': 'City not configured'}, status=400)

        service_id = request.GET.get('service_id')
        zoom_param = request.GET.get('zoom', '11')
        zoom_raw = int(float(zoom_param))
        if zoom_raw <= 10:
            zoom = 10
        elif zoom_raw <= 13:
            zoom = 12
        else:
            zoom = 14

        # Premium users can go to 100m; demo capped at 500m
        subscription, _ = Subscription.objects.get_or_create(
            user_profile=profile,
            defaults={'plan': 'demo'}
        )
        if not subscription.is_premium() and zoom > 13:
            zoom = 13  # Cap demo at 500m

        grid_geojson = generate_heatmap_grid(
            city_id=profile.city.id,
            service_id=service_id,
            zoom=zoom,
            user=request.user
        )

        # Generate boundary (20km buffer)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ST_AsGeoJSON(
                    ST_Buffer(center_point::geography, 20000)::geometry
                )
                FROM geo_city
                WHERE id = %s
            """, [profile.city.id])
            boundary_geojson = cursor.fetchone()[0] if cursor.rowcount else None

        return JsonResponse({
            'type': 'FeatureCollection',
            'features': grid_geojson or [],
            'boundary': boundary_geojson
        })

    except Exception as e:
        import traceback
        print("🔥 HEATMAP ERROR:", traceback.format_exc())
        return JsonResponse({'error': 'Failed to generate heatmap'}, status=500)