from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError

class UserLocation(models.Model):
    ACCESS_MODE_CHOICES = [
        ('foot', 'Foot'),
        ('car', 'Car'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    point = gis_models.PointField(geography=True, srid=4326)
    access_mode = models.CharField(max_length=10, choices=ACCESS_MODE_CHOICES)
    radius_meters = models.PositiveIntegerField(null=True, blank=True)  # user override
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.pk:  # Only on creation
            existing_count = UserLocation.objects.filter(user=self.user, is_active=True).count()
            if existing_count >= 3:
                raise ValidationError("User cannot have more than 3 active locations.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} – {self.access_mode} @ {self.point}"