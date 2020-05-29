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


def fetch(request):
    """fetch"""
    today = dt.date.today()
    tomorrow = dt.date.today() + dt.timedelta(1)
    date_range = get_date_range(today, tomorrow)
    save_all_candlestick(date_range)
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
        list: the shape is (1440, 5) like following
            [
                [open, high, low, close, volume, unixtime],
                ...
            ]
    """
    pub = python_bitbankcc.public()
    value = pub.get_candlestick("btc_jpy", "1min", date_str)
    candlestick = value["candlestick"][0]["ohlcv"]
    return candlestick


def get_date_range(start_date: dt.datetime, stop_date: dt.datetime):
    """
    Params:
        start_date (datetime): date of start.
        stop_date (datetime): date of end. it's not included.
    Returns:
        list: list of string of date
    """
    diff = (stop_date - start_date).days
    return (start_date + dt.timedelta(i) for i in range(diff))


def convert_candlestick_to_inserting(candlestick_list: list):
    """
    Params:
        candlestick_list (list): list of date
    Returns:
        list: list of Candlestick
    """
    insert_values = []
    for ohlcv in candlestick_list:
        data = Candlestick(
            unixtime=ohlcv[5] / 1000,
            open=ohlcv[0],
            high=ohlcv[1],
            low=ohlcv[2],
            close=ohlcv[3],
            volume=ohlcv[4],
        )
        insert_values.append(data)

    return insert_values


def save_all_candlestick(date_range):
    """
    Insert all candlesticks into DB
    """

    for date in date_range:
        logger.info("date: {:%Y-%m-%d}".format(date))
        date_str = date.strftime("%Y%m%d")
        candlestick_list = fetch_candlestick_from_bitbank(date_str)
        insert_values = convert_candlestick_to_inserting(candlestick_list)
        Candlestick.objects.bulk_create(insert_values, ignore_conflicts=True)
