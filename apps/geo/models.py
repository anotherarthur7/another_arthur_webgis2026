from django.contrib.gis.db import models as gis_models
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    center_point = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    polygon_boundary = gis_models.PolygonField(geography=True, srid=4326, null=True, blank=True)
    projection_code = models.CharField(
        max_length=20,
        default='EPSG:3857',  # Web Mercator fallback
        help_text="Projection used for map display (e.g., 'EPSG:28416')"
    )
    projection_definition = models.TextField(
        blank=True,
        help_text="proj4 definition for custom projections (e.g., EPSG:28416)"
    )

    def __str__(self):
        return f"{self.name}, {self.country.name}"
    
    class Meta:
        verbose_name_plural = "Cities"