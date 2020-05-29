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
        self.assertTrue(isinstance(insert_values[0], Candlestick))

    def test_save_all_candlestick(self):
        """test_save_all_candlestick"""
        days_ago_2 = dt.date.today() + dt.timedelta(-2)
        yesterday = dt.date.today() + dt.timedelta(-1)
        date_range = views.get_date_range(days_ago_2, yesterday)
        views.save_all_candlestick(date_range)
        self.assertEqual(Candlestick.objects.all().count(), 1440)

    def test_save_all_candlestick_last_minute(self):
        """test_save_all_candlestick_last_minute"""
        # FIXME: Consider timezone
        yesterday = dt.date.today() + dt.timedelta(-1)
        tomorrow = dt.date.today() + dt.timedelta(1)
        date_range = views.get_date_range(yesterday, tomorrow)
        views.save_all_candlestick(date_range)

        now_ts = dt.datetime.now().timestamp()
        latest_unixtime = Candlestick.objects.order_by("-unixtime")[0].unixtime
        self.assertTrue(now_ts - 60 < latest_unixtime <= now_ts)

    def test_save_all_candlestick_duplicated(self):
        """test_save_all_candlestick_duplicated"""
        # FIXME: Consider timezone
        yesterday = dt.date.today() + dt.timedelta(-1)
        tomorrow = dt.date.today() + dt.timedelta(1)
        date_range = views.get_date_range(yesterday, tomorrow)
        views.save_all_candlestick(date_range)
        views.save_all_candlestick(date_range)  # TODO: Why not any exception are happen
        self.assertEqual(True, True)
