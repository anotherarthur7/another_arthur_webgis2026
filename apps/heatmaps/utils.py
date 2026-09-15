# apps/heatmaps/utils.py
import json
from django.db import connection
from django.core.cache import cache

def get_cell_size_by_zoom(zoom):
    if zoom <= 10: return 200
    elif zoom <= 13: return 100
    else: return 50

def generate_heatmap_grid(city_id, service_id=None, zoom=11, user=None):
    cell_size = get_cell_size_by_zoom(zoom)
    cache_key = f"heatmap_{city_id}_{service_id or 'all'}_{cell_size}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    service_filter = ""
    # ⚠️ 3 params: geo_city.id, cell_size, userprofile.city_id
    params = [city_id, cell_size, city_id]
    if service_id and service_id != "":
        service_filter = "AND un.service_category_id = %s"
        params.append(service_id)

    with connection.cursor() as cursor:
        cursor.execute("""
        WITH city_geom AS (
            SELECT ST_Transform(
                CASE 
                    WHEN polygon_boundary IS NOT NULL THEN polygon_boundary
                    ELSE ST_Buffer(center_point::geography, 20000)
                END::geometry, 3857
            ) AS geom
            FROM geo_city WHERE id = %s
        ),
        grid AS (
            SELECT (ST_SquareGrid(%s, geom)).geom AS cell_3857
            FROM city_geom
        ),
        cell_centers AS (
            SELECT 
                ST_Transform(ST_Centroid(cell_3857), 4326) AS center,
                ST_Transform(cell_3857, 4326) AS cell
            FROM grid
        ),
        active_needs AS (
            SELECT point, radius_meters
            FROM needs_userneed un
            JOIN locations_userlocation ul ON un.user_location_id = ul.id
            JOIN users_userprofile up ON ul.user_id = up.user_id
            WHERE ul.is_active = true
              AND un.status = 'active'
              AND up.city_id = %s
              {service_filter}
        ),
        demand AS (
            SELECT 
                c.cell,
                COUNT(*) AS intensity
            FROM cell_centers c
            JOIN active_needs an 
              ON ST_DWithin(c.center::geography, an.point::geography, an.radius_meters)
            GROUP BY c.cell
            HAVING COUNT(*) >= 5  -- ✅ Only true overlaps
            ORDER BY intensity DESC
            LIMIT 2000
        )
        SELECT ST_AsGeoJSON(ST_ForcePolygonCCW(cell)), intensity
        FROM demand;
        """.format(service_filter=service_filter), params)

        rows = cursor.fetchall()
        features = []
        for geom_json_str, intensity in rows:
            if geom_json_str:
                try:
                    geom_obj = json.loads(geom_json_str)
                    if geom_obj and 'type' in geom_obj:
                        features.append({
                            'type': 'Feature',
                            'geometry': geom_obj,
                            'properties': {'intensity': intensity}
                        })
                except (ValueError, TypeError):
                    continue

        cache.set(cache_key, features, 3600)
        return features