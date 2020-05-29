"""views.py"""
import inspect
import datetime as dt
from logging import getLogger, basicConfig, DEBUG
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from bitbank.models import Candlestick
from scipy import signal  # pylint: disable=import-error
import python_bitbankcc  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error
import numpy as np  # pylint: disable=import-error
import matplotlib  # pylint: disable=import-error

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # pylint: disable=import-error,wrong-import-position

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


TRAIN_COLUMNS = [
    "day",
    "weekday",
    "second",
    "volume",
    "open_log",
    "high_log",
    "low_log",
    "close_log",
    "close_log-1",
    "close_log-2",
    "close_log-5",
    "close_log-10",
    "close_log-15",
    "close_log-30",
    "close_log-60",
    "close_log-120",
    "close_log-240",
    "close_log-480",
    "close_log-720",
    "close_log-1440",
    "close_log-2880",
    "close_log-10080",
]


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


def dataset(request, version):
    """dataset"""
    # TODO: Load from DB
    csv = pd.read_csv("bitbank/static/bitbank/datasets/test3.csv")
    _b = BitcoinDataset(version)
    _b.set_dataset(csv)
    _b.plot()
    return redirect("/static/bitbank/graphs/" + version + ".png")


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
    try:
        value = pub.get_candlestick("btc_jpy", "1min", date_str)
    except Exception:  # pylint: disable=broad-except
        return []
    else:
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


class BitcoinDataset:
    """
    BitcoinDataset
    """

    MINUTES_OF_HOURS = 60 * 1  # TODO: 最適な時間を要調査

    def __init__(self, version):
        self.version = version
        self.data = None

    def set_dataset(self, csv):
        """
        データセットを作成
        Params:
            csv (dataframe): originalデータ
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.data = csv
        self.convert_hlc_to_log()
        self.add_column_next_extreme()
        self.add_columns_close_log()
        self.add_columns_time()
        self.remove_missing_rows()
        self.data.to_csv(
            "bitbank/static/bitbank/datasets/" + str(self.version) + ".csv",
            index=False,
        )
        logger.info("end: {:s}".format(inspect.currentframe().f_code.co_name))

    def add_columns_time(self):
        """
        現在日時に関する列を追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "second" in self.data.columns:
            return

        timestamp = pd.Series(
            [dt.datetime.fromtimestamp(i) for i in self.data["unixtime"]]
        )
        self.data["day"] = timestamp.dt.day
        self.data["weekday"] = timestamp.dt.dayofweek
        self.data["second"] = (timestamp.dt.hour * 60 + timestamp.dt.minute) * 60
        self.data.to_csv(
            "bitbank/static/bitbank/datasets/" + str(self.version) + ".csv",
            index=False,
        )

    def remove_missing_rows(self):
        """
        欠損値を除外する
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.data.dropna(inplace=True)

    def add_columns_close_log(self):
        """
        指定した時間前のclose_logの差を追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        minute_list = [1, 2, 5, 10, 15, 30, 60, 120, 240, 480, 720, 1440, 2880, 10080]
        for i in minute_list:
            name = "close_log-" + str(i)
            if name in self.data.columns:
                continue

            self.data[name] = self.data["close_log"].diff(periods=i)
            self.data.to_csv(
                "bitbank/static/bitbank/datasets/" + str(self.version) + ".csv",
                index=False,
            )

    def convert_hlc_to_log(self):
        """
        価格データを対数変換して追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        columns = ["open", "high", "low", "close"]
        for column in columns:
            name = column + "_log"
            if name in self.data.columns:
                continue

            self.data[name] = np.log(self.data[column])
            self.data.to_csv(
                "bitbank/static/bitbank/datasets/" + str(self.version) + ".csv",
                index=False,
            )

    def add_column_next_extreme(self):
        """
        期間n分の極大値・極小値
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        column_name = "next_extreme_log"
        if column_name in self.data.columns:
            return

        _y = self.data["close_log"].values
        max_ids = signal.argrelmax(_y, order=1)
        min_ids = signal.argrelmin(_y, order=1)
        max_min_ids = np.concatenate([max_ids[0], min_ids[0]])
        max_min_ids = np.sort(max_min_ids)
        next_idx = 0
        for i, row in self.data.iterrows():
            if i % 10000 == 0:
                logger.info("  index: {:.2%}".format(i / len(self.data)))

            if next_idx >= len(max_min_ids):
                break

            _ni = max_min_ids[next_idx]
            if i >= _ni:
                next_idx += 1
            # TODO: Change open_log to close_log
            self.data.at[i, column_name] = (
                self.data.at[_ni, "close_log"] - row["open_log"]
            )

        self.data.to_csv(
            "bitbank/static/bitbank/datasets/" + str(self.version) + ".csv",
            index=False,
        )

    def plot(self):
        """plot"""

        _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
        plot_close(self.data, ax1)
        plot_label(self.data, ax1)

        data2 = self.data[-500:]
        plot_close(data2, ax2)
        plot_label(data2, ax2)

        plt.savefig("bitbank/static/bitbank/graphs/" + str(self.version) + ".png")


def plot_predict(data, model, _ax):
    """
    :param data:
    :param model:
    :param _ax:
    :return:
    """

    data.reset_index(drop=True, inplace=True)
    _p = list(model.predict(data[TRAIN_COLUMNS]))
    pred = pd.DataFrame(_p)
    pred.columns = ["pred"]
    y_predict = np.exp(data["close_log"] + pred["pred"])

    _ax.plot(list(range(len(data))), y_predict, color="red", label="predict")
    _ax.legend()


def plot_label(data, _ax):
    """
    :param data:
    :param _ax:
    :return:
    """

    data.reset_index(drop=True, inplace=True)
    y_label = np.exp(data["close_log"] + data["next_extreme_log"])

    _ax.plot(list(range(len(data))), y_label, color="orange", label="label")
    _ax.legend()


def plot_close(data, _ax):
    """
    :param data:
    :param _ax:
    :return:
    """

    data.reset_index(drop=True, inplace=True)
    y_close = data["close"]

    _ax.plot(list(range(len(data))), y_close, color="blue", label="close")
    _ax.legend()
