"""views.py"""
import datetime as dt
from logging import getLogger, basicConfig, DEBUG
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import pandas as pd  # pylint: disable=import-error
from . import dataset as ds

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


def index(request):
    """index"""
    return render(request, "bitbank/index.html")


def fetch(request):
    """fetch"""
    today = dt.date.today()
    tomorrow = dt.date.today() + dt.timedelta(1)
    date_range = ds.get_date_range(today, tomorrow)
    ds.save_all_candlestick(date_range)
    return HttpResponseRedirect(reverse("bitbank:results", args=("success",)))


def dataset(request, version):
    """dataset"""
    # TODO: Load from DB
    csv = pd.read_csv("bitbank/static/bitbank/datasets/test3.csv")
    _b = ds.BitcoinDataset(version)
    _b.set_dataset(csv)
    _b.plot()
    return redirect("/static/bitbank/graphs/" + version + ".png")


def results(request, results_str):
    """results"""
    return render(request, "bitbank/results.html", {"results": results_str})
