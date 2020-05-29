"""tests.py"""
import datetime as dt
from django.test import TestCase
from . import views
from .models import Candlestick


def create_oldest_candlestick():
    """create_oldest_candlestick"""
    return Candlestick.objects.create(
        unixtime=1487042760,
        open=111332,
        high=111332,
        low=111332,
        close=111332,
        volume=0.0058,
    )


def create_latest_candlestick():
    """create_last_candlestick"""
    return Candlestick.objects.create(
        unixtime=1497042760,
        open=111332,
        high=111332,
        low=111332,
        close=111332,
        volume=0.0058,
    )


class CandlestickModelTests(TestCase):
    """CandlestickModelTests"""

    def test_select_oldest_date(self):
        """test_select_oldest_date"""
        latest_date = views.select_latest_date()
        self.assertEqual(latest_date, dt.date(2017, 2, 14))

    def test_select_last_date(self):
        """test_select_last_date"""
        create_oldest_candlestick()
        create_latest_candlestick()
        latest_date = views.select_latest_date()
        self.assertEqual(latest_date, dt.date(2017, 6, 10))

    def test_fetch_candlestick_from_bitbank(self):
        """test_fetch_candlestick_from_bitbank"""
        candlestick_list = views.fetch_candlestick_from_bitbank("20170610")
        self.assertEqual(len(candlestick_list), 1440)

    def test_get_date_range(self):
        """test_get_date_range"""
        start_date = dt.date(2017, 2, 14)
        stop_date = dt.date(2017, 4, 14)
        data = views.get_date_range(start_date, stop_date)
        self.assertEqual(len(list(data)), 59)

    def test_convert_candlestick_to_inserting(self):
        """test_convert_candlestick_to_inserting"""
        candlestick_list = [
            ["312250", "312250", "312250", "312250", "0.0021", 1497052800000]
        ]
        insert_values = views.convert_candlestick_to_inserting(candlestick_list)
        print(type(insert_values))
        self.assertEqual(isinstance(insert_values[0], Candlestick), True)
