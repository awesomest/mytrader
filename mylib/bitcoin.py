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


class BitcoinRegression:
    def __init__(self, csv):
        self.data = csv
        self.data_train = None
        self.data_test = None
        self.label_train = None
        self.label_test = None

    def create_model(self):
        model = LinearRegression()
        model.fit(self.data_train, self.label_train)
        return model

    def calc_avg_score(self):
        sum_score = 0
        times = 100
        for i in range(times):
            self.set_train_test_dataset(0.2)
            model = self.create_model()
            score = model.score(self.data_test, self.label_test)
            print(f"score[{i:03}]: {score}")
            sum_score += score

        return sum_score / times

    def set_train_test_dataset(self, test_ratio):
        _x = self.data[TRAIN_COLUMNS]
        _y = self.data["result"]
        (
            self.data_train,
            self.data_test,
            self.label_train,
            self.label_test,
        ) = train_test_split(_x, _y, test_size=test_ratio)
