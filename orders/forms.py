
from django import forms


class OrderForm(forms.Form):

    customer_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Customer Name"
            }
        )
    )
