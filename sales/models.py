
from django.db import models
from products.models import Product


class Sale(models.Model):
    customer_name = models.CharField(max_length=200)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.product} - {self.quantity}"

