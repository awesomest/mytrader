"""views.py"""
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
    """index"""
    return render(request, "bitbank/index.html")


def fetch(_):
    """fetch"""
    return HttpResponseRedirect(reverse("bitbank:results", args=("success",)))


def results(request, results_str):
    """results"""
    return render(request, "bitbank/results.html", {"results": results_str})
