from django import forms
from .models import Purchase
from products.models import Product


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["product"].queryset = Product.objects.filter(
                user=user
            )
