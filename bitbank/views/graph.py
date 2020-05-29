"""graph.py"""
import pandas as pd  # pylint: disable=import-error
import numpy as np  # pylint: disable=import-error
from . import bitcoin


def plot_predict(data, model, _ax):
    """
    :param data:
    :param model:
    :param _ax:
    :return:
    """

    data.reset_index(drop=True, inplace=True)
    _p = list(model.predict(data[bitcoin.TRAIN_COLUMNS]))
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
