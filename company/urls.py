
from django.urls import path
from . import views

urlpatterns = [
    path("settings/", views.edit_company, name="edit_company"),
]
