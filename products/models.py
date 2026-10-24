from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("LED Bulb", "LED Bulb"),
        ("ice Light", "ice Light"),
        ("DC Light", "DC Light"),
        ("Selling Light", "Selling Light"),
    ]

   
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="LED Bulb"
    )
    watt = models.CharField(max_length=20)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return f"{self.category} - {self.watt}W"