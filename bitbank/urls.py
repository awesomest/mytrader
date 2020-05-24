"""urls.py"""
from django.urls import path

from . import views

app_name = "bitbank"  # pylint: disable=invalid-name
urlpatterns = [
    path("", views.index, name="index"),
]
