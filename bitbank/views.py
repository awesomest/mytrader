"""views.py"""
import datetime as dt
from logging import getLogger, basicConfig, DEBUG
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import python_bitbankcc  # pylint: disable=import-error
from bitbank.models import Candlestick

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)

# from .modules import candlestick


def index(request):
    """index"""
    return render(request, "bitbank/index.html")


def fetch():
    """fetch"""
    return HttpResponseRedirect(reverse("bitbank:results", args=("success",)))


def results(request, results_str):
    """results"""
    return render(request, "bitbank/results.html", {"results": results_str})


def select_latest_date():
    """select_latest_date"""
    try:
        latest_unixtime = Candlestick.objects.order_by("-unixtime")[0].unixtime
    except (Candlestick.DoesNotExist, IndexError):
        oldest_date = dt.date(2017, 2, 14)  # TODO: 適当に決めた日付なので要改善
        return oldest_date
    else:
        latest_datetime = dt.datetime.fromtimestamp(latest_unixtime)
        latest_date = dt.date(
            latest_datetime.year, latest_datetime.month, latest_datetime.day
        )
        return latest_date


def fetch_candlestick_from_bitbank(date_str: str):
    """
    Params:
        date_str (str): string of date
    Returns:
        list: all of list of candlestick
    """
    pub = python_bitbankcc.public()
    value = pub.get_candlestick("btc_jpy", "1min", date_str)
    candlestick = value["candlestick"][0]["ohlcv"]
    return candlestick
