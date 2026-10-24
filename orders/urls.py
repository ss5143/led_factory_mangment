from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path(
        "orders/",
        views.orders,
        name="orders"
    ),

    path(
        "add-order/",
        views.add_order,
        name="add_order"
    ),

    path(
        "orders/<int:id>/",
        views.order_detail,
        name="order_detail"
    ),

    path(
        "orders/<int:id>/edit/",
        views.edit_order,
        name="edit_order"
    ),
    path(
        "orders/<int:id>/delete/",
         views.delete_order,
         name="delete_order"
    ),

    path(
        "orders/<int:id>/paid/",
        views.mark_paid,
        name="mark_paid"
    ),

    path(
        "orders/<int:id>/invoice/",
        views.invoice,
        name="invoice"
    ),

    path(
        "orders/<int:order_id>/invoice-pdf/",
        views.invoice_pdf,
        name="invoice_pdf"
    ),
]