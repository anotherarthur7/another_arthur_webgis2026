from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('consumer', 'Consumer'),
        ('business', 'Business Representative'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    city = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='consumer'
    )

    def __str__(self):
        return f"Profile of {self.user.username} ({self.user_type})"

    def is_business_user(self):
        return self.user_type in ['business', 'admin']