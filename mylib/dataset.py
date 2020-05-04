from datetime import datetime as dt
from scipy.stats import linregress  # pylint: disable=import-error

MINUTES_OF_HOURS = 60 * 1  # TODO: 最適な時間を要調査


def calc_gradient(_x1, _y1, _x2, _y2):
    if _x2 == _x1:
        return float("inf")
    return (_y2 - _y1) / (_x2 - _x1)


class BitcoinDataset:
    def __init__(self):
        self.data = None

    def set_dataset(self, csv):
        csv = csv.reset_index()
        csv = csv[["unixtime", "open", "close", "low", "high", "volume"]]
        self.data = csv.sort_values(["unixtime"])
        self.format()
        self.add_result()
        self.add_column_diff_all(3)
        self.remove_missing_rows()

    def format(self):
        self.data["timestamp"] = [dt.fromtimestamp(l) for l in self.data["unixtime"]]
        self.data["result"] = 0.0

    def remove_missing_rows(self):
        last = max(0, len(self.data) - MINUTES_OF_HOURS)
        self.data = self.data.loc[2:last]  # remove rows includes NaN or result=0

    # 目的変数を設定
    def add_result(self):
        for index, _ in self.data.iterrows():
            if index + MINUTES_OF_HOURS >= len(self.data):
                break

            last_index = index + MINUTES_OF_HOURS
            data_in_hours = self.data[index:last_index]

            _x = list(range(len(data_in_hours["unixtime"])))
            trend_line = linregress(x=_x, y=data_in_hours["close"])
            self.data.at[index, "result"] = trend_line[0]

    def add_column_diff_all(self, _n):
        for i in list(range(1, _n)):
            self.set_column_diff_i(i)

    def set_column_diff_i(self, i):
        name = "diff" + str(i)
        self.data[name] = self.data["open"].shift(i)
