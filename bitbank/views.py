"""views.py"""
import inspect
import datetime as dt
from logging import getLogger, basicConfig, DEBUG
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import python_bitbankcc  # pylint: disable=import-error
from bitbank.models import Candlestick
import pandas as pd  # pylint: disable=import-error
import numpy as np  # pylint: disable=import-error
from scipy.stats import linregress  # pylint: disable=import-error
from scipy import signal  # pylint: disable=import-error

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
        # self.add_column_trend()  # TODO: 不要になったら削除
        # self.add_column_extreme_60_later()  # TODO: 不要になったら削除
        # self.add_column_trend_60_later()  # TODO: 不要になったら削除
        self.add_column_next_extreme()
        # self.add_columns_close_log()
        # self.add_columns_time()
        # self.remove_missing_rows()
        # self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)
        logger.info("end: {:s}".format(inspect.currentframe().f_code.co_name))

    def add_column_extreme_60_later(self):
        """
        現在から60分後までの最大値or最小値を追加
        TODO: dataframe.rolling を使用する
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "extreme60" in self.data.columns:
            return

        for index, row in self.data.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(self.data)))
            last_index = index + self.MINUTES_OF_HOURS
            if last_index > len(self.data):
                continue

            # TODO: closeの最大・最小でも要確認
            data_in_hours = self.data[["high", "low"]][index:last_index]
            highest_index = data_in_hours["high"].idxmax()
            highest = data_in_hours["high"][highest_index]
            lowest_index = data_in_hours["low"].idxmin()
            lowest = data_in_hours["low"][lowest_index]

            if highest_index < lowest_index:
                extreme60 = highest / row["open"]
            else:
                extreme60 = lowest / row["open"]

            self.data.at[index, "extreme60"] = extreme60

        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def add_columns_time(self):
        """
        現在日時に関する列を追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "second" in self.data.columns:
            return

        # timestamp = pd.Series([dt.fromtimestamp(i) for i in self.data["unixtime"]])
        # self.data["day"] = timestamp.dt.day
        # self.data["weekday"] = timestamp.dt.dayofweek
        # self.data["second"] = (timestamp.dt.hour * 60 + timestamp.dt.minute) * 60
        # # self.data.drop(columns=["unixtime"], inplace=True)
        # self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def remove_missing_rows(self):
        """
        欠損値を除外する
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.data.dropna(inplace=True)

    def add_column_trend(self):
        """
        60分前から現在までのトレンドを追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "trend" in self.data.columns:
            return

        for index, _ in self.data.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(self.data)))
            first_index = index - self.MINUTES_OF_HOURS
            if first_index < 0:
                continue

            data_in_hours = self.data[["close"]][first_index:index]

            _x = list(range(len(data_in_hours)))
            trend_line = linregress(x=_x, y=data_in_hours["close"])
            self.data.at[index, "trend"] = trend_line[0] / data_in_hours["close"].iat[0]

        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def add_column_trend_60_later(self):
        """
        現在から60分後までのトレンドを追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "trend60" in self.data.columns:
            return

        self.data["trend60"] = self.data["trend"].shift(-1 * self.MINUTES_OF_HOURS)
        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

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
            self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

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
        for index, row in self.data.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(self.data)))

            if next_idx >= len(max_min_ids):
                break

            _ni = max_min_ids[next_idx]
            if index >= _ni:
                next_idx += 1
            # TODO: Change open_log to close_log
            self.data.at[index, column_name] = (
                self.data.at[_ni, "close_log"] - row["open_log"]
            )

        self.data.to_csv(
            "bitbank/static/bitbank/datasets/" + str(self.version) + ".csv",
            index=False,
        )
