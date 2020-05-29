"""urls.py"""
from django.urls import path

from .views import views

app_name = "bitbank"  # pylint: disable=invalid-name
urlpatterns = [
    path("", views.index, name="index"),
    path("fetch/", views.fetch, name="fetch"),
    path("dataset/<str:version>", views.dataset, name="dataset"),
    path("train/<str:version>", views.train, name="train"),
    path("simulate/<str:version>", views.simulate, name="simulate"),
    path("results/<str:results_str>", views.results, name="results"),
]
