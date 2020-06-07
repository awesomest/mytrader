"""bitcoin.py"""
import inspect
import pickle
from logging import getLogger, basicConfig, DEBUG
from sklearn.linear_model import LinearRegression  # pylint: disable=import-error
from sklearn.model_selection import train_test_split  # pylint: disable=import-error
from bitbank.models import Prediction
import numpy as np  # pylint: disable=import-error
import matplotlib  # pylint: disable=import-error

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # pylint: disable=import-error,wrong-import-position
from . import graph  # pylint: disable=wrong-import-position,relative-beyond-top-level
from . import dataset  # pylint: disable=wrong-import-position,relative-beyond-top-level

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


def predict_realtime():
    """
    Returns:
        float: btc price
    """
    data = dataset.create_realtime_input_dataset()
    pickle_file = "bitbank/static/bitbank/models/production.pickle"
    with open(pickle_file, mode="rb") as file:
        model = pickle.load(file)
    predict_log = model.predict(data[TRAIN_COLUMNS])[0]
    predict_price = np.exp(predict_log)
    Prediction(unixtime=data.iloc[-1]["unixtime"], price=predict_price).save()
    return predict_price


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
