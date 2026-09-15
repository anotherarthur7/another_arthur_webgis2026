from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserNeed(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('satisfied', 'Satisfied'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_location = models.ForeignKey('locations.UserLocation', on_delete=models.CASCADE)
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by_partner = models.ForeignKey(
        'businesses.PartnerBusiness',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def clean(self):
        if self.user_location.user != self.user:
            raise ValidationError("UserLocation must belong to the same user.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} needs {self.service_category.name}"