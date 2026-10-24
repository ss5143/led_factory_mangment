from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<int:id>/", views.edit_product, name="edit_product"),
    path("delete-product/<int:id>/", views.delete_product, name="delete_product"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path(
    "export/products/",
    views.export_products_excel,
    name="export_products_excel",
    ),
]