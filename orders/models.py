
from django.db import models
from customers.models import Customer


class Order(models.Model):

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    customer_name = models.CharField(
        max_length=100,
        default="Walk-in Customer"
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    @property
    def total_quantity(self):
        """
        Order ke tamam items ki total quantity.
        Example:
        50 + 50 + 45 = 145
        """
        return sum(
            item.quantity
            for item in self.items.all()
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def save(self, *args, **kwargs):

        self.total_price = (
            self.unit_price * self.quantity
        )

        self.profit = (
            (self.unit_price - self.purchase_price)
            * self.quantity
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.product.category} - {self.product.watt}W × {self.quantity}"
        )
