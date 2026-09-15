from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from .models import UserLocation
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point

@login_required
@require_http_methods(["PATCH", "DELETE"])
def location_detail(request, location_id):
    location = get_object_or_404(
        UserLocation,
        id=location_id,
        user=request.user,
        is_active=True
    )
    
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            access_mode = data.get('access_mode')
            radius_meters = int(data.get('radius_meters')) if data.get('radius_meters') else None
            service_ids = data.get('service_category_ids')  # ← NEW (optional)

            # Validate and process service IDs if provided
            if service_ids is not None:
                if not isinstance(service_ids, list):
                    return JsonResponse({'success': False, 'error': 'service_category_ids must be a list'}, status=400)
                if len(service_ids) > 3:
                    return JsonResponse({'success': False, 'error': 'Maximum 3 service categories allowed'}, status=400)
                
                from apps.services.models import ServiceCategory
                from apps.needs.models import UserNeed

                valid_service_ids = list(ServiceCategory.objects.filter(
                    id__in=service_ids, is_active=True
                ).values_list('id', flat=True))
                if len(valid_service_ids) != len(service_ids):
                    return JsonResponse({'success': False, 'error': 'Invalid service category'}, status=400)

                # Replace all needs for this location
                UserNeed.objects.filter(user_location=location).delete()
                needs = [
                    UserNeed(user=request.user, user_location=location, service_category_id=sid)
                    for sid in valid_service_ids
                ]
                UserNeed.objects.bulk_create(needs)

            # Update basic fields
            if access_mode in ['foot', 'car']:
                location.access_mode = access_mode
            if isinstance(radius_meters, int) and radius_meters > 0:
                location.radius_meters = radius_meters
                
            location.save()
            
            # Fetch current service IDs for response
            current_service_ids = list(
                UserNeed.objects.filter(user_location=location)
                .values_list('service_category_id', flat=True)
            )

            return JsonResponse({
                'success': True,
                'id': location.id,
                'lat': location.point.y,
                'lon': location.point.x,
                'access_mode': location.access_mode,
                'radius_meters': location.radius_meters,
                'service_category_ids': current_service_ids,  # ← include
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        location.is_active = False
        location.save()
        return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def save_location(request):
    try:
        data = json.loads(request.body)
        lat = float(data['lat'])
        lon = float(data['lon'])
        access_mode = data.get('access_mode', 'foot')
        radius_input = data.get('radius_meters')
        service_ids = data.get('service_category_ids', [])  # ← NEW

        # Validate service IDs
        if not isinstance(service_ids, list):
            return JsonResponse({'error': 'service_category_ids must be a list'}, status=400)
        if len(service_ids) > 3:
            return JsonResponse({'error': 'Maximum 3 service categories allowed'}, status=400)
        
        # Import here to avoid circular import (or put at top if safe)
        from apps.services.models import ServiceCategory
        from apps.needs.models import UserNeed

        # Verify all service IDs are valid and active
        valid_service_ids = list(ServiceCategory.objects.filter(
            id__in=service_ids, is_active=True
        ).values_list('id', flat=True))
        if len(valid_service_ids) != len(service_ids):
            return JsonResponse({'error': 'One or more invalid/inactive service categories'}, status=400)

        radius_meters = None
        if radius_input is not None:
            radius_meters = int(float(radius_input))

        if access_mode not in ['foot', 'car']:
            return JsonResponse({'error': 'Invalid access mode'}, status=400)

        point = Point(lon, lat, srid=4326)
        location = UserLocation.objects.create(
            user=request.user,
            point=point,
            access_mode=access_mode,
            radius_meters=radius_meters
        )

        # ✅ CREATE UserNeed entries
        needs = [
            UserNeed(user=request.user, user_location=location, service_category_id=sid)
            for sid in valid_service_ids
        ]
        UserNeed.objects.bulk_create(needs)

        return JsonResponse({
            'id': location.id,
            'lat': lat,
            'lon': lon,
            'access_mode': access_mode,
            'radius_meters': radius_meters or (800 if access_mode == 'foot' else 3000),
            'service_category_ids': valid_service_ids,  # ← include in response
        })

    except (ValueError, TypeError, KeyError) as e:
        return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)
    except Exception as e:
        print(f"Save location error: {e}")
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
@login_required
@require_http_methods(["GET"])
def get_locations(request):
    locations = UserLocation.objects.filter(user=request.user, is_active=True)
    location_list = []
    for loc in locations:
        try:
            lon = float(loc.point.x)
            lat = float(loc.point.y)
            
            # ✅ Fetch associated service category IDs
            from apps.needs.models import UserNeed
            service_ids = list(
                UserNeed.objects.filter(user_location=loc)
                .values_list('service_category_id', flat=True)
            )

            location_list.append({
                'id': loc.id,
                'lat': lat,
                'lon': lon,
                'access_mode': loc.access_mode,
                'radius_meters': loc.radius_meters or (800 if loc.access_mode == 'foot' else 3000),
                'service_category_ids': service_ids,  # ← add this
            })
        except (AttributeError, ValueError, TypeError) as e:
            print(f"Skipping invalid location {loc.id}: {e}")
            continue
    return JsonResponse(location_list, safe=False)