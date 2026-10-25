from django.conf import settings
from django.db import models
from products.models import Product


class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_records')

    supplier = models.CharField(max_length=100)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    # Bulb / LED type
    product_type = models.CharField(
        max_length=50,
        default="LED"
    )

    # Watt
    watt = models.PositiveIntegerField(
        default=12
    )

    quantity = models.PositiveIntegerField()

    # ONE PIECE purchase price
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

def __str__(self):
    return f"{self.product.category} - {self.product.watt}W - {self.product_type}"