from sklearn.linear_model import LinearRegression  # pylint: disable=import-error
from sklearn.model_selection import train_test_split  # pylint: disable=import-error

TRAIN_COLUMNS = [
    "day",
    "weekday",
    "second",
    "volume",
    "high_ratio",
    "low_ratio",
    "close_ratio",
    "trend",
    "close_ratio1",
    "close_ratio2",
    "close_ratio5",
    "close_ratio10",
    "close_ratio15",
    "close_ratio30",
    "close_ratio60",
    "close_ratio120",
    "close_ratio240",
    "close_ratio480",
    "close_ratio720",
    "close_ratio1440",
    "close_ratio2880",
    "close_ratio10080",
]


def create_model(data_train, label_train):
    model = LinearRegression()
    model.fit(data_train, label_train)
    return model


def calc_avg_score(data):
    sum_score = 0
    times = 100
    for i in range(times):
        (data_train, data_test, label_train, label_test,) = set_train_test_dataset(
            data, 0.2
        )
        model = create_model(data_train, label_train)
        score = model.score(data_test, label_test)
        print(f"score[{i:03}]: {score}")
        sum_score += score

    return sum_score / times


def set_train_test_dataset(data, test_ratio):
    _x = data[TRAIN_COLUMNS]
    _y = data["result"]
    return train_test_split(_x, _y, test_size=test_ratio)
