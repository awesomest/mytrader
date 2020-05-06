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
        self.data = csv.sort_values(["unixtime"])
        self.init_columns()
        self.convert_hlc_to_ratio()
        self.add_trend()
        self.add_result()
        self.add_column_latest_close()
        self.remove_missing_rows()

    def init_columns(self):
        self.data["timestamp"] = [dt.fromtimestamp(l) for l in self.data["unixtime"]]

    def remove_missing_rows(self):
        # TODO: check also zero
        self.data.dropna(inplace=True)

    def add_trend(self):
        for index, _ in self.data.iterrows():
            first_index = index - MINUTES_OF_HOURS
            if first_index < 0:
                continue

            data_in_hours = self.data[first_index:index]

            _x = list(range(len(data_in_hours["unixtime"])))
            trend_line = linregress(x=_x, y=data_in_hours["close"])
            self.data.at[index, "trend"] = trend_line[0] / data_in_hours["close"].iat[0]

    # 目的変数を設定
    def add_result(self):
        self.data["result"] = self.data["trend"].shift(-1 * MINUTES_OF_HOURS)

    def add_column_latest_close(self):
        minute_list = [1, 2, 5, 10, 15, 30, 60, 120, 240, 480, 720, 1440, 2880, 10080]
        for i in minute_list:
            name = "close_ratio" + str(i)
            self.data[name] = self.data["close_ratio"].shift(i)

    def convert_hlc_to_ratio(self):
        columns = ["high", "low", "close"]
        for column in columns:
            self.data[column + "_ratio"] = self.data[column] / self.data["open"]
