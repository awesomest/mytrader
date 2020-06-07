"""dataset.py"""
import inspect
import datetime as dt
from logging import getLogger, basicConfig, DEBUG
from scipy import signal  # pylint: disable=import-error
from bitbank.models import Candlestick
import python_bitbankcc  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error
import numpy as np  # pylint: disable=import-error
import matplotlib  # pylint: disable=import-error

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # pylint: disable=import-error,wrong-import-position
from . import graph  # pylint: disable=wrong-import-position,relative-beyond-top-level

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


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


def convert_hlc_to_log(data: pd.DataFrame, file_name=None):
    """
    価格データを対数変換して追加
    Params:
        data (dataframe):
        file_name:
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    columns = ["open", "high", "low", "close"]
    new_data = data.copy()
    for column in columns:
        name = column + "_log"
        if name in new_data.columns:
            continue

        new_data[name] = np.log(new_data[column])
        if file_name is not None:
            new_data.to_csv(
                "bitbank/static/bitbank/datasets/" + file_name + ".csv", index=False,
            )

    return new_data


def add_column_next_extreme(data: pd.DataFrame, file_name=None):
    """
    期間n分の極大値・極小値
    Params:
        data (dataframe):
        file_name:
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    column_name = "next_extreme_log"
    if column_name in data.columns:
        return data

    new_data = data.copy()
    _y = new_data["close_log"].values
    max_ids = signal.argrelmax(_y, order=1)
    min_ids = signal.argrelmin(_y, order=1)
    max_min_ids = np.concatenate([max_ids[0], min_ids[0]])
    max_min_ids = np.sort(max_min_ids)
    next_idx = 0
    for i, row in new_data.iterrows():
        if i % 10000 == 0:
            logger.info("  index: {:.2%}".format(i / len(new_data)))

        if next_idx >= len(max_min_ids):
            break

        _ni = max_min_ids[next_idx]
        if i >= _ni:
            next_idx += 1
        # TODO: Change open_log to close_log
        new_data.at[i, column_name] = new_data.at[_ni, "close_log"] - row["open_log"]

    if file_name is not None:
        new_data.to_csv(
            "bitbank/static/bitbank/datasets/" + file_name + ".csv", index=False,
        )

    return new_data


def add_columns_close_log(data: pd.DataFrame, file_name=None):
    """
    指定した時間前のclose_logの差を追加
    Params:
        data (dataframe):
        file_name:
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    minute_list = [
        1,
        2,
        5,
        10,
        15,
        30,
        60,
        120,
        240,
        480,
        720,
        1440,
        2880,
        10080,
    ]
    new_data = data.copy()
    for i in minute_list:
        name = "close_log-" + str(i)
        if name in new_data.columns:
            continue

        new_data[name] = new_data["close_log"].diff(periods=i)
        if file_name is not None:
            new_data.to_csv(
                "bitbank/static/bitbank/datasets/" + file_name + ".csv", index=False,
            )

    return new_data


def add_columns_time(data: pd.DataFrame, file_name=None):
    """
    現在日時に関する列を追加
    Params:
        data (dataframe):
        file_name:
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    if "second" in data.columns:
        return data

    new_data = data.copy()
    timestamp = pd.Series([dt.datetime.fromtimestamp(i) for i in new_data["unixtime"]])
    new_data["day"] = timestamp.dt.day
    new_data["weekday"] = timestamp.dt.dayofweek
    new_data["second"] = (timestamp.dt.hour * 60 + timestamp.dt.minute) * 60
    if file_name is not None:
        new_data.to_csv(
            "bitbank/static/bitbank/datasets/" + file_name + ".csv", index=False,
        )

    return new_data


def remove_missing_rows(data: pd.DataFrame, file_name=None):
    """
    欠損値を除外する
    Params:
        data (dataframe):
        file_name:
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    new_data = data.copy()
    new_data.dropna(inplace=True)
    if file_name is not None:
        new_data.to_csv(
            "bitbank/static/bitbank/datasets/" + file_name + ".csv", index=False,
        )
    return new_data


def create_realtime_input_dataset():
    """
    リアルタイムの予測用データセットを作成
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    candlestick_list = []
    week_ago = dt.date.today() + dt.timedelta(-8)
    tomorrow = dt.date.today() + dt.timedelta(1)
    date_range = get_date_range(week_ago, tomorrow)
    for date in date_range:
        date_str = date.strftime("%Y%m%d")
        candlestick_list.extend(fetch_candlestick_from_bitbank(date_str))

    input_dataset = pd.DataFrame(
        candlestick_list,
        columns=["open", "high", "low", "close", "volume", "unixtime"],
    ).astype(float)
    input_dataset["unixtime"] = input_dataset["unixtime"] / 1000
    input_dataset = convert_hlc_to_log(input_dataset)
    input_dataset = add_columns_close_log(input_dataset)
    input_dataset = add_columns_time(input_dataset)
    input_dataset = remove_missing_rows(input_dataset, "test01")
    logger.info("end: {:s}".format(inspect.currentframe().f_code.co_name))
    return input_dataset.tail(1)


def create_training_dataset(data: pd.DataFrame, file_name: str):
    """
    学習用データセットを作成
    Params:
        data (dataframe): originalデータ
        file_name:
    Returns:
        dataframe
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    new_data = data.copy()
    new_data = convert_hlc_to_log(new_data, file_name)
    new_data = add_column_next_extreme(new_data, file_name)
    new_data = add_columns_close_log(new_data, file_name)
    new_data = add_columns_time(new_data, file_name)
    new_data = remove_missing_rows(new_data, file_name)
    logger.info("end: {:s}".format(inspect.currentframe().f_code.co_name))
    return new_data


def plot(data: pd.DataFrame, file_name: str):
    """
    Params:
        data (dataframe):
        file_name:
    Returns:
        dataframe
    """

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    graph.plot_close(data, ax1)
    graph.plot_label(data, ax1)

    data2 = data[-500:]
    graph.plot_close(data2, ax2)
    graph.plot_label(data2, ax2)

    plt.savefig("bitbank/static/bitbank/graphs/" + file_name + "_dataset.png")
