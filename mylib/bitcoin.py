"""
bitcoin.py
"""
import inspect
from logging import getLogger, basicConfig, DEBUG
from sklearn.linear_model import LinearRegression  # pylint: disable=import-error
from sklearn.model_selection import train_test_split  # pylint: disable=import-error

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)

TRAIN_COLUMNS = [
    "day",
    "weekday",
    "second",
    "volume",
    "high_ratio",
    "low_ratio",
    "close_ratio",
    "trend",
    "close_ratio-1",
    "close_ratio-2",
    "close_ratio-5",
    "close_ratio-10",
    "close_ratio-15",
    "close_ratio-30",
    "close_ratio-60",
    "close_ratio-120",
    "close_ratio-240",
    "close_ratio-480",
    "close_ratio-720",
    "close_ratio-1440",
    "close_ratio-2880",
    "close_ratio-10080",
]


def create_model(data_train, label_train):
    """
    Params:
        data_train (dataframe): training data
        label_train (dataframe): label data
    Returns:
        model: trained model
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    model = LinearRegression()
    model.fit(data_train, label_train)
    return model


def calc_avg_score(data):
    """
    Params:
        data (dataframe): all dataset to be scored
    Returns:
        float: average score of model
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    sum_score = 0
    times = 100
    for i in range(times):
        (data_train, data_test, label_train, label_test,) = set_train_test_dataset(
            data, 0.2
        )
        model = create_model(data_train, label_train)
        score = model.score(data_test, label_test)
        logger.info("score[{:3d}]: {:f}".format(i, score))
        sum_score += score

    logger.info("score[avg]: {:f}".format(score))

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

    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    _x = data[TRAIN_COLUMNS]
    _y = data["extreme60"]
    return train_test_split(_x, _y, test_size=test_ratio)
