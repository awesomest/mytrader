"""bitcoin.py"""
import inspect
from logging import getLogger, basicConfig, DEBUG
from datetime import datetime as dt
from bitbank.models import Candlestick
import pandas as pd  # pylint: disable=import-error
import numpy as np  # pylint: disable=import-error
from sklearn.linear_model import LinearRegression  # pylint: disable=import-error
from sklearn.model_selection import train_test_split  # pylint: disable=import-error
import matplotlib  # pylint: disable=import-error

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # pylint: disable=import-error,wrong-import-position
from . import graph  # pylint: disable=wrong-import-position

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


def build_input_for_model(candlestick):
    """
    Params:
        candlestick: (np.array): time of the target row
            includes: ["unixtime", "open", "high", "low", "close", "volume"]
    Return:
        row: (dataframe): input for model
    """

    data = pd.DataFrame([[]])

    timestamp = dt.fromtimestamp(candlestick[0])
    data["day"] = timestamp.day
    data["weekday"] = timestamp.weekday()
    data["second"] = (timestamp.hour * 60 + timestamp.minute) * 60

    data["open_log"] = np.log(candlestick[1])
    data["high_log"] = np.log(candlestick[2])
    data["low_log"] = np.log(candlestick[3])
    data["close_log"] = np.log(candlestick[4])
    data["volume"] = candlestick[5]

    minutes_diffs = [
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

    for i in minutes_diffs:
        seconds_diff = i * 60
        close = Candlestick.objects.get(
            unixtime__lte=int(candlestick[0] - seconds_diff)
        ).close
        data["close_log-" + str(i)] = data["close_log"] - np.log(close)

    return data


def predict(data, model):
    """
    Params:
        data: (dataframe): input data as 1 row
        model (model): model for predict
    Return:
        predicted_value: (float): next extreme value as log
    """
    return model.predict(data[TRAIN_COLUMNS])


def create_model(data_train, label_train):
    """
    Params:
        data_train (dataframe): training data
        label_train (dataframe): label data
    Returns:
        model: trained model
    """
    model = LinearRegression()
    model.fit(data_train, label_train)
    return model


def calc_avg_score(data, times=100):
    """
    Params:
        data (dataframe): all dataset to be scored
        times (int): how many executions
    Returns:
        float: average score of model
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    sum_score = 0
    for i in range(times):
        (data_train, data_test, label_train, label_test,) = set_train_test_dataset(
            data, 0.2
        )
        model = create_model(data_train, label_train)
        score = model.score(data_test, label_test)
        logger.info("score[{:3d}]: {:.5f}".format(i, score))
        sum_score += score

    logger.info("score[avg]: {:.5f}".format(score))

    return sum_score / times


def set_train_test_dataset(data, test_ratio):
    """
    Params:
        data (dataframe): data to be split
        test_ratio (float): test ratio
    Returns:
        dataframe: data_train
        dataframe: data_test
        dataframe: label_train
        dataframe: label_test
    """

    _x = data[TRAIN_COLUMNS]
    _y = data["next_extreme_log"]
    return train_test_split(_x, _y, test_size=test_ratio)


def plot(data, model, file_name):
    """
    :param data:
    :param model:
    :param file_name:
    :return:
    """

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    graph.plot_close(data, ax1)
    graph.plot_predict(data, model, ax1)

    data2 = data[-500:]
    graph.plot_close(data2, ax2)
    graph.plot_predict(data2, model, ax2)

    plt.savefig("bitbank/static/bitbank/graphs/" + file_name + "_predict.png")
