from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="company_logo/")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
