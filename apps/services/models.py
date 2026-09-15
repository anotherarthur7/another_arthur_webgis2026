from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True) # for the case we stop providing this service

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service categories"