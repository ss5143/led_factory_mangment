from django.conf import settings
from django.db import models


class Company(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_profile",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="company_logo/", blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name