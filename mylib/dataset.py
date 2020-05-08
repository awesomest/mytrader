from datetime import datetime as dt
import pandas as pd  # pylint: disable=import-error
from scipy.stats import linregress  # pylint: disable=import-error

MINUTES_OF_HOURS = 60 * 1  # TODO: 最適な時間を要調査


class BitcoinDataset:
    def __init__(self):
        self.data = None

    def set_dataset(self, csv):
        self.data = csv.sort_values(["unixtime"])
        self.add_time_columns()
        self.convert_hlc_to_ratio()
        self.add_trend()
        # self.add_result()
        self.add_extreme_column()
        self.add_column_latest_close()
        self.remove_missing_rows()

    def set_dataset_for_test(self, csv):
        self.data = csv
        self.rename_result_column()
        self.add_extreme_column()

    def add_extreme_column(self):
        for index, row in self.data.iterrows():
            last_index = index + MINUTES_OF_HOURS
            if last_index > len(self.data):
                continue

            data_in_hours = self.data[["high", "low"]][index:last_index]
            highest = data_in_hours["high"].max()
            lowest = data_in_hours["low"].min()
            diff_highest = highest - row["open"]
            diff_lowest = row["open"] - lowest

            if diff_highest > diff_lowest:
                extreme60 = highest / row["open"]
            else:
                extreme60 = lowest / row["open"]

            self.data.at[index, "extreme60"] = extreme60

    def rename_result_column(self):
        self.data = self.data.rename(columns={"result": "trend60"})

    def add_time_columns(self):
        timestamp = pd.Series([dt.fromtimestamp(i) for i in self.data["unixtime"]])
        self.data["day"] = timestamp.dt.day
        self.data["weekday"] = timestamp.dt.dayofweek
        self.data["second"] = (timestamp.dt.hour * 60 + timestamp.dt.minute) * 60
        self.data.drop(columns=["unixtime"], inplace=True)

    def remove_missing_rows(self):
        self.data.dropna(inplace=True)

    def add_trend(self):
        for index, _ in self.data.iterrows():
            first_index = index - MINUTES_OF_HOURS
            if first_index < 0:
                continue

            data_in_hours = self.data[["close"]][first_index:index]

            _x = list(range(len(data_in_hours)))
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
