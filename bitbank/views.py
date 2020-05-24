"""views.py"""
from django.shortcuts import render


def index(request):
    """index"""
    return render(request, "bitbank/index.html")
