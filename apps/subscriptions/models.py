from datetime import timezone
from django.db import models
from apps.users.models import UserProfile

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('demo', 'Demo'),
        ('premium', 'Premium'),
    ]
    
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='demo')
    starts_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # null = lifetime demo

    def is_premium(self):
        if self.plan == 'premium':
            if self.expires_at:
                return timezone.now() < self.expires_at
            return True
        return False