"""urls.py"""
from django.urls import path

from . import views

app_name = "bitbank"  # pylint: disable=invalid-name
urlpatterns = [
    path("", views.index, name="index"),
    path("fetch/", views.fetch, name="fetch"),
    path("dataset/<str:version>", views.dataset, name="dataset"),
    path("results/<str:results_str>", views.results, name="results"),
]
