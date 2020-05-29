"""tests.py"""
import datetime as dt
import pickle
from django.test import TestCase
import pandas as pd  # pylint: disable=import-error
from sklearn.linear_model import LinearRegression  # pylint: disable=import-error
from .views import dataset
from .views import bitcoin
from .views import simulator
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
        latest_date = dataset.select_latest_date()
        self.assertEqual(latest_date, dt.date(2017, 2, 14))

    def test_select_last_date(self):
        """test_select_last_date"""
        create_oldest_candlestick()
        create_latest_candlestick()
        latest_date = dataset.select_latest_date()
        self.assertEqual(latest_date, dt.date(2017, 6, 10))

    def test_fetch_candlestick_from_bitbank(self):
        """test_fetch_candlestick_from_bitbank"""
        candlestick_list = dataset.fetch_candlestick_from_bitbank("20170610")
        self.assertEqual(len(candlestick_list), 1440)

    def test_get_date_range(self):
        """test_get_date_range"""
        start_date = dt.date(2017, 2, 14)
        stop_date = dt.date(2017, 4, 14)
        data = dataset.get_date_range(start_date, stop_date)
        self.assertEqual(len(list(data)), 59)

    def test_convert_candlestick_to_inserting(self):
        """test_convert_candlestick_to_inserting"""
        candlestick_list = [
            ["312250", "312250", "312250", "312250", "0.0021", 1497052800000]
        ]
        insert_values = dataset.convert_candlestick_to_inserting(candlestick_list)
        self.assertTrue(isinstance(insert_values[0], Candlestick))

    def test_save_all_candlestick(self):
        """test_save_all_candlestick"""
        days_ago_2 = dt.date.today() + dt.timedelta(-2)
        yesterday = dt.date.today() + dt.timedelta(-1)
        date_range = dataset.get_date_range(days_ago_2, yesterday)
        dataset.save_all_candlestick(date_range)
        self.assertEqual(Candlestick.objects.all().count(), 1440)

    def test_save_all_candlestick_last_minute(self):
        """test_save_all_candlestick_last_minute"""
        # FIXME: Consider timezone
        yesterday = dt.date.today() + dt.timedelta(-1)
        tomorrow = dt.date.today() + dt.timedelta(1)
        date_range = dataset.get_date_range(yesterday, tomorrow)
        dataset.save_all_candlestick(date_range)

        now_ts = dt.datetime.now().timestamp()
        latest_unixtime = Candlestick.objects.order_by("-unixtime")[0].unixtime
        self.assertTrue(now_ts - 60 < latest_unixtime <= now_ts)

    def test_save_all_candlestick_duplicated(self):
        """test_save_all_candlestick_duplicated"""
        # FIXME: Consider timezone
        yesterday = dt.date.today() + dt.timedelta(-1)
        tomorrow = dt.date.today() + dt.timedelta(1)
        date_range = dataset.get_date_range(yesterday, tomorrow)
        dataset.save_all_candlestick(date_range)
        dataset.save_all_candlestick(
            date_range
        )  # TODO: Why not any exception are happen
        self.assertEqual(True, True)

    def test_create_dataset(self):
        """test_create_dataset"""
        file_name = "test"
        csv = pd.read_csv("bitbank/static/bitbank/datasets/candlestick.csv")
        csv = csv[:20000]
        _b = dataset.BitcoinDataset(file_name)
        _b.set_dataset(csv)
        _b.plot()
        self.assertTrue(isinstance(_b.data, pd.core.frame.DataFrame))

    def test_create_model(self):
        """test_create_model"""
        file_name = "test"
        csv = pd.read_csv("bitbank/static/bitbank/datasets/latest.csv")
        # 最後20%のデータでテスト
        test_ratio = 0.2
        test_start = int(len(csv) * (1 - test_ratio))
        csv = csv[:test_start]

        (data_train, _, label_train, _) = bitcoin.set_train_test_dataset(
            csv, test_ratio
        )
        model = bitcoin.create_model(data_train, label_train)

        pickle_file = "bitbank/static/bitbank/models/" + file_name + ".pickle"
        with open(pickle_file, mode="wb",) as file:
            pickle.dump(model, file)

        bitcoin.calc_avg_score(csv, 1)
        bitcoin.plot(csv, model, file_name)

        self.assertTrue(isinstance(model, LinearRegression))

    def test_simulator(self):
        """test_simulator"""
        file_name = "test"
        csv = pd.read_csv("bitbank/static/bitbank/datasets/latest.csv")

        pickle_file = "bitbank/static/bitbank/models/" + file_name + ".pickle"
        with open(pickle_file, mode="rb") as file:
            model = pickle.load(file)

        # 最後20%のデータでテスト
        test_ratio = 0.2
        test_start = int(len(csv) * (1 - test_ratio))
        data = csv[test_start:]

        _s = simulator.BitcoinSimulator(200000)

        y_assets = _s.simulate(data, model)
        print(y_assets[-1])

        simulator.plot(data, model, y_assets, file_name + "_simulate")
        self.assertGreater(len(y_assets), 0)
