from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models

class ExternalBusiness(models.Model):
    name = models.CharField(max_length=200)
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.CASCADE)
    location = gis_models.PointField(geography=True, srid=4326)
    city = models.ForeignKey('geo.City', on_delete=models.CASCADE)
    source = models.CharField(max_length=50)  # e.g., 'osm', '2gis'
    external_id = models.CharField(max_length=100)
    detected_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[External] {self.name} ({self.service_category.name})"

class PartnerBusiness(models.Model):
    name = models.CharField(max_length=200)
    owner_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.PROTECT)
    location = gis_models.PointField(geography=True, srid=4326)
    city = models.ForeignKey('geo.City', on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[Partner] {self.name} ({self.service_category.name})"

class OsmTagMapping(models.Model):
    osm_key = models.CharField(max_length=50)
    osm_value = models.CharField(max_length=50)
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('osm_key', 'osm_value')
        verbose_name = "OSM Tag Mapping"

    def __str__(self):
        return f"{self.osm_key}={self.osm_value} → {self.service_category.slug}"